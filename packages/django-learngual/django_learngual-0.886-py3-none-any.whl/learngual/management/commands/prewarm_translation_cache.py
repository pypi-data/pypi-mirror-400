"""
Management command to pre-warm the translation cache.

This command loads all translations from Google Sheets into the cache,
preventing the automatic trigger of translate_load_translations task
when translations are requested.
"""
from django.core.management.base import BaseCommand
from gspread.exceptions import APIError

from iam_service.learngual.translator import Translator


class Command(BaseCommand):
    help = (
        "Pre-warm the translation cache by loading all translations from Google Sheets"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force reload even if cache already exists",
        )

    def handle(self, *args, **options):
        force = options.get("force", False)

        self.stdout.write("Pre-warming translation cache...")

        try:
            translator = Translator()

            # Check if cache already has data
            if translator.headers and not force:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Cache already contains {len(translator.translations)} translations with "
                        f"{len(translator.headers)} language columns"
                    )
                )
                self.stdout.write(
                    "Use --force flag to reload translations from Google Sheets"
                )
                return

            # Load translations from Google Sheets
            self.stdout.write("Loading translations from Google Sheets...")
            translator.force_load_translations()

            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Successfully loaded {len(translator.translations)} translations with "
                    f"{len(translator.headers)} language columns into cache"
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    "✓ Translation cache is now pre-warmed and ready for use"
                )
            )

        except APIError as e:
            if e.response.status_code == 429:
                self.stdout.write(
                    self.style.WARNING(
                        "⚠ Google API rate limit exceeded during cache pre-warming"
                    )
                )
                self.stdout.write(
                    "Triggering async translation load task to retry later..."
                )
                try:
                    translator.celery_app.send_task(
                        "iam.accounts.translate_load_translations",
                        routing_key="iam.accounts.translate_load_translations",
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            "✓ Async translation load task queued successfully"
                        )
                    )
                except Exception as task_error:
                    self.stdout.write(
                        self.style.ERROR(
                            f"✗ Failed to queue async task: {str(task_error)}"
                        )
                    )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f"✗ Google API Error ({e.response.status_code}): {str(e)}"
                    )
                )
                raise

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"✗ Failed to pre-warm translation cache: {str(e)}")
            )
            raise
