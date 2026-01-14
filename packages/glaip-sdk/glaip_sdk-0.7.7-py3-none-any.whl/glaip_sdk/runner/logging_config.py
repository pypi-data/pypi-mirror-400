"""Logging configuration for CLI to suppress noisy dependency warnings.

This module provides centralized logging suppression for optional dependencies
that emit noisy warnings during CLI usage. Warnings are suppressed by default
but can be shown using GLAIP_LOG_LEVEL=DEBUG.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import logging
import os
import warnings

NOISY_LOGGERS = ["transformers", "gllm_privacy", "google.cloud.aiplatform"]


class NameFilter(logging.Filter):
    """Filter logs by logger name prefix."""

    def __init__(self, prefixes: list[str]) -> None:
        """Initialize filter with logger name prefixes to suppress.

        Args:
            prefixes: List of logger name prefixes to filter out.
        """
        super().__init__()
        self.prefixes = prefixes

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log records by name prefix.

        Args:
            record: Log record to filter.

        Returns:
            False if record should be suppressed, True otherwise.
        """
        return not any(record.name.startswith(p) for p in self.prefixes)


def setup_cli_logging() -> None:
    """Suppress INFO from noisy third-party libraries.

    Use GLAIP_LOG_LEVEL=DEBUG to see all warnings.
    This function is idempotent - calling it multiple times is safe.
    """
    # Check env level FIRST before any suppression
    env_level = os.getenv("GLAIP_LOG_LEVEL", "").upper()
    is_debug = env_level == "DEBUG"

    if is_debug:
        # Debug mode: show everything, no suppression
        if env_level and hasattr(logging, env_level):
            logging.basicConfig(level=getattr(logging, env_level))
        return

    # Default mode: suppress noisy warnings
    if env_level and hasattr(logging, env_level):
        logging.basicConfig(level=getattr(logging, env_level))

    # Add handler filter to suppress by name prefix (handles child loggers)
    # Check if filter already exists to ensure idempotency
    root_logger = logging.getLogger()
    has_name_filter = any(isinstance(f, NameFilter) for h in root_logger.handlers for f in h.filters)

    if not has_name_filter:
        handler = logging.StreamHandler()
        handler.addFilter(NameFilter(NOISY_LOGGERS))
        root_logger.addHandler(handler)

    # Suppress FutureWarning for GCS (idempotent - multiple calls are safe)
    warnings.filterwarnings(
        "ignore",
        category=FutureWarning,
        message=r".*google-cloud-storage.*",
    )
