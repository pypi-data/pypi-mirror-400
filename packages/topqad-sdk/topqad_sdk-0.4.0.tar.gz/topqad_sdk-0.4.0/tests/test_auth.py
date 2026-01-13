import os
from unittest import TestCase
from unittest.mock import patch
from topqad_sdk._auth._auth_manager import *
from topqad_sdk._exceptions import MissingRefreshToken


class TestTokenValidation(TestCase):
    """Tests for token validation utility functions."""

    @patch.dict(os.environ, {}, clear=True)
    @patch("topqad_sdk._auth._auth_manager.load_dotenv", return_value=None)
    def test_refresh_token_not_set_raises_error(self, mock_load_dotenv):
        """Should raise MissingRefreshToken if TOPQAD_REFRESH_TOKEN is missing."""
        with self.assertRaises(MissingRefreshToken) as context:
            read_token_from_env()
        self.assertIn("TOPQAD_REFRESH_TOKEN is not set", str(context.exception))
        mock_load_dotenv.assert_called_once()

    @patch.dict(os.environ, {"TOPQAD_REFRESH_TOKEN": "test_refresh_token"}, clear=True)
    @patch("topqad_sdk._auth._auth_manager.load_dotenv", return_value=None)
    def test_refresh_token_exists_when_set(self, mock_load_dotenv):
        """Should return the token if TOPQAD_REFRESH_TOKEN is set."""
        token = read_token_from_env()
        self.assertEqual(token, "test_refresh_token")
        mock_load_dotenv.assert_called_once()

    @patch.dict(os.environ, {"TOPQAD_REFRESH_TOKEN": ""}, clear=True)
    @patch("topqad_sdk._auth._auth_manager.load_dotenv", return_value=None)
    def test_refresh_token_empty_string_raises_error(self, mock_load_dotenv):
        """Should raise MissingRefreshToken if TOPQAD_REFRESH_TOKEN is empty."""
        with self.assertRaises(MissingRefreshToken):
            read_token_from_env()
        mock_load_dotenv.assert_called_once()

    @patch(
        "topqad_sdk._auth._auth_manager.read_token_from_env",
        return_value="test_refresh_token",
    )
    def test_is_refresh_token_set_success(self, mock_read_token):
        """Should return True if TOPQAD_REFRESH_TOKEN is set."""
        result = is_refresh_token_set()
        self.assertTrue(result)

    @patch(
        "topqad_sdk._auth._auth_manager.read_token_from_env",
        side_effect=MissingRefreshToken("TOPQAD_REFRESH_TOKEN is not set."),
    )
    def test_is_refresh_token_set_failure_logs_warning(self, mock_read_token):
        """Should return False and log a warning if TOPQAD_REFRESH_TOKEN is missing."""
        with self.assertLogs("topqad_sdk._auth._auth_manager", level="WARNING") as cm:
            result = is_refresh_token_set()
        self.assertFalse(result)
        self.assertIn("Missing refresh token", cm.output[0])
