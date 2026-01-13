"""WebDAV Upload - Upload ODS files to Nextcloud via WebDAV.

Provides secure file upload to Nextcloud servers using WebDAV protocol.
"""

from __future__ import annotations

import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

import requests
from requests.auth import HTTPBasicAuth


@dataclass
class NextcloudConfig:
    """Configuration for Nextcloud WebDAV connection."""

    server_url: str  # Base URL, e.g., "https://nextcloud.example.com"
    username: str
    password: str  # App password recommended
    remote_path: str = "/Finance"  # Path within Nextcloud

    @classmethod
    def from_env(cls) -> NextcloudConfig:
        """Create config from environment variables.

        Environment variables:
            NEXTCLOUD_URL: Server base URL
            NEXTCLOUD_USER: Username
            NEXTCLOUD_PASSWORD: Password or app password
            NEXTCLOUD_PATH: Remote path (optional, defaults to /Finance)
        """
        url = os.environ.get("NEXTCLOUD_URL")
        user = os.environ.get("NEXTCLOUD_USER")
        password = os.environ.get("NEXTCLOUD_PASSWORD")
        path = os.environ.get("NEXTCLOUD_PATH", "/Finance")

        if not all([url, user, password]):
            raise ValueError(
                "Missing required environment variables: "
                "NEXTCLOUD_URL, NEXTCLOUD_USER, NEXTCLOUD_PASSWORD"
            )

        # All values guaranteed non-None by validation above
        assert url is not None
        assert user is not None
        assert password is not None

        return cls(
            server_url=url,
            username=user,
            password=password,
            remote_path=path,
        )


