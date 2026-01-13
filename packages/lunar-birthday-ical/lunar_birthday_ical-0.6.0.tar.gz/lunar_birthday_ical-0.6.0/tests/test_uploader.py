"""Tests for uploader."""

from pathlib import Path
from unittest.mock import MagicMock, Mock, mock_open, patch

import httpx
import pytest

from lunar_birthday_ical.uploader import GitHubGistUploader, PastebinWorkerUploader


@pytest.fixture
def mock_file() -> Path:
    """Fixture for mock file path."""
    return Path("/path/to/mock/file.txt")


@pytest.fixture
def mock_config() -> dict:
    """Fixture for mock configuration."""
    return {
        "pastebin": {
            "base_url": "http://mockbaseurl.com",
            "manage_url": "http://mockbaseurl.com/mockname:mockpassword",
            "expiration": "7d",
        }
    }


class TestPastebinUploader:
    """Test cases for PastebinWorkerUploader class."""

    def test_init_with_full_config(self) -> None:
        """Test initialization with full configuration."""
        config = {
            "base_url": "http://testurl.com",
            "manage_url": "http://testurl.com/manage",
            "expiration": "7d",
        }
        uploader = PastebinWorkerUploader(config)

        assert uploader.base_url == "http://testurl.com"
        assert uploader.manage_url == "http://testurl.com/manage"
        assert uploader.expiration == "7d"

    def test_init_with_default_values(self) -> None:
        """Test initialization with default values."""
        config = {}
        uploader = PastebinWorkerUploader(config)

        assert uploader.base_url == "https://komj.uk"
        assert uploader.manage_url is None
        assert uploader.expiration == ""

    @patch("builtins.open", new_callable=mock_open, read_data="mock file content")
    @patch("httpx.post")
    def test_create_paste(
        self, mock_post: Mock, mock_open_file: Mock, mock_file: Path
    ) -> None:
        """Test creating a new paste."""
        config = {"base_url": "http://mockbaseurl.com", "expiration": "7d"}
        uploader = PastebinWorkerUploader(config)

        mock_response = httpx.Response(200, json={"key": "value"})
        mock_response.request = httpx.Request("POST", "http://mockbaseurl.com")
        mock_post.return_value = mock_response

        result = uploader.upload(mock_file)

        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args.kwargs
        assert call_kwargs["data"]["p"] is True
        assert call_kwargs["data"]["e"] == "7d"
        assert result == {"key": "value"}

    @patch("builtins.open", new_callable=mock_open, read_data="mock file content")
    @patch("httpx.put")
    def test_update_paste(
        self, mock_put: Mock, mock_open_file: Mock, mock_file: Path
    ) -> None:
        """Test updating an existing paste."""
        config = {
            "base_url": "http://mockbaseurl.com",
            "manage_url": "http://mockbaseurl.com/manage",
            "expiration": "7d",
        }
        uploader = PastebinWorkerUploader(config)

        mock_response = httpx.Response(200, json={"key": "value"})
        mock_response.request = httpx.Request("PUT", "http://mockbaseurl.com/manage")
        mock_put.return_value = mock_response

        result = uploader.upload(mock_file)

        mock_put.assert_called_once()
        call_kwargs = mock_put.call_args.kwargs
        assert call_kwargs["data"]["e"] == "7d"
        assert result == {"key": "value"}

    @patch("builtins.open", new_callable=mock_open, read_data="mock file content")
    @patch("httpx.post")
    def test_create_paste_no_expiration(
        self, mock_post: Mock, mock_open_file: Mock, mock_file: Path
    ) -> None:
        """Test creating a paste without expiration."""
        config = {"base_url": "http://mockbaseurl.com"}
        uploader = PastebinWorkerUploader(config)

        mock_response = httpx.Response(200, json={"key": "value"})
        mock_response.request = httpx.Request("POST", "http://mockbaseurl.com")
        mock_post.return_value = mock_response

        uploader.upload(mock_file)

        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args.kwargs
        assert call_kwargs["data"]["p"] is True
        assert "e" not in call_kwargs["data"]


class TestGitHubGistUploader:
    """Test cases for GitHubGistUploader class."""

    def test_init_with_valid_config(self) -> None:
        """Test initialization with valid configuration."""
        config = {
            "token": "test_token",
            "gist_id": "abc123",
            "description": "Test Gist",
            "public": True,
        }
        uploader = GitHubGistUploader(config)

        assert uploader.token == "test_token"
        assert uploader.gist_id == "abc123"
        assert uploader.description == "Test Gist"
        assert uploader.public is True

    def test_init_without_token_raises_error(self) -> None:
        """Test initialization without token raises ValueError."""
        config = {"gist_id": "abc123"}

        with pytest.raises(ValueError, match="GitHub token is required"):
            GitHubGistUploader(config)

    def test_init_with_default_values(self) -> None:
        """Test initialization with default values."""
        config = {"token": "test_token"}
        uploader = GitHubGistUploader(config)

        assert uploader.token == "test_token"
        assert uploader.gist_id is None
        assert uploader.description == "Lunar Birthday iCalendar"
        assert uploader.public is False

    def test_get_headers(self) -> None:
        """Test HTTP headers generation."""
        config = {"token": "test_token"}
        uploader = GitHubGistUploader(config)

        headers = uploader._get_headers()

        assert headers["Accept"] == "application/vnd.github+json"
        assert headers["Authorization"] == "Bearer test_token"
        assert headers["X-GitHub-Api-Version"] == "2022-11-28"

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="BEGIN:VCALENDAR\nEND:VCALENDAR",
    )
    @patch("httpx.post")
    def test_create_gist(self, mock_post: MagicMock, mock_file: MagicMock) -> None:
        """Test creating a new gist."""
        config = {
            "token": "test_token",
            "description": "Test Calendar",
            "public": False,
        }
        uploader = GitHubGistUploader(config)

        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {
            "id": "new_gist_id",
            "html_url": "https://gist.github.com/new_gist_id",
        }
        mock_post.return_value = mock_response

        file_path = Path("/tmp/test.ics")
        result = uploader.upload(file_path)

        assert result["id"] == "new_gist_id"
        assert "html_url" in result
        mock_post.assert_called_once()

        # Verify the payload
        call_kwargs = mock_post.call_args.kwargs
        assert call_kwargs["json"]["description"] == "Test Calendar"
        assert call_kwargs["json"]["public"] is False
        assert "test.ics" in call_kwargs["json"]["files"]

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="BEGIN:VCALENDAR\nEND:VCALENDAR",
    )
    @patch("httpx.patch")
    def test_update_gist(self, mock_patch: MagicMock, mock_file: MagicMock) -> None:
        """Test updating an existing gist."""
        config = {
            "token": "test_token",
            "gist_id": "existing_gist_id",
            "description": "Updated Calendar",
        }
        uploader = GitHubGistUploader(config)

        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {
            "id": "existing_gist_id",
            "html_url": "https://gist.github.com/existing_gist_id",
        }
        mock_patch.return_value = mock_response

        file_path = Path("/tmp/test.ics")
        result = uploader.upload(file_path)

        assert result["id"] == "existing_gist_id"
        mock_patch.assert_called_once()

        # Verify the URL includes gist_id
        call_args = mock_patch.call_args
        assert "existing_gist_id" in call_args.args[0]

        # Verify the payload
        call_kwargs = mock_patch.call_args.kwargs
        assert call_kwargs["json"]["description"] == "Updated Calendar"
        assert "test.ics" in call_kwargs["json"]["files"]
