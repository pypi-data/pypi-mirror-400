"""Calendar uploaders for various services."""

import json
import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class CalendarUploader(ABC):
    """Abstract base class for calendar uploaders.

    This class defines the interface for uploading calendar files to various services.
    Subclasses should implement the upload method according to the specific service API.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize the uploader with configuration.

        Args:
            config: Configuration dictionary specific to the uploader service.
        """
        self.config = config

    @abstractmethod
    def upload(self, file: Path) -> dict[str, Any]:
        """Upload a calendar file to the service.

        Args:
            file: Path to the calendar file to upload.

        Returns:
            Response data from the upload operation.

        Raises:
            httpx.HTTPError: If the upload request fails.
        """
        pass


class PastebinWorkerUploader(CalendarUploader):
    """Uploader for pastebin-compatible services.

    This uploader supports creating new pastes and updating existing ones
    using pastebin-compatible API endpoints.
    """

    API_BASE_URL = "https://komj.uk"

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize the pastebin uploader.

        Args:
            config: Configuration dictionary with keys:
                - base_url: Base URL of the pastebin service
                - manage_url: Optional URL for updating existing paste
                - expiration: Optional expiration time for the paste
        """
        super().__init__(config)
        self.base_url: str = config.get("base_url", self.API_BASE_URL)
        self.manage_url: str | None = config.get("manage_url")
        self.expiration: int | str = config.get("expiration", "")

    def upload(self, file: Path) -> dict[str, Any]:
        """Upload a calendar file to pastebin.

        Args:
            file: Path to the calendar file to upload.

        Returns:
            JSON response from the pastebin service.

        Raises:
            httpx.HTTPError: If the upload request fails.
        """
        if not self.manage_url:
            response = self._create_paste(file)
        else:
            response = self._update_paste(file)

        logger.debug(json.dumps(response.json(), ensure_ascii=False, default=str))
        return response.json()

    def _create_paste(self, file: Path) -> httpx.Response:
        """Create a new paste on the pastebin service.

        Args:
            file: Path to the calendar file to upload.

        Returns:
            HTTP response from the pastebin service.
        """
        with open(file, "rb") as f:
            files = {"c": f}
            # private mode by default
            data: dict[str, Any] = {"p": True}
            if self.expiration:
                data["e"] = self.expiration

            response = httpx.post(f"{self.base_url}/", data=data, files=files)
            response.raise_for_status()
            return response

    def _update_paste(self, file: Path) -> httpx.Response:
        """Update an existing paste on the pastebin service.

        Args:
            file: Path to the calendar file to upload.

        Returns:
            HTTP response from the pastebin service.
        """
        with open(file, "rb") as f:
            files = {"c": f}
            data: dict[str, Any] = {}
            if self.expiration:
                data["e"] = self.expiration

            response = httpx.put(self.manage_url, data=data, files=files)
            response.raise_for_status()
            return response


class GitHubGistUploader(CalendarUploader):
    """Uploader for GitHub Gist service.

    This uploader supports creating new gists and updating existing ones
    using the GitHub Gist API. Requires a GitHub personal access token
    with gist scope.
    """

    API_BASE_URL = "https://api.github.com"

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize the GitHub Gist uploader.

        Args:
            config: Configuration dictionary with keys:
                - token: GitHub personal access token (required)
                - gist_id: Optional gist ID for updating existing gist
                - description: Optional description for the gist
                - public: Whether the gist should be public (default: False)
        """
        super().__init__(config)
        self.token: str = os.environ.get("GITHUB_TOKEN") or config.get("token", "")
        self.gist_id: str | None = config.get("gist_id")
        self.description: str = config.get("description", "Lunar Birthday iCalendar")
        self.public: bool = config.get("public", False)

        if not self.token:
            raise ValueError("GitHub token is required for GitHubGistUploader")

    def upload(self, file: Path) -> dict[str, Any]:
        """Upload a calendar file to GitHub Gist.

        Args:
            file: Path to the calendar file to upload.

        Returns:
            JSON response from the GitHub Gist API, containing gist details
            including the gist ID and URLs.

        Raises:
            httpx.HTTPError: If the upload request fails.
            ValueError: If the GitHub token is not provided.
        """
        if not self.gist_id:
            response = self._create_gist(file)
        else:
            response = self._update_gist(file)

        result = response.json()
        logger.info(
            "GitHub Gist operation successful: gist_id=%s, url=%s",
            result.get("id"),
            result.get("html_url"),
        )
        logger.debug(json.dumps(result, ensure_ascii=False, default=str))
        return result

    def _get_headers(self) -> dict[str, str]:
        """Get HTTP headers for GitHub API requests.

        Returns:
            Dictionary of HTTP headers including authorization.
        """
        return {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _create_gist(self, file: Path) -> httpx.Response:
        """Create a new gist on GitHub.

        Args:
            file: Path to the calendar file to upload.

        Returns:
            HTTP response from the GitHub Gist API.
        """
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()

        payload = {
            "description": self.description,
            "public": self.public,
            "files": {file.name: {"content": content}},
        }

        response = httpx.post(
            f"{self.API_BASE_URL}/gists",
            headers=self._get_headers(),
            json=payload,
            timeout=30.0,
        )
        response.raise_for_status()
        return response

    def _update_gist(self, file: Path) -> httpx.Response:
        """Update an existing gist on GitHub.

        Args:
            file: Path to the calendar file to upload.

        Returns:
            HTTP response from the GitHub Gist API.
        """
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()

        payload = {
            "description": self.description,
            "files": {file.name: {"content": content}},
        }

        response = httpx.patch(
            f"{self.API_BASE_URL}/gists/{self.gist_id}",
            headers=self._get_headers(),
            json=payload,
            timeout=30.0,
        )
        response.raise_for_status()
        return response
