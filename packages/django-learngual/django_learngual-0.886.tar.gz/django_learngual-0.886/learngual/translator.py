import importlib
import json
import os
import time
from collections import defaultdict
from logging import getLogger

import gspread
from django.conf import settings
from django.utils import timezone, translation
from google.oauth2.service_account import Credentials
from rest_framework.serializers import ValidationError

from .cache_models import CacheTranslation
from .enums import LanguageCodeType

logger = getLogger(__file__)


def load_callable(path: str) -> object | None:
    """
    Dynamically loads a callable object from a module path string.

    This function imports a module and retrieves a specific callable attribute
    from it using a dot-separated path notation. It's useful for late binding
    of callables that are configured via settings or environment variables.

    Args:
        path (str): A dot-separated path to the callable (e.g., 'module.submodule.function_name').
                   The last component is treated as the attribute name, and everything
                   before it is treated as the module path.

    Returns:
        object | None: The callable object if found, None if the path doesn't resolve
                      to an existing callable. A warning is logged if the module
                      or callable does not exist.

    Example:
        >>> load_callable('os.path.join')
        <built-in function join>
    """
    logger.info(f"[load_callable] Attempting to load callable from path: {path}")
    paths = path.split(".")
    modules = importlib.import_module(".".join(paths[:-1]))
    result = getattr(modules, paths[-1], None)
    if not result:
        logger.warning(f"[load_callable] Module does not exist. path: {path}")
    else:
        logger.info(f"[load_callable] Successfully loaded callable: {path}")
    return result


"""
from iam_service.learngual.translator import Translator
t = self = Translator(target_language="KO")
t.log_queue
"""


