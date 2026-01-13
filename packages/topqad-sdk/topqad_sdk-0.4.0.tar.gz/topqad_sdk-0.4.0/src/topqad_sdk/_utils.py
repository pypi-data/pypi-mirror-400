"""utils.py.

This module contains shared utility functions used across the SDK.
"""

from urllib.parse import urlparse
from typing import Any
import logging
import os
from IPython import get_ipython


class Validator:
    """Utility class for common validation methods."""

    # Add a class-level logger
    logger = logging.getLogger(__name__)

    @staticmethod
    def is_url(url: str) -> bool:
        """Validates if the given string is a valid HTTP or HTTPS URL.

        Args:
            url (str): The URL string to validate.

        Returns:
            bool: True if valid, False otherwise.
        """
        try:
            parsed_url = urlparse(url)
            is_valid_scheme = parsed_url.scheme in ("http", "https")
            has_netloc = bool(parsed_url.netloc)
            # Check for double slashes after the scheme (excluding the initial '://')
            path_and_query = parsed_url.path + (
                "?" + parsed_url.query if parsed_url.query else ""
            )
            has_double_slash = "//" in path_and_query
            return all([is_valid_scheme, has_netloc, not has_double_slash])
        except Exception:
            Validator.logger.error(f"URL validation failed for {url}")
            return False

    @staticmethod
    def is_dict(data: Any) -> bool:
        """Checks if the input is a dictionary.

        Args:
            data: The object to check.

        Returns:
            bool: True if data is a dict, False otherwise.
        """
        return isinstance(data, dict)


class Logger:
    """Utility class for logging."""

    @staticmethod
    def setup_logging():
        """Set up logging configuration for the SDK.

        Configures the root logger and sets a specific logger for the SDK to a level
        based on the environment variable `TOPQAD_LOG_LEVEL`.
        """
        log_level_str = os.environ.get("TOPQAD_LOG_LEVEL", "INFO").upper()
        log_level = getattr(logging, log_level_str, logging.INFO)

        # Configure the root logger
        logging.basicConfig(
            level=log_level,
            format="[%(asctime)s - %(name)s:%(lineno)d - %(levelname)s] %(message)s",
        )
        # Set httpcore logger to WARNING to reduce httpx logs
        httpcore_logger = logging.getLogger("httpcore")
        httpcore_logger.setLevel(logging.WARNING)
        # Set the SDK-specific logger level
        logger_sdk = logging.getLogger("topqad_sdk")
        logger_sdk.setLevel(log_level)
        logger_sdk.info(f"Logging level set to {log_level_str}")


def handle_keyboard_interrupt(job_name, job_id, logger, client):
    """
    Handle user interruption during polling with options to stop, cancel, or resume.

    Args:
        job_name (str): The name of the job being tracked.
        job_id (str): The ID of the job being tracked.
        logger (logging.Logger): The logger instance for logging messages.
        client: The TopQAD client instance to perform job cancellation.

    Returns:
        str: "resume" if the user chooses to resume polling.

    Raises:
        KeyboardInterrupt: if the user chooses to stop or cancel the job.
    """
    print("\n\033[1;38;5;208mInterrupted. What would you like to do?\033[0m")
    print("\033[94m1: Stop tracking the job (exit, job continues on server)\033[0m")
    print("\033[94m2: Cancel the job on the server and exit\033[0m")
    print("\033[94m3: Resume waiting for the job to complete\033[0m")
    choice = input("\033[1;96mEnter your choice (1, 2, or 3): \033[0m").strip()
    logger.info(
        "User selected option %s after interrupt for Job ID %s.",
        choice,
        job_id,
    )
    if choice == "1":
        logger.info(
            "Exiting. The job for '%s' (Job ID: %s) will continue on the server.",
            job_name,
            job_id,
        )
        raise KeyboardInterrupt(
            f"Job for '{job_name}' (Job ID: {job_id}) is still running on the server."
        )
    elif choice == "2":
        client.cancel(job_id)
        logger.info(
            "Successfully requested cancellation for '%s' (Job ID: %s) to the server.",
            job_name,
            job_id,
        )
        raise KeyboardInterrupt(
            f"Successfully requested cancellation for '{job_name}' (Job ID: {job_id}) to the server."
        )
    elif choice == "3":
        logger.info(
            "Resuming the job to complete for '%s' (Job ID: %s).",
            job_name,
            job_id,
        )
        return "resume"
    else:
        print("Invalid choice. Resuming polling.")
        return "resume"


def is_notebook():
    """Check if the code is running in a Jupyter notebook environment."""
    try:
        shell = get_ipython()
        if shell is None:
            return False
        # Jupyter notebook or qtconsole
        if shell.__class__.__name__ == "ZMQInteractiveShell":
            return True
        # Terminal running IPython
        elif shell.__class__.__name__ == "TerminalInteractiveShell":
            return False
        else:
            return False
    except Exception:
        return False
