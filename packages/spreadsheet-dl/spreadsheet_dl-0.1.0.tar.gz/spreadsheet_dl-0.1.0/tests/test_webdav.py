"""Tests for WebDAV upload functionality."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest

from spreadsheet_dl.webdav_upload import (
    NextcloudConfig,
    WebDAVClient,
)

if TYPE_CHECKING:
    from pathlib import Path


pytestmark = [pytest.mark.integration]


class TestNextcloudConfig:
    """Tests for NextcloudConfig."""

    def test_create_config(self) -> None:
        """Test creating config directly."""
        config = NextcloudConfig(
            server_url="https://nextcloud.example.com",
            username="testuser",
            password="testpass",
            remote_path="/Finance",
        )

        assert config.server_url == "https://nextcloud.example.com"
        assert config.username == "testuser"
        assert config.remote_path == "/Finance"

    def test_from_env(self) -> None:
        """Test creating config from environment."""
        with patch.dict(
            os.environ,
            {
                "NEXTCLOUD_URL": "https://test.example.com",
                "NEXTCLOUD_USER": "envuser",
                "NEXTCLOUD_PASSWORD": "envpass",
                "NEXTCLOUD_PATH": "/CustomPath",
            },
        ):
            config = NextcloudConfig.from_env()

            assert config.server_url == "https://test.example.com"
            assert config.username == "envuser"
            assert config.remote_path == "/CustomPath"

    def test_from_env_missing_vars(self) -> None:
        """Test that missing env vars raise error."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove variables if they exist
            for var in ["NEXTCLOUD_URL", "NEXTCLOUD_USER", "NEXTCLOUD_PASSWORD"]:
                os.environ.pop(var, None)

            with pytest.raises(ValueError):
                NextcloudConfig.from_env()

    def test_default_remote_path(self) -> None:
        """Test default remote path."""
        config = NextcloudConfig(
            server_url="https://test.com",
            username="user",
            password="pass",
        )

        assert config.remote_path == "/Finance"


class TestWebDAVClient:
    """Tests for WebDAVClient."""

    @pytest.fixture
    def config(self) -> NextcloudConfig:
        """Create test config."""
        return NextcloudConfig(
            server_url="https://nextcloud.example.com",
            username="testuser",
            password="testpass",
        )

    @pytest.fixture
    def client(self, config: NextcloudConfig) -> WebDAVClient:
        """Create test client."""
        return WebDAVClient(config)

    def test_webdav_url(self, client: WebDAVClient) -> None:
        """Test WebDAV URL construction."""
        url = client.webdav_url
        assert "nextcloud.example.com" in url
        assert "remote.php/dav/files" in url
        assert "testuser" in url

    def test_build_url(self, client: WebDAVClient) -> None:
        """Test building full WebDAV URLs."""
        url = client._build_url("/Finance/budget.ods")
        assert "Finance" in url
        assert "budget.ods" in url

    def test_upload_file_not_found(
        self,
        client: WebDAVClient,
        tmp_path: Path,
    ) -> None:
        """Test upload with non-existent file."""
        with pytest.raises(FileNotFoundError):
            client.upload_file(tmp_path / "nonexistent.ods")

    @patch("requests.Session.put")
    @patch("requests.Session.request")
    def test_upload_file_success(
        self,
        mock_request: MagicMock,
        mock_put: MagicMock,
        client: WebDAVClient,
        tmp_path: Path,
    ) -> None:
        """Test successful file upload."""
        # Create test file
        test_file = tmp_path / "test.ods"
        test_file.write_text("test content")

        # Mock responses
        mock_request.return_value = MagicMock(status_code=207)  # PROPFIND
        mock_put.return_value = MagicMock(status_code=201)  # PUT

        url = client.upload_file(test_file)
        assert "test.ods" in url

    @patch("requests.Session.request")
    def test_test_connection(
        self,
        mock_request: MagicMock,
        client: WebDAVClient,
    ) -> None:
        """Test connection test."""
        mock_request.return_value = MagicMock(status_code=207)

        result = client.test_connection()
        assert result is True

    @patch("requests.Session.request")
    def test_test_connection_failure(
        self,
        mock_request: MagicMock,
        client: WebDAVClient,
    ) -> None:
        """Test connection test failure."""
        mock_request.return_value = MagicMock(status_code=401)

        result = client.test_connection()
        assert result is False

    @patch("requests.Session.request")
    def test_list_files(
        self,
        mock_request: MagicMock,
        client: WebDAVClient,
    ) -> None:
        """Test listing files."""
        # Mock PROPFIND response
        xml_response = """<?xml version="1.0"?>
        <d:multistatus xmlns:d="DAV:">
            <d:response>
                <d:href>/remote.php/dav/files/testuser/Finance/budget.ods</d:href>
            </d:response>
        </d:multistatus>
        """
        mock_request.return_value = MagicMock(
            status_code=207,
            text=xml_response,
        )

        files = client.list_files("/Finance")
        assert "budget.ods" in files

    @patch("requests.Session.head")
    def test_file_exists(
        self,
        mock_head: MagicMock,
        client: WebDAVClient,
    ) -> None:
        """Test checking if file exists."""
        mock_head.return_value = MagicMock(status_code=200)

        assert client.file_exists("/Finance/budget.ods") is True

        mock_head.return_value = MagicMock(status_code=404)
        assert client.file_exists("/Finance/nonexistent.ods") is False

    @patch("requests.Session.delete")
    def test_delete_file(
        self,
        mock_delete: MagicMock,
        client: WebDAVClient,
    ) -> None:
        """Test deleting a file."""
        mock_delete.return_value = MagicMock(status_code=204)

        result = client.delete_file("/Finance/old.ods")
        assert result is True

    @patch("requests.Session.get")
    def test_download_file(
        self,
        mock_get: MagicMock,
        client: WebDAVClient,
        tmp_path: Path,
    ) -> None:
        """Test downloading a file."""
        mock_get.return_value = MagicMock(
            status_code=200,
            iter_content=lambda chunk_size: [b"test content"],
        )

        local_path = tmp_path / "downloaded.ods"
        result = client.download_file("/Finance/budget.ods", local_path)

        assert result == local_path
        # File should exist (mock content written)
