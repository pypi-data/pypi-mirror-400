"""Entry point wrapper for early logging configuration.

This must be imported BEFORE glaip_sdk.cli.main to catch import-time warnings.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import sys

# Configure logging BEFORE importing anything else
from glaip_sdk.runner.logging_config import setup_cli_logging

setup_cli_logging()

# Now import and run CLI
from glaip_sdk.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())  # pylint: disable=no-value-for-parameter
