import cProfile
import ipaddress
import logging
import os
import time
import tracemalloc
import zoneinfo
from logging import getLogger
from logging.handlers import RotatingFileHandler

import pytz
from django.db import connection
from django.http import HttpResponseForbidden
from django.test.utils import CaptureQueriesContext
from django.utils import timezone, translation
from django.utils.deprecation import MiddlewareMixin

from .utils import get_language_code

logger = getLogger(__file__)


BLOCKED_IPS = [x.strip() for x in os.getenv("BLOCKED_IPS", "").split(",") if x.strip()]
BLOCKED_NETWORKS = [
    x.strip() for x in os.getenv("BLOCKED_NETWORKS", "").split(",") if x.strip()
]


class TimeZoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tz_header = request.headers.get("TZ")

        if tz_header:
            try:
                timezone.activate(tz_header)
            except (pytz.UnknownTimeZoneError, zoneinfo.ZoneInfoNotFoundError):
                logger.error("Invalid timezone %s", tz_header)
                pass  # Handle unknown timezone error here
        else:
            # Set default timezone if TZ header is not provided
            timezone.activate("UTC")

        response = self.get_response(request)
        timezone.deactivate()
        return response


class LanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Extract language from _lang query parameter
        lang = request.GET.get("_lang")
        if lang:
            lang = get_language_code(lang).upper()
        if lang:
            # Activate the new language if it's valid
            translation.activate(lang)
        else:
            # Fallback to default language if not valid
            translation.activate("EN")

        response = self.get_response(request)
        # Restore the original language
        translation.activate("EN")
        return response


class RequestTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Record the start time
        start_time = time.time()

        # Process the request
        response = self.get_response(request)

        # Calculate the time taken
        duration = time.time() - start_time
        logger.info(f"Request to {request.path} took {duration:.4f} seconds")

        response["X-Request-Duration"] = f"{duration:.4f} seconds"
        return response


class MemoryUsageMiddleware(MiddlewareMixin):
    def process_request(self, request):
        tracemalloc.start()  # Start tracking memory

    def process_response(self, request, response):
        _, peak_memory = tracemalloc.get_traced_memory()
        peak_memory_mb = peak_memory / 1024 / 1024  # Convert to MB
        tracemalloc.stop()  # Stop tracking

        logger.info(
            f"[{request.method}] {request.path} - Peak Memory Used: {peak_memory_mb:.2f} MB"
        )
        return response


class ResponseTimeLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger("metric_logger")
        if not self.logger.handlers:
            handler = RotatingFileHandler(
                "metric.log", maxBytes=5 * 1024 * 1024, backupCount=3
            )
            formatter = logging.Formatter(
                "%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def __call__(self, request):
        start = time.time()
        response = self.get_response(request)
        duration_ms = int((time.time() - start) * 1000)
        path = request.path
        method = request.method
        self.logger.info(
            f"Method: {method} | Path: {path} | Response Time: {duration_ms} ms"
        )
        return response


class QueryLoggingMiddleware:
    """
    Django middleware for logging all SQL queries executed during the processing of each HTTP request.

    This middleware captures all database queries made during the lifecycle of a request,
    logs the total number of queries, their execution time, and details about each query
    (including the SQL statement and its duration) to a rotating log file ("query.log").
    The log entry also includes the HTTP method, request path, user (if authenticated), and
    the total duration of the request.

    Attributes:
        get_response (callable): The next middleware or view in the Django request/response cycle.
        logger (logging.Logger): Logger instance for writing query logs to file.

        Initialize the QueryLoggingMiddleware.

        Sets up the logger with a rotating file handler if it hasn't been set up already.

        Args:
            get_response (callable): The next middleware or view in the Django request/response cycle.

        # ...


        Process the incoming HTTP request, capture and log all SQL queries executed.

        Args:
            request (HttpRequest): The incoming HTTP request object.

        Returns:
            HttpResponse: The response generated by the next middleware or view.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger("query_logger")
        if not self.logger.handlers:
            handler = RotatingFileHandler(
                "query.log", maxBytes=5 * 1024 * 1024, backupCount=3
            )
            formatter = logging.Formatter(
                "%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def __call__(self, request):
        start_time = time.time()
        with CaptureQueriesContext(connection) as queries:
            response = self.get_response(request)
        duration = time.time() - start_time
        path = request.path
        method = request.method
        user = getattr(request, "user", None)
        user_repr = str(user) if user and user.is_authenticated else "Anonymous"
        total_queries = len(queries.captured_queries)
        if queries.captured_queries:
            log_lines = [
                f"Method: {method} | Path: {path} | User: {user_repr} | "
                f"Total Queries: {total_queries} | Total Duration: {duration:.4f} sec | Queries:"
            ]
            for q in queries.captured_queries:
                sql = q.get("sql")
                q_duration = q.get("time")
                log_lines.append(f"    Query: {sql} | Duration: {q_duration} sec")
            log_message = "\n".join(log_lines)
            self.logger.info(log_message)
        return response


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "").strip()
    if x_forwarded_for and x_forwarded_for.split(","):
        ip = x_forwarded_for.split(",")[0].strip()  # Take the first IP in the list
    else:
        ip = request.META.get("REMOTE_ADDR", "").strip()
    return ip


class BlockBlackListedIPMiddleware:
    """
    Django middleware for blocking requests from blacklisted IP addresses and network ranges.

    This middleware checks the client's IP address against a list of blocked individual IPs
    and network ranges. If the client's IP matches any blocked IP or falls within a blocked
    network range, the request is denied with an HTTP 403 Forbidden response.

    The blocked IPs and networks are configured in Django settings as BLOCKED_IPS and
    BLOCKED_NETWORKS respectively.

    Attributes:
        get_response (callable): The next middleware or view in the Django request/response cycle.

    Args:
        get_response (callable): The next middleware or view in the Django request/response cycle.

    Returns:
        HttpResponse: Either an HTTP 403 Forbidden response for blocked IPs, or the response
                     from the next middleware/view in the chain.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = get_client_ip(request)
        if ip:
            client_ip = ipaddress.ip_address(ip)

            # Check individual IPs
            if BLOCKED_IPS and ip in BLOCKED_IPS:
                logger.info(
                    f"[BlockBlackListedIPMiddleware] Blocked request from IP: {ip} - IP found in blocked list"
                )
                return HttpResponseForbidden("Access Denied: Your IP is blocked.")

            # Check IP ranges
            if BLOCKED_NETWORKS:
                for network_str in BLOCKED_NETWORKS:
                    network = ipaddress.ip_network(network_str)
                    if client_ip in network:
                        logger.info(
                            f"[BlockBlackListedIPMiddleware] Blocked request from IP: {ip} - IP "
                            f"falls within blocked network range: {network_str}"
                        )
                        return HttpResponseForbidden(
                            "Access Denied: Your IP range is blocked."
                        )

        response = self.get_response(request)
        return response


class FunctionDurationTrackingMiddleware:
    """
    Django middleware for profiling application code execution during request processing.

    This middleware uses cProfile to capture detailed profiling information similar to the
    profile_and_timeit decorator but at the middleware level for all requests. It focuses on
    application code and provides meaningful profiling data like a traditional profiler.

    The middleware tracks:
    - Application function calls with cumulative and per-call times
    - Function call counts and time percentages
    - Detailed profiling statistics
    - Request context (method, path, user)

    Logs are written to "function_durations.log" with rotation for file size management.
    """

    def __init__(self, get_response):

        self.get_response = get_response
        self.logger = logging.getLogger("function_duration_logger")
        if not self.logger.handlers:
            handler = RotatingFileHandler(
                "function_durations.log", maxBytes=10 * 1024 * 1024, backupCount=5
            )
            formatter = logging.Formatter(
                "%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def __call__(self, request):

        # Start profiling
        pr = cProfile.Profile()
        pr.enable()

        start_time = time.perf_counter()
        response = self.get_response(request)
        end_time = time.perf_counter()

        pr.disable()

        # Generate profiling report
        self._log_profiling_results(request, pr, end_time - start_time)

        return response

    def _log_profiling_results(self, request, profiler, total_time):
        """Generate and log profiling results showing ALL function calls with durations."""
        import io
        import pstats

        method = request.method
        path = request.path
        user = getattr(request, "user", None)
        user_repr = str(user) if user and user.is_authenticated else "Anonymous"

        # Create stats object
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s)

        # Sort by cumulative time
        ps.sort_stats("cumulative")

        # Get stats data for custom formatting
        stats = ps.stats
        total_calls = ps.total_calls

        # Prepare log message header
        log_lines = [
            "COMPREHENSIVE PROFILING REPORT",
            f"Method: {method} | Path: {path} | User: {user_repr}",
            f"Total Time: {total_time:.6f}s | Total Function Calls: {total_calls}",
            "",
            f"{'ncalls':<10} {'tottime':<10} {'percall':<10} {'cumtime':<10} "
            f"{'percall':<10} {'filename:lineno(function)'}",
            f"{'-'*120}",
        ]

        # Sort all functions by cumulative time (most expensive first)
        sorted_stats = sorted(
            [(key, value) for key, value in stats.items()],
            key=lambda x: x[1][3],  # Sort by cumtime
            reverse=True,
        )

        # No categorization needed - just prepare for top 30 display

        # Helper function to format function info
        def format_function_line(filename, lineno, funcname, cc, nc, tt, ct):
            percall_tt = tt / cc if cc > 0 else 0
            percall_ct = ct / cc if cc > 0 else 0

            # Create a more readable function location
            if "site-packages" in filename:
                # For third-party packages, show package/module
                parts = filename.split("site-packages/")
                if len(parts) > 1:
                    package_path = parts[1]
                    if "django/" in package_path:
                        short_path = "django/" + package_path.split("django/")[-1]
                    else:
                        short_path = "/".join(
                            package_path.split("/")[:2]
                        )  # Show package/module
                else:
                    short_path = filename.split("/")[-1]
            else:
                # For application code, show relative path
                if "/iam_service/" in filename:
                    short_path = "iam_service/" + filename.split("/iam_service/")[-1]
                elif "/config/" in filename:
                    short_path = "config/" + filename.split("/config/")[-1]
                else:
                    short_path = (
                        "/".join(filename.split("/")[-2:])
                        if "/" in filename
                        else filename
                    )

            func_location = f"{short_path}:{lineno}({funcname})"

            return f"{cc:<10} {tt:<10.6f} {percall_tt:<10.6f} {ct:<10.6f} {percall_ct:<10.6f} {func_location}"

        # Show top 30 slowest functions only
        log_lines.append("")
        log_lines.append("TOP 30 SLOWEST FUNCTIONS:")

        for i, ((filename, lineno, funcname), stat_tuple) in enumerate(
            sorted_stats[:30]
        ):
            # Handle different stat tuple formats
            if len(stat_tuple) >= 4:
                cc, nc, tt, ct = stat_tuple[:4]
            else:
                continue  # Skip malformed entries

            log_lines.append(
                f"{i+1:2d}. {format_function_line(filename, lineno, funcname, cc, nc, tt, ct)}"
            )

        # Simple performance summary
        log_lines.extend(
            [
                "",
                "PERFORMANCE SUMMARY:",
                f"  Total Request Time: {total_time:.6f}s",
                f"  Total Functions Analyzed: {len(sorted_stats)}",
                "  Showing Top 30 Slowest Functions",
                "",
            ]
        )

        # Log everything as a single message
        log_message = "\n".join(log_lines)
        self.logger.info(log_message)
