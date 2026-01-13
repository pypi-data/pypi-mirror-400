"""Tests for the ChangeCrab client."""

from unittest.mock import Mock, patch

import pytest
import requests

from changecrab import ChangeCrab
from changecrab.exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)


class TestChangeCrab:
    """Test the ChangeCrab client."""

    def test_init_with_api_key(self):
        """Test client initialization with API key."""
        client = ChangeCrab(api_key="test_key")
        assert client._api_key == "test_key"
        assert client._base_url == "https://changecrab.com/api"
        assert client._timeout == 30

    def test_init_without_api_key(self):
        """Test that missing API key raises ValueError."""
        with pytest.raises(ValueError, match="API key is required"):
            ChangeCrab(api_key="")

    def test_init_with_custom_base_url(self):
        """Test client initialization with custom base URL."""
        client = ChangeCrab(api_key="test_key", base_url="https://custom.com/api")
        assert client._base_url == "https://custom.com/api"

    def test_init_with_custom_timeout(self):
        """Test client initialization with custom timeout."""
        client = ChangeCrab(api_key="test_key", timeout=60)
        assert client._timeout == 60

    @patch("changecrab.client.requests.Session")
    def test_list_changelogs(self, mock_session):
        """Test listing changelogs."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "data": [
                {
                    "id": 1,
                    "accessid": "abc123",
                    "name": "Test Changelog",
                    "team": 1,
                    "team_name": "Test Team",
                }
            ],
        }
        mock_response.status_code = 200
        mock_response.ok = True
        mock_session.return_value.request.return_value = mock_response

        client = ChangeCrab(api_key="test_key")
        changelogs = client.list_changelogs()

        assert len(changelogs) == 1
        assert changelogs[0].name == "Test Changelog"
        assert changelogs[0].access_id == "abc123"

    @patch("changecrab.client.requests.Session")
    def test_list_changelogs_with_team_id(self, mock_session):
        """Test listing changelogs with team filter."""
        mock_response = Mock()
        mock_response.json.return_value = {"success": True, "data": []}
        mock_response.status_code = 200
        mock_response.ok = True
        mock_session.return_value.request.return_value = mock_response

        client = ChangeCrab(api_key="test_key")
        client.list_changelogs(team_id=123)

        call_args = mock_session.return_value.request.call_args
        assert call_args[1]["params"]["team_id"] == 123

    @patch("changecrab.client.requests.Session")
    def test_get_changelog(self, mock_session):
        """Test getting a specific changelog."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "id": 1,
                "accessid": "abc123",
                "name": "Test Changelog",
                "team": 1,
            },
        }
        mock_response.status_code = 200
        mock_response.ok = True
        mock_session.return_value.request.return_value = mock_response

        client = ChangeCrab(api_key="test_key")
        changelog = client.get_changelog("abc123")

        assert changelog.name == "Test Changelog"
        assert changelog.access_id == "abc123"

    @patch("changecrab.client.requests.Session")
    def test_create_changelog(self, mock_session):
        """Test creating a changelog."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "id": 2,
                "accessid": "xyz789",
                "name": "New Changelog",
                "team": 1,
            },
        }
        mock_response.status_code = 200
        mock_response.ok = True
        mock_session.return_value.request.return_value = mock_response

        client = ChangeCrab(api_key="test_key")
        changelog = client.create_changelog(name="New Changelog", team=1)

        assert changelog.name == "New Changelog"
        assert changelog.access_id == "xyz789"

    @patch("changecrab.client.requests.Session")
    def test_create_post(self, mock_session):
        """Test creating a post."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "id": 1,
                "summary": "Test Post",
                "markdown": "Content",
                "type": "editor",
                "project": "abc123",
                "team": 1,
                "public": 1,
                "announced": 0,
                "draft": 0,
                "categories": [],
            },
        }
        mock_response.status_code = 200
        mock_response.ok = True
        mock_session.return_value.request.return_value = mock_response

        client = ChangeCrab(api_key="test_key")
        post = client.create_post(
            changelog_id="abc123",
            summary="Test Post",
            markdown="Content",
            team=1,
        )

        assert post.summary == "Test Post"
        assert post.markdown == "Content"

    @patch("changecrab.client.requests.Session")
    def test_authentication_error(self, mock_session):
        """Test authentication error handling."""
        mock_response = Mock()
        mock_response.json.return_value = {"success": False, "error": "Unauthorized"}
        mock_response.status_code = 401
        mock_response.ok = False
        mock_session.return_value.request.return_value = mock_response

        client = ChangeCrab(api_key="invalid_key")
        with pytest.raises(AuthenticationError):
            client.list_changelogs()

    @patch("changecrab.client.requests.Session")
    def test_not_found_error(self, mock_session):
        """Test not found error handling."""
        mock_response = Mock()
        mock_response.json.return_value = {"success": False, "error": "Not found"}
        mock_response.status_code = 404
        mock_response.ok = False
        mock_session.return_value.request.return_value = mock_response

        client = ChangeCrab(api_key="test_key")
        with pytest.raises(NotFoundError):
            client.get_changelog("invalid_id")

    @patch("changecrab.client.requests.Session")
    def test_validation_error(self, mock_session):
        """Test validation error handling."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": False,
            "error": "Validation failed",
            "errors": {"name": ["The name field is required."]},
        }
        mock_response.status_code = 422
        mock_response.ok = False
        mock_session.return_value.request.return_value = mock_response

        client = ChangeCrab(api_key="test_key")
        with pytest.raises(ValidationError) as exc_info:
            client.create_changelog(name="", team=1)

        assert "name" in exc_info.value.errors

    @patch("changecrab.client.requests.Session")
    def test_rate_limit_error(self, mock_session):
        """Test rate limit error handling."""
        mock_response = Mock()
        mock_response.json.return_value = {"success": False, "error": "Rate limit exceeded"}
        mock_response.status_code = 429
        mock_response.ok = False
        mock_session.return_value.request.return_value = mock_response

        client = ChangeCrab(api_key="test_key")
        with pytest.raises(RateLimitError):
            client.list_changelogs()

    @patch("changecrab.client.requests.Session")
    def test_server_error(self, mock_session):
        """Test server error handling."""
        mock_response = Mock()
        mock_response.json.return_value = {"success": False, "error": "Internal server error"}
        mock_response.status_code = 500
        mock_response.ok = False
        mock_session.return_value.request.return_value = mock_response

        client = ChangeCrab(api_key="test_key")
        with pytest.raises(ServerError):
            client.list_changelogs()

    @patch("changecrab.client.requests.Session")
    def test_update_changelog(self, mock_session):
        """Test updating a changelog."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "id": 1,
                "accessid": "abc123",
                "name": "Updated Changelog",
                "team": 1,
                "accent": "#FF0000",
            },
        }
        mock_response.status_code = 200
        mock_response.ok = True
        mock_session.return_value.request.return_value = mock_response

        client = ChangeCrab(api_key="test_key")
        changelog = client.update_changelog("abc123", accent="#FF0000")

        assert changelog.accent == "#FF0000"

    @patch("changecrab.client.requests.Session")
    def test_delete_changelog(self, mock_session):
        """Test deleting a changelog."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "message": "Changelog deleted successfully",
        }
        mock_response.status_code = 200
        mock_response.ok = True
        mock_session.return_value.request.return_value = mock_response

        client = ChangeCrab(api_key="test_key")
        result = client.delete_changelog("abc123")

        assert result is True

    @patch("changecrab.client.requests.Session")
    def test_list_categories(self, mock_session):
        """Test listing categories."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "data": [
                {
                    "id": 1,
                    "title": "Bug Fixes",
                    "colour": "#EF4444",
                    "type": "changelog",
                    "project": "abc123",
                    "isDefault": 0,
                }
            ],
        }
        mock_response.status_code = 200
        mock_response.ok = True
        mock_session.return_value.request.return_value = mock_response

        client = ChangeCrab(api_key="test_key")
        categories = client.list_categories("abc123")

        assert len(categories) == 1
        assert categories[0].title == "Bug Fixes"

    @patch("changecrab.client.requests.Session")
    def test_list_posts(self, mock_session):
        """Test listing posts."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "data": [
                {
                    "id": 1,
                    "summary": "Test Post",
                    "markdown": "Content",
                    "type": "editor",
                    "project": "abc123",
                    "team": 1,
                    "public": 1,
                    "announced": 0,
                    "draft": 0,
                    "categories": [],
                }
            ],
        }
        mock_response.status_code = 200
        mock_response.ok = True
        mock_session.return_value.request.return_value = mock_response

        client = ChangeCrab(api_key="test_key")
        posts = client.list_posts("abc123")

        assert len(posts) == 1
        assert posts[0].summary == "Test Post"

    @patch("changecrab.client.requests.Session")
    def test_update_post(self, mock_session):
        """Test updating a post."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "id": 1,
                "summary": "Updated Post",
                "markdown": "Updated content",
                "type": "editor",
                "project": "abc123",
                "team": 1,
                "public": 1,
                "announced": 1,
                "draft": 0,
                "categories": [],
            },
        }
        mock_response.status_code = 200
        mock_response.ok = True
        mock_session.return_value.request.return_value = mock_response

        client = ChangeCrab(api_key="test_key")
        post = client.update_post(
            changelog_id="abc123",
            post_id=1,
            markdown="Updated content",
            team=1,
            summary="Updated Post",
            announced=True,
        )

        assert post.summary == "Updated Post"
        assert post.announced is True

    @patch("changecrab.client.requests.Session")
    def test_delete_post(self, mock_session):
        """Test deleting a post."""
        mock_response = Mock()
        mock_response.json.return_value = {"success": True, "message": "Post deleted successfully"}
        mock_response.status_code = 200
        mock_response.ok = True
        mock_session.return_value.request.return_value = mock_response

        client = ChangeCrab(api_key="test_key")
        result = client.delete_post("abc123", post_id=1)

        assert result is True

    @patch("changecrab.client.requests.Session")
    @patch("changecrab.client.time.sleep")
    def test_retry_on_timeout(self, mock_sleep, mock_session):
        """Test retry logic on timeout errors."""
        mock_response = Mock()
        mock_response.json.return_value = {"success": True, "data": []}
        mock_response.status_code = 200
        mock_response.ok = True

        mock_session.return_value.request.side_effect = [
            requests.Timeout("Connection timeout"),
            requests.Timeout("Connection timeout"),
            mock_response,
        ]

        client = ChangeCrab(api_key="test_key", max_retries=2, retry_delay=0.1)
        changelogs = client.list_changelogs()

        assert len(changelogs) == 0
        assert mock_sleep.call_count == 2

    @patch("changecrab.client.requests.Session")
    @patch("changecrab.client.time.sleep")
    def test_retry_exhausted(self, mock_sleep, mock_session):
        """Test that retries are exhausted after max attempts."""
        mock_session.return_value.request.side_effect = requests.Timeout("Connection timeout")

        client = ChangeCrab(api_key="test_key", max_retries=2, retry_delay=0.1)
        with pytest.raises(Exception) as exc_info:
            client.list_changelogs()

        assert "Request failed after" in str(exc_info.value)
        assert mock_sleep.call_count == 2

    def test_init_with_retry_params(self):
        """Test client initialization with retry parameters."""
        client = ChangeCrab(api_key="test_key", max_retries=5, retry_delay=2.0)
        assert client._max_retries == 5
        assert client._retry_delay == 2.0

    @patch("changecrab.client.requests.Session")
    def test_request_exception(self, mock_session):
        """Test handling of request exceptions."""
        mock_session.return_value.request.side_effect = requests.RequestException(
            "Connection error"
        )

        client = ChangeCrab(api_key="test_key")
        with pytest.raises(Exception) as exc_info:
            client.list_changelogs()

        assert "Request failed" in str(exc_info.value)