class Translator:
    key = "Translator-datav2"
    queue_key = "Translator-queue"
    # Google Sheets API per-request write limit: up to ~40,000 cells
    # Conservative limit to account for rate limiting (60 writes/min per user)
    # Batch size = 5000 rows per insert = 1 write; remove_duplicate_rows = 1 write; total = 2 ops
    # 60/min quota shared across ENTIRE PROJECT (all service accounts)
    # Can be overridden via Django settings: GOOGLE_SHEETS_MAX_WRITE_CELLS
    MAX_SHEETS_WRITE_CELLS = (
        5000  # Process 5000 rows per batch to respect 60 writes/min PROJECT quota
    )

    refresh_duration = timezone.timedelta(minutes=1).total_seconds()

    def __init__(
        self,
        sheet_id=None,
        sheet_name=None,
        celery_app_path: str | None = None,
        target_language: str = None,
    ):
        """
        Initialize the Translator instance with Google Sheets integration.

        This constructor sets up the translator with necessary configuration for
        connecting to Google Sheets, managing translations, and handling async tasks
        via Celery. It clears existing cache and authenticates with Google Sheets API.

        Args:
            sheet_id (str, optional): Google Sheets document ID. If not provided, will use
                                     LEARNGUAL_TRANSLATE_SHEET_ID from Django settings or
                                     environment variables. Defaults to None.
            sheet_name (str, optional): Name of the worksheet to use. If not provided, will use
                                       LEARNGUAL_TRANSLATE_SHEET_NAME from Django settings or
                                       environment variables. Defaults to None.
            celery_app_path (str | None, optional): Dot-separated path to the Celery app instance
                                                    for async tasks. If not provided, will use
                                                    LEARNGUAL_CELERY_APP_PATH from settings or
                                                    environment variables. Defaults to None.
            target_language (str, optional): Target language code for translations (e.g., 'EN', 'KO').
                                           If not provided, defaults to the current Django
                                           language or 'EN'. Defaults to None.

        Raises:
            AssertionError: If LEARNGUAL_TRANSLATE_SHEET_ID is not set.
            AssertionError: If LEARNGUAL_TRANSLATE_SHEET_NAME is not set.

        Note:
            - Cache is preserved across Translator instances to improve performance.
            - Use force_load_translations() method or prewarm_translation_cache command
              to refresh translations from Google Sheets.
            - Requires Google service account credentials to be set in LEARNGUAL_GOOGLE_BOT_GRED.
            - The language code is converted to uppercase for consistency.
        """
        logger.info(
            f"[Translator][__init__] Initializing Translator with target_language: {target_language}"
        )
        if not target_language:
            target_language = translation.get_language() or "EN"
        target_language = target_language.upper()
        # Note: Cache is NOT cleared on init to preserve pre-warmed translations
        # Use force_load_translations() or prewarm_translation_cache command to refresh
        logger.info("[Translator][__init__] Translator initialized (cache preserved)")
        self.sheet_id = (
            sheet_id
            or getattr(settings, "LEARNGUAL_TRANSLATE_SHEET_ID", None)
            or os.getenv("LEARNGUAL_TRANSLATE_SHEET_ID")
        )
        self.sheet_name = (
            sheet_name
            or getattr(settings, "LEARNGUAL_TRANSLATE_SHEET_NAME", None)
            or os.getenv("LEARNGUAL_TRANSLATE_SHEET_NAME")
        )

        self.celery_app_path = (
            celery_app_path
            or getattr(settings, "LEARNGUAL_CELERY_APP_PATH", None)
            or os.getenv("LEARNGUAL_CELERY_APP_PATH")
        )

        assert (
            self.sheet_id
        ), "`LEARNGUAL_TRANSLATE_SHEET_ID` must be set in enviroment variable or Django setting"
        assert (
            self.sheet_name
        ), "`LEARNGUAL_TRANSLATE_SHEET_NAME` must be set in enviroment variable or Django setting"

        logger.info(
            f"[Translator][__init__] Connecting to Google Sheets - "
            f"sheet_id: {self.sheet_id}, sheet_name: {self.sheet_name}"
        )
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = json.loads(
            getattr(settings, "LEARNGUAL_GOOGLE_BOT_GRED", None)
            or os.getenv("LEARNGUAL_GOOGLE_BOT_GRED")
            or "{}"
        )
        credentials = Credentials.from_service_account_info(creds, scopes=scopes)
        self.gc = gspread.authorize(credentials)

        self.target_language = target_language
        logger.info(
            f"[Translator][__init__] Translator initialized successfully with language: {target_language}"
        )

    @property
    def translations(self):
        return self.get_cache_model().get_default_cache_model().translation

    @property
    def headers(self):
        return self.get_cache_model().get_default_cache_model().headers

    @property
    def celery_app(self):
        return load_callable(self.celery_app_path)

    def remove_duplicate_rows(self, column_name="en"):
        """
        Remove duplicate entries from the Google Sheet based on a specified column.

        This method identifies and removes duplicate rows while keeping the last
        occurrence of each unique value in the specified column. This helps maintain
        data integrity by ensuring no duplicate translations exist for the same key.

        Args:
            column_name (str, optional): The name of the column to check for duplicates.
                                        Case-insensitive search is performed. Defaults to "en".

        Raises:
            ValueError: If the specified column_name is not found in the sheet headers.

        Note:
            - Rows are deleted from bottom to top to prevent index shifting issues.
            - The last occurrence of each value is kept; earlier duplicates are removed.
            - This operation directly modifies the Google Sheet.
            - Deletion count is logged for auditing purposes.

        Example:
            >>> translator.remove_duplicate_rows('en')
            # Logs: Removed X duplicate rows from column 'en'.
        """
        # Authenticate and open the Google Sheet
        logger.info(
            f"[Translator][remove_duplicate_rows] Starting duplicate removal for column: {column_name}"
        )

        sheet = self.gc.open_by_key(self.sheet_id)
        worksheet = sheet.worksheet(self.sheet_name)

        # Get all data from the sheet
        data = worksheet.get_all_values()

        # Extract header and data rows
        header = data[0]
        rows = data[1:]

        # Find the index of the target column
        try:
            if column_name.lower() in header:
                column_index = header.index(column_name.lower())
            elif column_name.upper() in header:
                column_index = header.index(column_name.upper())
            else:
                column_index = header.index(column_name)
        except ValueError:
            raise ValueError(f"Column '{column_name}' not found in the sheet.")

        # Use a dictionary to track the last occurrence of each value in the target column
        last_occurrence = defaultdict(int)

        # Iterate through the rows to find the last occurrence of each value
        for i, row in enumerate(rows):
            value = row[column_index]
            last_occurrence[value] = i + 1  # +1 because of header

        # Build a list of row indices to keep
        rows_to_keep = set(last_occurrence.values())

        # Delete rows that are not in the rows_to_keep set
        rows_to_delete = [
            i + 2 for i in range(len(rows)) if (i + 1) not in rows_to_keep
        ]

        if rows_to_delete:
            # Use batch delete instead of individual deletes to reduce API calls
            # Sort in descending order to delete from bottom to top (avoid index shifting)
            rows_to_delete.sort(reverse=True)

            # Build batch delete requests
            requests = []
            for row_index in rows_to_delete:
                requests.append(
                    {
                        "deleteDimension": {
                            "range": {
                                "sheetId": worksheet.id,
                                "dimension": "ROWS",
                                "startIndex": row_index - 1,  # 0-indexed
                                "endIndex": row_index,  # Exclusive
                            }
                        }
                    }
                )

            # Execute batch delete in single API call
            body = {"requests": requests}
            sheet.batch_update(body)

            logger.info(
                f"[Translator][remove_duplicate_rows] Removed {len(rows_to_delete)} duplicate rows "
                f"from column '{column_name}' in a single batch operation."
            )
        else:
            logger.info(
                f"[Translator][remove_duplicate_rows] No duplicate rows found in column '{column_name}'."
            )

    def get_cache_model(self) -> CacheTranslation:
        """
        Retrieve the cache model class for translation data.

        Returns the CacheTranslation model used for caching translation data.
        This allows for abstraction of the cache backend and makes it easier
        to mock or swap implementations if needed.

        Returns:
            CacheTranslation: The cache model class for managing cached translations.
        """
        return CacheTranslation

    def update_translation(self, headers, translations):
        """
        Update the cached translation data with new headers and translations.

        This method updates the internal cache model with new translation mappings
        and language headers. It synchronizes the in-memory cache with the provided
        translation data.

        Args:
            headers (list): List of language codes representing the available languages
                          (e.g., ['EN', 'KO', 'DE']).
            translations (dict): Dictionary mapping source text to translation dictionaries.
                                Format: {source_text: {language_code: translated_text, ...}, ...}

        Note:
            - This operation updates the cache model in place.
            - Both headers and translations must be provided together for consistency.
        """
        logger.info(
            f"[Translator][update_translation] Updating cache with {len(translations)} translations "
            f"and {len(headers)} language headers"
        )

        self.get_cache_model().get_default_cache_model().update_translations(
            translations=translations, headers=headers
        )
        logger.info(
            "[Translator][update_translation] Cache update completed successfully"
        )

    def update_queue(self, *texts: str):
        """
        Add new text entries to the translation queue.

        This method adds one or more texts to the queue of untranslated strings
        that need to be translated and added to the Google Sheet. The queue is
        used to batch process new translations asynchronously.

        Args:
            *texts (str): Variable number of text strings to add to the queue.

        Returns:
            The result from the cache model's add_to_queue method.

        Example:
            >>> translator.update_queue('Hello', 'World')
        """
        logger.info(
            f"[Translator][update_queue] Adding {len(texts)} text(s) to translation queue"
        )
        logger.info(f"[Translator][update_queue] data {texts[:20]}")
        result = self.get_cache_model().get_default_cache_model().add_to_queue(*texts)
        logger.info(f"[Translator][update_queue] data in queue {self.log_queue[:20]}")
        logger.info("[Translator][update_queue] Queue updated successfully")
        return result

    def overwrite_queue(self, texts: list):
        """
        Completely overwrite the translation queue with a new list.

        This method replaces the entire queue with the provided list of texts.
        Useful for batch operations or when you need to reset the queue state
        after processing a batch of translations.

        Args:
            texts (list): Complete list of text strings to set as the new queue.

        Note:
            - This operation completely replaces the existing queue.
            - Any texts previously in the queue will be lost.

        Example:
            >>> translator.overwrite_queue(['text1', 'text2', 'text3'])
        """
        logger.info(
            f"[Translator][overwrite_queue] Overwriting queue with {len(texts)} text(s). "
            f"Previous queue size: {len(self.log_queue)}"
        )
        import traceback

        logger.info(
            f"[Translator][overwrite_queue] Stack trace:\n{''.join(traceback.format_stack()[-4:-1])}"
        )

        model = self.get_cache_model().get_default_cache_model()
        model.queue = texts
        logger.info(
            f"[Translator][overwrite_queue] Queue overwritten successfully. New size: {len(texts)}"
        )

    def force_load_translations(self):
        """
        Force reload all translations from Google Sheet and update the cache.

        This method performs a complete refresh of all translations by:
        1. Attempting to remove duplicate rows from the sheet
        2. Fetching all data from the Google Sheet
        3. Validating that required languages (EN and KO) are present
        4. Building a translation dictionary from the sheet data
        5. Updating the internal cache with the new data

        Returns:
            dict: A dictionary of all loaded translations in the format:
                  {source_text: {language_code: translated_text, ...}, ...}

        Raises:
            ValidationError: If the required EN or KO language columns are missing.

        Note:
            - Any exceptions during duplicate row removal are silently caught.
            - All header values are normalized to uppercase.
            - All text values are stripped of leading/trailing whitespace.
            - This is an expensive operation that fetches from Google Sheets.
            - The loaded translations are cached for performance.

        Example:
            >>> translator.force_load_translations()
            {'Hello': {'EN': 'Hello', 'KO': '안녕하세요'}, ...}
        """
        logger.info(
            "[Translator][force_load_translations] Initiating translation refresh from Google Sheets"
        )
        try:
            self.remove_duplicate_rows()
        except Exception as e:
            logger.warning(
                f"[Translator][force_load_translations] Failed to remove duplicates: {str(e)}"
            )
        sheet = self.gc.open_by_key(self.sheet_id)
        worksheet = sheet.worksheet(self.sheet_name)
        data = worksheet.get_all_values()

        headers = [x.upper() for x in data[0]]
        translations = {}

        if not all([x in headers for x in ["EN", "KO"]]):
            raise ValidationError("No translation for EN or KO.")

        for row in data[1:]:
            en_value = row[0].strip()
            translations[en_value] = {
                headers[i]: row[i] for i in range(1, len(headers))
            }
        logger.info(
            f"[Translator][force_load_translations] Successfully loaded {len(translations.keys())} "
            f"translations with {len(headers)} languages"
        )
        self.update_translation(headers=headers, translations=translations)
        logger.info(
            "[Translator][force_load_translations] Translation refresh completed"
        )

        return translations

    def get_language_code(self, language: str) -> str:
        """
        Normalize a language identifier to its standard language code.

        This method converts various language name formats to standardized language
        codes using the LanguageCodeType enum. It handles case-insensitive matching
        and returns the corresponding code, falling back to the uppercased input if
        no mapping is found.

        Args:
            language (str): Language name or code to normalize. Can be in any case.
                          If empty or None, defaults to 'EN'.

        Returns:
            str: The standardized uppercase language code. Returns the language
                 parameter as-is (uppercased) if no mapping is found in LanguageCodeType.

        Example:
            >>> translator.get_language_code('korean')
            'KO'
            >>> translator.get_language_code('')
            'EN'
            >>> translator.get_language_code('EN')
            'EN'
        """
        languages = {
            key.strip().upper(): value.strip().upper()
            for key, value in LanguageCodeType.dict_name_key().items()
        }
        if not language:
            language = "EN"
        language = language.strip().upper()
        return languages.get(language, language)

    @property
    def log_queue(self):
        return self.get_cache_model().get_default_cache_model().queue

    def get_language_list(self):
        """
        Retrieve a dictionary of all available translations organized by language.

        This method compiles all translations from the cache and groups them by
        language, creating a dictionary where each language code maps to a list
        of available translated strings.

        Returns:
            dict: A dictionary with language codes as keys and lists of translated
                  strings as values. Format: {"EN": [text1, text2, ...], "KO": [...], ...}
                  Languages present in headers are initialized as empty lists.

        Note:
            - The EN language list is populated from the source English texts.
            - Other languages are populated from the translation values.
            - Empty translation strings are filtered out.
            - Only languages present in self.headers are included in the result.

        Example:
            >>> translator.get_language_list()
            {
                "EN": ["Hello", "Goodbye"],
                "KO": ["안녕하세요", "안녕히 가세요"],
                "DE": ["Hallo", "Auf Wiedersehen"]
            }
        """
        logger.info(
            f"[Translator][get_language_list] Compiling language list for {len(self.headers)} languages"
        )
        data = {key.upper(): [] for key in self.headers}
        data["EN"] = []
        for en_value, value in self.translations.items():
            data["EN"].append(en_value)
            for key, micro in value.items():
                if micro and key in data:
                    data[key].append(micro)

        logger.info(
            "[Translator][get_language_list] Language list compiled successfully"
        )
        return data

    def log_microcopy(self, text: str):
        """
        Log a new microcopy string that needs translation.

        This method tracks untranslated text strings by:
        1. Adding the text to the translations cache with empty values for all languages
        2. Updating the cache model with the new translation entry
        3. Adding the text to the queue for batch processing

        The logged strings are later processed by log_microcopy_job() which adds them
        to the Google Sheet and fills in translations.

        Args:
            text (str): The text to log. Must be non-empty.

        Note:
            - Only non-empty texts that aren't already in translations are logged.
            - Duplicate queue entries are prevented by checking before adding.
            - Logging is done at info level for audit purposes.
            - The method updates both the cache and the queue simultaneously.

        Example:
            >>> translator.log_microcopy('New feature button')
            # Text is added to cache and queue for later translation
        """
        logger.info(f"[Translator][log_microcopy] Logging microcopy: {text}")
        if text not in self.translations and text:
            translations = self.translations
            headers = self.headers
            translations[text] = {headers[i]: "" for i in range(1, len(headers))}
            self.update_translation(
                **{"headers": headers, "translations": translations}
            )

            if text not in self.log_queue:
                self.update_queue(text)
                logger.info(
                    f"[Translator][log_microcopy] Added microcopy '{text}' to log queue"
                )
        else:
            logger.info(
                f"[Translator][log_microcopy] Microcopy '{text}' already exists in translations"
            )

    def log_microcopy_job(self):
        """
        Process the queue of logged microcopies by adding them to the Google Sheet.

        This is a batch processing job that:
        1. Retrieves the current queue of microcopies to be added
        2. Fetches all existing translations from the Google Sheet
        3. Filters the queue to only include texts not yet in the sheet
        4. Batches new texts in chunks of 60 rows
        5. Inserts the batch into the sheet
        6. Updates the queue to only keep unprocessed texts
        7. Reloads all translations from the sheet to sync cache

        This method should be called periodically as an async job (typically via Celery)
        to process accumulated untranslated strings in batches.

        Raises:
            ValidationError: If the sheet doesn't contain both EN and KO language columns.

        Note:
            - Processes up to 60 new entries per job run (batch size = 60).
            - Inserts new rows at the beginning of the data (after header).
            - The queue is updated to remove processed items and retain the rest.
            - After insertion, force_load_translations() syncs the cache.
            - Useful for preventing excessive individual sheet updates.

        Example:
            >>> translator.log_microcopy_job()
            # Adds up to 60 queued microcopies to sheet and syncs cache
        """
        logger.info(
            "[Translator][log_microcopy_job] Starting microcopy batch processing job"
        )
        queue_list = self.log_queue
        logger.info(
            f"[Translator][log_microcopy_job] Current queue size: {len(queue_list)}"
        )

        sheet = self.gc.open_by_key(self.sheet_id)
        worksheet = sheet.worksheet(self.sheet_name)
        data = worksheet.get_all_values()

        translations = {}
        headers = [x.upper() for x in data[0]]

        if not all([x in headers for x in ["EN", "KO"]]):
            logger.error(
                "[Translator][log_microcopy_job] EN and KO columns not found in sheet"
            )
            raise ValidationError("No translation for EN and KO")

        for row in data[1:]:
            en_value = row[0].strip()
            translations[en_value] = {
                headers[i]: row[i] for i in range(1, len(headers))
            }
        # print(f"{translations = }")
        queue_list = [x for x in self.log_queue if x not in translations]

        # Each insert writes 1 cell per row (EN only). Respect the Sheets 40k-cells limit.
        cells_per_row = 1
        max_cells = (
            getattr(
                settings, "GOOGLE_SHEETS_MAX_WRITE_CELLS", self.MAX_SHEETS_WRITE_CELLS
            )
            or self.MAX_SHEETS_WRITE_CELLS
        )
        try:
            max_cells = int(max_cells)
        except Exception:
            max_cells = self.MAX_SHEETS_WRITE_CELLS

        max_rows_per_request = max(1, max_cells // max(cells_per_row, 1))

        batch_to_update = queue_list[:max_rows_per_request]
        batch_to_keep = queue_list[max_rows_per_request:]
        logger.info(
            f"[Translator][log_microcopy_job] Filtered queue: {len(queue_list)} new items, "
            f"processing {len(batch_to_update)}, keeping {len(batch_to_keep)} for next batch"
        )
        logger.info(
            f"[Translator][log_microcopy_job] Batch to update content: {batch_to_update[:30]}"
        )
        if batch_to_update:
            logger.info(
                f"[Translator][log_microcopy_job] Inserting {len(batch_to_update)} microcopies into sheet "
                f"(limit {max_rows_per_request} rows per request based on {max_cells} cells)"
            )
            try:
                start_index = 2
                worksheet.insert_rows([[x] for x in batch_to_update], row=start_index)
                logger.info(
                    f"[Translator][log_microcopy_job] Successfully inserted {len(batch_to_update)} microcopies"
                )

                # Add delay before dedup to spread out write operations and respect rate limits
                time.sleep(2)
                logger.info(
                    "[Translator][log_microcopy_job] Waiting 2 seconds before duplicate removal"
                )

                # Clean up duplicates if any exist
                try:
                    self.remove_duplicate_rows()
                    logger.info(
                        "[Translator][log_microcopy_job] Duplicate rows cleaned up"
                    )
                except Exception as e:
                    logger.warning(
                        f"[Translator][log_microcopy_job] Failed to remove duplicates: {str(e)}"
                    )

                # Update cache with new items (done before queue clear for atomicity)
                logger.info(
                    f"[Translator][log_microcopy_job] Adding {len(batch_to_update)} new items to translations cache"
                )
                for new_text in batch_to_update:
                    # Add with empty values for all languages except EN
                    translations[new_text] = {
                        headers[i]: "" for i in range(1, len(headers))
                    }

                # Update cache with expanded translations
                self.update_translation(headers=headers, translations=translations)
                logger.info(
                    "[Translator][log_microcopy_job] Translations cache updated successfully"
                )

                # CRITICAL: Only clear queue as the FINAL operation after all writes succeed
                # If any exception occurs before this point, queue remains intact for retry
                self.overwrite_queue(batch_to_keep)
                logger.info(
                    f"[Translator][log_microcopy_job] Queue cleared - removed {len(batch_to_update)} processed items"
                )

            except Exception as e:
                logger.error(
                    f"[Translator][log_microcopy_job] Failed to insert microcopies: {str(e)}. "
                    f"Queue unchanged - {len(queue_list)} items will retry on next run."
                )
                # Don't call overwrite_queue() - leave the original queue intact
                raise
        else:
            logger.info(
                "[Translator][log_microcopy_job] No new microcopies to add to sheet"
            )

        logger.info(
            "[Translator][log_microcopy_job] Microcopy batch processing job completed"
        )

    def force_add_language_column(self, language: str):
        """
        Directly add a new language column to the Google Sheet.

        This method performs a direct write to the Google Sheet to add a new
        language column header. It only adds the column if it doesn't already exist
        in the headers.

        Args:
            language (str): The language code to add as a new column header.
                          Will be converted to uppercase.

        Note:
            - The new column header is placed at the end of existing columns.
            - No translations are initialized for the new language; all values are empty.
            - This directly modifies the Google Sheet.
            - Language code is normalized to uppercase.
            - Silently skips if language already exists in headers.

        Example:
            >>> translator.force_add_language_column('ES')
            # Adds 'ES' column to the Google Sheet
        """
        logger.info(
            f"[Translator][force_add_language_column] Attempting to add language column: {language}"
        )
        if self.headers and language not in self.headers:
            sheet = self.gc.open_by_key(self.sheet_id)
            worksheet = sheet.worksheet(self.sheet_name)
            # Add new column with target language header
            col_count = len(worksheet.row_values(1))
            worksheet.update_cell(1, col_count + 1, language.upper())
            logger.info(
                f"[Translator][force_add_language_column] Successfully added new language column: {language}"
            )
        else:
            logger.info(
                f"[Translator][force_add_language_column] Language column {language} already exists "
                f"or headers not initialized"
            )

    def add_language_column(self, language: str):
        """
        Add a new language column to both cache and Google Sheet.

        This method adds a new language in two steps:
        1. Updates the in-memory cache with the new language header
        2. Calls force_add_language_column to persist the change to Google Sheet

        Args:
            language (str): The language code to add (e.g., 'ES', 'FR', 'DE').
                          Will be converted to uppercase.

        Note:
            - Only adds the column if it doesn't already exist in headers.
            - Updates both cache and sheet for consistency.
            - The new language column will be empty for all existing translations.
            - Useful for expanding the translation system to support new languages.

        Example:
            >>> translator.add_language_column('ES')
            # Adds Spanish as a new language to both cache and sheet
        """
        logger.info(
            f"[Translator][add_language_column] Adding language column: {language}"
        )
        if self.headers and language not in self.headers:
            headers: list = self.headers
            headers.append(language.upper())
            self.update_translation(
                **{"headers": headers, "translations": self.translations}
            )

            self.force_add_language_column(language=language)
            logger.info(
                f"[Translator][add_language_column] Language column {language} added successfully "
                f"to cache and sheet"
            )
        else:
            logger.info(
                f"[Translator][add_language_column] Language column {language} already exists "
                f"or headers not initialized"
            )

    def translate(self, text: str, target_language: str):
        """
        Translate a text string to the target language.

        This is the core translation method that:
        1. Normalizes the target language code
        2. Checks if the target language is available
        3. Triggers translation load if cache is empty
        4. Looks up the translation from cache
        5. Logs untranslated microcopies for later processing
        6. Returns translated text or falls back to original

        Args:
            text (str): The text to translate. Usually English source text.
            target_language (str): The target language code (e.g., 'KO', 'korean').
                                  Will be normalized via get_language_code().

        Returns:
            str: The translated text if found and non-empty, otherwise the stripped
                 original text. Returns original text if target language is not available.

        Note:
            - Text is stripped of whitespace before processing.
            - If cache is empty, triggers async task to load translations.
            - Untranslated texts are automatically logged via log_microcopy().
            - Returns original text if translation not found or is empty.
            - Language code is case-insensitive and normalized to uppercase.

        Example:
            >>> translator.translate('Hello', 'KO')
            '안녕하세요'
            >>> translator.translate('Unknown text', 'KO')
            'Unknown text'  # Logged for later translation
        """
        target_language = self.get_language_code(target_language)
        if target_language.upper() not in self.headers:
            if not self.headers:
                logger.info(
                    "[Translator][translate] Headers not loaded, triggering async translation load task"
                )
                self.celery_app.send_task(
                    "iam.accounts.translate_load_translations",
                    routing_key="iam.accounts.translate_load_translations",
                )
            # else:
            #     self.add_language_column(target_language.upper())
            logger.warning(
                f"[Translator][translate] Language {target_language} does not exist in sheet headers"
            )
            return text
        stripped_text = text.strip()
        translated_dict = self.translations.get(stripped_text)
        if not translated_dict:
            if translated_dict is None:
                if text not in (
                    self.get_language_list()[self.get_language_code(target_language)]
                    or []
                ):
                    logger.info(
                        f"[Translator][translate] Translation not found for '{stripped_text}', logging as microcopy"
                    )
                    self.log_microcopy(stripped_text)
            return stripped_text

        translated_text = translated_dict.get(target_language, text)
        if not translated_text:
            logger.info(
                f"[Translator][translate] Empty translation for '{stripped_text}' in "
                f"language {target_language}, returning original"
            )
            return stripped_text

        return translated_text

    def get_translation(
        self, text, target_language: str | None = None, **kwargs
    ) -> str:
        """
        Get a translation of text with optional variable substitution.

        This is the main public method for retrieving translations. It handles:
        1. Language resolution (uses provided language or instance default)
        2. Translation lookup via translate()
        3. Optional string formatting/rendering with provided kwargs

        Args:
            text (str): The source text to translate.
            target_language (str | None, optional): Target language code. If not provided,
                                                   uses the instance's target_language.
                                                   Defaults to None.
            **kwargs: Optional keyword arguments for string formatting/rendering.
                     Used to substitute placeholders in the translated text.
                     Format: {key} in the translation string.

        Returns:
            str: The translated and optionally formatted text.

        Raises:
            AssertionError: If no target_language is provided and instance has no default.
            ValidationError: If kwargs are provided but translation has unmatched placeholders.

        Example:
            >>> translator.get_translation('Hello, {name}!', 'KO', name='John')
            '안녕하세요, John!'
            >>> translator.get_translation('Welcome', 'KO')
            '환영합니다'
        """
        target_language = target_language or self.target_language
        assert target_language, "target_language is required."
        logger.info(
            f"[Translator][get_translation] Getting translation for text to language: {target_language}"
        )
        result = self.translate(text, target_language)
        if kwargs:
            logger.info(
                f"[Translator][get_translation] Rendering translation with {len(kwargs)} variable(s)"
            )
            result = self.render(result, **kwargs)

        return result

    def render(self, text: str, **kwargs):
        """
        Render a text string by substituting template variables.

        This method performs Python string formatting using the provided keyword
        arguments. It's used to substitute placeholders like {name}, {count}, etc.
        into translated text strings.

        Args:
            text (str): The template text containing placeholders to substitute.
                       Placeholders use Python format string syntax: {key}
            **kwargs: Keyword arguments providing values for the placeholders.

        Returns:
            str: The rendered text with all placeholders substituted. If text is
                 empty, returns the empty string unchanged.

        Raises:
            ValidationError: If text contains placeholders that are not provided
                           in kwargs (KeyError from format() method).

        Example:
            >>> translator.render('Hello {name}, you have {count} messages',
            ...                   name='John', count=5)
            'Hello John, you have 5 messages'

            >>> translator.render('Welcome {user}', name='John')  # Missing 'user' key
            # Raises ValidationError with detail about incomplete kwargs
        """
        if not text:
            return text
        try:
            result = text.format(**kwargs)
            logger.info(
                "[Translator][render] Successfully rendered text with variables"
            )
            return result
        except KeyError as e:
            logger.error(
                f"[Translator][render] Failed to render text - incomplete kwargs: {kwargs} for text: {text}"
            )
            raise ValidationError(
                {"detail": f"Imcomplete kwargs for {kwargs} for text {text}"}
            ) from e


def translate(text, target_language: str | None = None, **kwargs) -> str:
    """
    Module-level convenience function for translating text.

    This is a convenience wrapper around the Translator class that creates
    a new Translator instance and immediately uses it to translate text.
    Useful for quick, one-off translations without maintaining a Translator instance.

    Can be used as: _(text) if aliased in templates or configuration.

    Args:
        text (str): The source text to translate.
        target_language (str | None, optional): The target language code for translation.
                                               If None, uses the current Django language
                                               or defaults to 'EN'. Defaults to None.
        **kwargs: Optional keyword arguments for variable substitution in the
                 translated text (e.g., name='John' for 'Hello {name}!')

    Returns:
        str: The translated text with optional variable substitution applied.

    Note:
        - Creates a new Translator instance for each call.
        - For high-frequency translations, consider reusing a Translator instance
          for better performance.
        - Inherits all behavior from Translator.get_translation().

    Example:
        >>> translate('Hello World', target_language='KO')
        '안녕하세요 세계'

        >>> translate('Welcome {user}', target_language='KO', user='John')
        '환영합니다 John'
    """
    logger.info(
        f"[translate] Module-level translate called for language: {target_language}"
    )
    return Translator().get_translation(text, target_language=target_language, **kwargs)