class WebDAVClient:
    """WebDAV client for Nextcloud file operations.

    Supports uploading, listing, and managing files on Nextcloud
    via the WebDAV protocol.
    """

    def __init__(self, config: NextcloudConfig) -> None:
        """Initialize WebDAV client.

        Args:
            config: Nextcloud connection configuration.
        """
        self.config = config
        self._session = requests.Session()
        self._session.auth = HTTPBasicAuth(config.username, config.password)
        self._session.headers.update(
            {
                "User-Agent": "spreadsheet-dl/0.1.0",
            }
        )

    @property
    def webdav_url(self) -> str:
        """Get the WebDAV base URL."""
        base = self.config.server_url.rstrip("/")
        return f"{base}/remote.php/dav/files/{self.config.username}"

    def _build_url(self, remote_path: str) -> str:
        """Build full WebDAV URL for a remote path."""
        # Ensure path starts with /
        if not remote_path.startswith("/"):
            remote_path = f"/{remote_path}"
        # URL-encode the path components
        encoded_path = "/".join(quote(part, safe="") for part in remote_path.split("/"))
        return f"{self.webdav_url}{encoded_path}"

    def upload_file(
        self,
        local_path: Path | str,
        remote_path: str | None = None,
        create_dirs: bool = True,
    ) -> str:
        """Upload a file to Nextcloud.

        Args:
            local_path: Path to local file.
            remote_path: Remote path (defaults to config.remote_path + filename).
            create_dirs: Create parent directories if they don't exist.

        Returns:
            Remote URL of uploaded file.

        Raises:
            FileNotFoundError: If local file doesn't exist.
            PermissionError: If upload fails due to permissions.
            ConnectionError: If connection to server fails.
        """
        local_path = Path(local_path)
        if not local_path.exists():
            raise FileNotFoundError(f"Local file not found: {local_path}")

        # Build remote path
        if remote_path is None:
            remote_path = f"{self.config.remote_path}/{local_path.name}"
        elif not remote_path.startswith("/"):
            remote_path = f"{self.config.remote_path}/{remote_path}"

        # Create parent directories if needed
        if create_dirs:
            parent_path = "/".join(remote_path.split("/")[:-1])
            if parent_path:
                self._ensure_directory(parent_path)

        # Upload file
        url = self._build_url(remote_path)
        with open(local_path, "rb") as f:
            response = self._session.put(url, data=f)

        if response.status_code == 401:
            raise PermissionError("Authentication failed. Check credentials.")
        elif response.status_code == 403:
            raise PermissionError(f"Permission denied for: {remote_path}")
        elif response.status_code == 507:
            raise OSError("Insufficient storage on server")
        elif response.status_code not in (200, 201, 204):
            raise ConnectionError(
                f"Upload failed with status {response.status_code}: {response.text}"
            )

        return url

    def _ensure_directory(self, remote_path: str) -> None:
        """Create directory and parents if they don't exist."""
        parts = remote_path.strip("/").split("/")
        current_path = ""

        for part in parts:
            if not part:
                continue
            current_path = f"{current_path}/{part}"
            url = self._build_url(current_path)

            # Check if exists
            response = self._session.request("PROPFIND", url, headers={"Depth": "0"})
            if response.status_code == 404:
                # Create directory
                response = self._session.request("MKCOL", url)
                if response.status_code not in (201, 405):  # 405 = already exists
                    raise ConnectionError(f"Failed to create directory: {current_path}")

    def list_files(self, remote_path: str | None = None) -> list[str]:
        """List files in a remote directory.

        Args:
            remote_path: Directory path (defaults to config.remote_path).

        Returns:
            List of file names in the directory.
        """
        if remote_path is None:
            remote_path = self.config.remote_path

        url = self._build_url(remote_path)
        response = self._session.request(
            "PROPFIND",
            url,
            headers={"Depth": "1"},
        )

        if response.status_code == 404:
            return []
        elif response.status_code != 207:
            raise ConnectionError(f"Failed to list directory: {response.status_code}")

        # Parse response (simple extraction)
        files = []

        try:
            root = ET.fromstring(response.text)
            for href in root.iter("{DAV:}href"):
                path = href.text
                if path and not path.endswith("/"):
                    # Extract filename
                    name = path.split("/")[-1]
                    if name:
                        files.append(name)
        except ET.ParseError:
            pass

        return files

    def file_exists(self, remote_path: str) -> bool:
        """Check if a file exists on the server."""
        url = self._build_url(remote_path)
        response = self._session.head(url)
        return response.status_code == 200

    def delete_file(self, remote_path: str) -> bool:
        """Delete a file from the server.

        Args:
            remote_path: Path to file to delete.

        Returns:
            True if deleted, False if file didn't exist.
        """
        url = self._build_url(remote_path)
        response = self._session.delete(url)
        return response.status_code in (200, 204)

    def download_file(
        self,
        remote_path: str,
        local_path: Path | str,
    ) -> Path:
        """Download a file from the server.

        Args:
            remote_path: Path to remote file.
            local_path: Local path to save file.

        Returns:
            Path to downloaded file.
        """
        local_path = Path(local_path)
        url = self._build_url(remote_path)

        response = self._session.get(url, stream=True)
        if response.status_code == 404:
            raise FileNotFoundError(f"Remote file not found: {remote_path}")
        elif response.status_code != 200:
            raise ConnectionError(f"Download failed: {response.status_code}")

        local_path.parent.mkdir(parents=True, exist_ok=True)
        with open(local_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return local_path

    def test_connection(self) -> bool:
        """Test connection to Nextcloud server.

        Returns:
            True if connection successful, False otherwise.
        """
        try:
            response = self._session.request(
                "PROPFIND",
                self.webdav_url,
                headers={"Depth": "0"},
            )
            return response.status_code == 207
        except requests.RequestException:
            return False


def upload_budget(
    local_path: Path | str,
    config: NextcloudConfig | None = None,
) -> str:
    """Convenience function to upload a budget file to Nextcloud.

    Args:
        local_path: Path to local ODS file.
        config: Nextcloud config (defaults to env vars).

    Returns:
        Remote URL of uploaded file.
    """
    if config is None:
        config = NextcloudConfig.from_env()

    client = WebDAVClient(config)
    return client.upload_file(local_path)
