import pytest
from unittest.mock import patch, MagicMock
import json
import os
import sys

from tracebloc_package.linkModelDataSet import LinkModelDataSet

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pathlib import Path

from tracebloc_package.user import User

# Mock credentials for testing
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "test_password"
TEST_TOKEN = "dummy_test_token_12345"


@pytest.fixture
def mock_user():
    """Create a mock user that simulates the interactive login"""
    # Mock the input and getpass to simulate user entering credentials
    with patch("builtins.input", return_value=TEST_EMAIL), patch(
        "getpass.getpass", return_value=TEST_PASSWORD
    ), patch("requests.post") as mock_post:
        # Mock successful login response
        mock_post.return_value = MagicMock(
            status_code=200, text=json.dumps({"token": TEST_TOKEN})
        )

        # Create user instance which will trigger the mocked input prompts
        user = User()
        return user


class TestUser:
    def test_user_initialization(self):
        """Test user initialization with prompted credentials"""
        with patch("builtins.input", return_value=TEST_EMAIL), patch(
            "getpass.getpass", return_value=TEST_PASSWORD
        ), patch("requests.post") as mock_post:
            mock_post.return_value = MagicMock(
                status_code=200, text=json.dumps({"token": TEST_TOKEN})
            )

            user = User()

            assert getattr(user, "_User__username") == TEST_EMAIL
            assert getattr(user, "_User__password") == TEST_PASSWORD
            assert getattr(user, "_User__token") == TEST_TOKEN

    def test_login_success(self, mock_user):
        """Test successful login"""
        with patch("requests.post") as mock_post:
            mock_post.return_value = MagicMock(
                status_code=200, text=json.dumps({"token": TEST_TOKEN})
            )

            token = mock_user.login()
            assert token == TEST_TOKEN

    def test_login_failure(self):
        """Test failed login attempt"""
        with patch("builtins.input", return_value=TEST_EMAIL), patch(
            "getpass.getpass", return_value="wrong_password"
        ), patch("requests.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=401)

            user = User()
            token = user.login()
            assert token == ""

    def test_logout_success(self, mock_user):
        """Test logout functionality"""
        with patch("requests.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200)

            # Verify token exists before logout
            assert getattr(mock_user, "_User__token") == TEST_TOKEN

            mock_user.logout()

            # Verify token is cleared after logout
            assert getattr(mock_user, "_User__token") is None

    def test_logout_failure(self, mock_user):
        """Test logout functionality"""
        with patch("requests.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=400)

            # Verify token exists before logout
            assert getattr(mock_user, "_User__token") == TEST_TOKEN

            mock_user.logout()

            # Verify token is cleared after logout
            assert getattr(mock_user, "_User__token") == TEST_TOKEN

    def test_prompt_credentials(self):
        """Test that User prompts for credentials"""
        with patch("builtins.input") as mock_input, patch(
            "getpass.getpass"
        ) as mock_getpass, patch("requests.post") as mock_post:
            mock_input.return_value = TEST_EMAIL
            mock_getpass.return_value = TEST_PASSWORD
            mock_post.return_value = MagicMock(
                status_code=200, text=json.dumps({"token": TEST_TOKEN})
            )

            user = User()

            # Verify that input was called for email
            mock_input.assert_called_once_with("Enter your email address : ")
            # Verify that getpass was called for password
            mock_getpass.assert_called_once_with("Enter your password : ")

    def test_help_output(self, capsys, mock_user):
        """Test that help() method prints the expected documentation"""
        mock_user.help()
        captured = capsys.readouterr()

        # Expected output strings based on the help() implementation
        expected_outputs = [
            "User is a method in this package which authenticates the user",
            "provides access to Tracebloc",
            "Only registered Users are allowed to access this package",
            "In order to authenticate, run cell",
            "Enter email register on tracebloc and password",
            "Other user attributes are uploadModel() and linkModelDataset()",
            "uploadModel():",
            "This helps user to upload a compatible model and weights",
            "linkModelDataset():",
            "Link uploaded model with a dataset",
        ]

        # Check that each expected string appears in the output
        for expected in expected_outputs:
            assert expected in captured.out
