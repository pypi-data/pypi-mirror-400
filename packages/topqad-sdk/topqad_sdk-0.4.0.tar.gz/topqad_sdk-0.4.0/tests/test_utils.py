import os
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch
from parameterized import parameterized
from topqad_sdk._exceptions import TopQADJobInterrupted
from topqad_sdk._utils import Validator, Logger, handle_keyboard_interrupt, is_notebook
from tests.test_helpers import generate_test_name


class TestValidator(TestCase):
    """Tests for the Validator utility class."""

    @parameterized.expand(
        [
            ("valid_http", "http://example.com", True),
            ("valid_https", "https://example.com", True),
            ("valid_http_path", "http://example.com/path/to/resource", True),
            ("valid_https_query", "https://example.com/path?query=1", True),
        ],
        name_func=generate_test_name,
    )
    def test_is_url_valid(self, name, url, expected):
        """Test valid URLs using the is_url method."""
        self.assertEqual(Validator.is_url(url), expected)

    @parameterized.expand(
        [
            ("invalid_ftp", "ftp://example.com", False),
            ("invalid_http", "http:/example.com", False),
            ("invalid_empty", "http://", False),
            ("invalid_path", "http:///path", False),
            ("invalid_string", "just-a-string", False),
        ],
        name_func=generate_test_name,
    )
    def test_is_url_invalid(self, name, url, expected):
        """Test invalid URLs using the is_url method."""
        self.assertEqual(Validator.is_url(url), expected)

    @parameterized.expand(
        [
            ("none", None, False),
            ("integer", 12345, False),
            ("list", [], False),
        ],
        name_func=generate_test_name,
    )
    def test_is_url_exception(self, name, input_value, expected):
        """Test exceptions for invalid input types using the is_url method."""
        self.assertEqual(Validator.is_url(input_value), expected)

    @parameterized.expand(
        [
            ("empty_dict", {}, True),
            ("valid_dict", {"key": "value"}, True),
            ("list", [], False),
            ("string", "string", False),
            ("integer", 123, False),
        ],
        name_func=generate_test_name,
    )
    def test_is_dict(self, name, input_value, expected):
        """Test the is_dict method for various input types."""
        self.assertEqual(Validator.is_dict(input_value), expected)


class TestLogger(TestCase):
    """Tests for the Logger utility class."""

    @patch("logging.basicConfig")
    @patch("logging.getLogger")
    def test_setup_logging_default_level(self, mock_get_logger, mock_basic_config):
        """Test logging setup with default log level."""
        if "TOPQAD_LOG_LEVEL" in os.environ:
            del os.environ["TOPQAD_LOG_LEVEL"]

        Logger.setup_logging()

        mock_basic_config.assert_called_once_with(
            level=logging.INFO,
            format="[%(asctime)s - %(name)s:%(lineno)d - %(levelname)s] %(message)s",
        )
        mock_get_logger.assert_called_with("topqad_sdk")

    @patch("logging.basicConfig")
    @patch("logging.getLogger")
    def test_setup_logging_custom_level(self, mock_get_logger, mock_basic_config):
        """Test logging setup with a custom log level from environment variable."""
        os.environ["TOPQAD_LOG_LEVEL"] = "DEBUG"

        Logger.setup_logging()

        mock_basic_config.assert_called_once_with(
            level=logging.DEBUG,
            format="[%(asctime)s - %(name)s:%(lineno)d - %(levelname)s] %(message)s",
        )
        mock_get_logger.assert_called_with("topqad_sdk")

    @patch("logging.basicConfig")
    @patch("logging.getLogger")
    def test_setup_logging_invalid_level(self, mock_get_logger, mock_basic_config):
        """Test logging setup with an invalid log level in environment variable."""
        os.environ["TOPQAD_LOG_LEVEL"] = "INVALID_LEVEL"

        Logger.setup_logging()

        mock_basic_config.assert_called_once_with(
            level=logging.INFO,
            format="[%(asctime)s - %(name)s:%(lineno)d - %(levelname)s] %(message)s",
        )
        mock_get_logger.assert_called_with("topqad_sdk")


class TestKeyboardInterrupt(TestCase):
    """Tests for the handle_keyboard_interrupt function."""

    @classmethod
    def setUpClass(cls):
        cls.logger = logging.getLogger("test_logger")
        cls.client = MagicMock()
        cls.job_name = "test_job"
        cls.job_id = "test-job-id"

    @parameterized.expand(
        [
            ("1", "is still running on the server", False),
            ("2", "Successfully requested cancellation for", True),
        ]
    )
    @patch("builtins.input")
    def test_handle_keyboard_interrupt_stop_and_cancel(
        self, user_choice, expected_message, should_cancel, mock_input
    ):
        mock_input.return_value = user_choice

        with self.assertLogs(self.logger, level="INFO") as log:
            with self.assertRaises(KeyboardInterrupt) as exc:
                handle_keyboard_interrupt(
                    self.job_name, self.job_id, self.logger, self.client
                )
            self.assertIn(expected_message, str(exc.exception))
            if should_cancel:
                self.client.cancel.assert_called_once_with(self.job_id)
            else:
                self.client.cancel.assert_not_called()
            # Check log message for user selection
            self.assertTrue(
                any(
                    f"User selected option {user_choice} after interrupt" in msg
                    for msg in log.output
                )
            )

    @patch("builtins.input", return_value="3")
    def test_handle_keyboard_interrupt_resume(self, mock_input):

        with self.assertLogs(self.logger, level="INFO") as log:
            result = handle_keyboard_interrupt(
                self.job_name, self.job_id, self.logger, self.client
            )
            self.assertEqual(result, "resume")
            self.assertTrue(
                any("Resuming the job to complete for" in msg for msg in log.output)
            )

    @patch("builtins.input", return_value="invalid")
    def test_handle_keyboard_interrupt_invalid_choice(self, mock_input):

        with self.assertLogs(self.logger, level="INFO"):
            result = handle_keyboard_interrupt(
                self.job_name, self.job_id, self.logger, self.client
            )
            self.assertEqual(result, "resume")


class TestIsNotebook(TestCase):
    def test_zmq_interactive_shell(self):
        mock_shell = MagicMock()
        mock_shell.__class__.__name__ = "ZMQInteractiveShell"
        with patch("topqad_sdk._utils.get_ipython", return_value=mock_shell):
            self.assertTrue(is_notebook())

    def test_terminal_interactive_shell(self):
        mock_shell = MagicMock()
        mock_shell.__class__.__name__ = "TerminalInteractiveShell"
        with patch("topqad_sdk._utils.get_ipython", return_value=mock_shell):
            self.assertFalse(is_notebook())

    def test_none_shell(self):
        with patch("topqad_sdk._utils.get_ipython", return_value=None):
            self.assertFalse(is_notebook())

    def test_exception(self):
        with patch("topqad_sdk._utils.get_ipython", side_effect=Exception("fail")):
            self.assertFalse(is_notebook())
