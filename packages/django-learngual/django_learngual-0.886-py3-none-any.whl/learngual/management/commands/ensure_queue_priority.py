"""
Management command to ensure RabbitMQ queues have the correct priority configuration.

This command checks if queues exist with the correct x-max-priority argument.
If a queue exists without the correct configuration, it will be deleted and
recreated automatically with the new settings.
"""
import socket
import time

from amqp import exceptions as amqp_exceptions
from django.conf import settings
from django.core.management.base import BaseCommand
from kombu import Connection


class Command(BaseCommand):
    help = "Ensure RabbitMQ queues have correct priority configuration"

    def add_arguments(self, parser):
        parser.add_argument(
            "--queue",
            type=str,
            default="iam",
            help="Queue name to check (default: iam)",
        )
        parser.add_argument(
            "--max-priority",
            type=int,
            default=10,
            help="Expected x-max-priority value (default: 10)",
        )
        parser.add_argument(
            "--max-retries",
            type=int,
            default=5,
            help="Maximum connection retry attempts (default: 5)",
        )
        parser.add_argument(
            "--retry-delay",
            type=int,
            default=2,
            help="Delay between retries in seconds (default: 2)",
        )

    def handle(self, *args, **options):
        queue_name = options["queue"]
        expected_priority = options["max_priority"]
        max_retries = options["max_retries"]
        retry_delay = options["retry_delay"]

        self.stdout.write(f"Checking queue configuration for: {queue_name}")

        broker_url = settings.CELERY_BROKER_URL

        # Wait for RabbitMQ to be ready
        for attempt in range(1, max_retries + 1):
            try:
                with Connection(broker_url) as conn:
                    conn.connect()
                    self.stdout.write(self.style.SUCCESS("✓ Connected to RabbitMQ"))
                    break
            except (socket.gaierror, ConnectionRefusedError, OSError) as e:
                if attempt < max_retries:
                    self.stdout.write(
                        f"⏳ Waiting for RabbitMQ... (attempt {attempt}/{max_retries})"
                    )
                    time.sleep(retry_delay)
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"⚠ Could not connect to RabbitMQ after {max_retries} attempts: {str(e)}"
                        )
                    )
                    self.stdout.write(
                        "RabbitMQ may not be available yet, skipping queue check"
                    )
                    return

        try:
            with Connection(broker_url) as conn:
                channel = conn.channel()

                try:
                    # Try to passively declare the queue (check if it exists)
                    (
                        queue_name_response,
                        message_count,
                        consumer_count,
                    ) = channel.queue_declare(queue=queue_name, passive=True)

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ Queue '{queue_name}' exists with {message_count} messages"
                        )
                    )

                    # Try to declare queue with durable=True and priority argument to check if it matches
                    # This must match what Celery will declare with
                    try:
                        channel.queue_declare(
                            queue=queue_name,
                            durable=True,
                            auto_delete=False,
                            arguments={"x-max-priority": expected_priority},
                            passive=False,
                        )
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"✓ Queue '{queue_name}' already has correct configuration "
                                f"(durable=True, x-max-priority={expected_priority})"
                            )
                        )
                    except amqp_exceptions.PreconditionFailed as e:
                        error_msg = str(e)

                        self.stdout.write(
                            self.style.WARNING(
                                "⚠ Queue configuration mismatch detected"
                            )
                        )
                        self.stdout.write(f"RabbitMQ error: {error_msg}")

                        # Delete and recreate if error is about x-max-priority, durable, or auto_delete
                        if (
                            "x-max-priority" in error_msg
                            or "durable" in error_msg
                            or "auto_delete" in error_msg
                        ):
                            self.stdout.write(
                                self.style.WARNING(
                                    f"⚠ Queue '{queue_name}' configuration is incorrect "
                                    f"(needs durable=True, auto_delete=False, "
                                    f"x-max-priority={expected_priority})"
                                )
                            )

                            if message_count > 0:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f"⚠ Queue has {message_count} messages - they will be lost if queue is deleted"
                                    )
                                )

                            # Delete the old queue
                            self.stdout.write(f"Deleting queue '{queue_name}'...")
                            channel.queue_delete(queue=queue_name)
                            self.stdout.write(
                                self.style.SUCCESS(f"✓ Queue '{queue_name}' deleted")
                            )

                            # Recreate with CORRECT settings: durable=True and x-max-priority
                            self.stdout.write(
                                f"Recreating queue '{queue_name}' with durable=True, "
                                f"auto_delete=False and x-max-priority={expected_priority}..."
                            )
                            channel.queue_declare(
                                queue=queue_name,
                                durable=True,
                                auto_delete=False,
                                arguments={"x-max-priority": expected_priority},
                            )
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"✓ Queue '{queue_name}' recreated with correct settings"
                                )
                            )
                        else:
                            # Error is about auto_delete or other non-critical settings
                            self.stdout.write(
                                self.style.WARNING(
                                    f"⚠ Queue '{queue_name}' has non-critical configuration differences"
                                )
                            )
                            self.stdout.write(f"Details: {error_msg}")

                except amqp_exceptions.NotFound:
                    # Queue doesn't exist, create it with priority
                    self.stdout.write(
                        f"Queue '{queue_name}' doesn't exist, creating with durable=True, "
                        f"auto_delete=False and x-max-priority={expected_priority}..."
                    )
                    channel.queue_declare(
                        queue=queue_name,
                        durable=True,
                        auto_delete=False,
                        arguments={"x-max-priority": expected_priority},
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ Queue '{queue_name}' created with correct settings"
                        )
                    )

        except socket.gaierror as e:
            self.stdout.write(
                self.style.ERROR(f"✗ Could not connect to RabbitMQ: {str(e)}")
            )
            self.stdout.write("RabbitMQ may not be available yet, skipping queue check")
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"✗ Error checking/updating queue: {str(e)}")
            )
            self.stdout.write("Queue configuration may need manual intervention")
