# Tests for notify_to_cisco_webex.Webex client.
#
# These tests mock httpx.Client to avoid real network calls and validate
# behavior required by the project specification.
#
# Docstrings and comments are in English and use Google-style where applicable.

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import pytest

from notify_to_cisco_webex.notify_to_cisco_webex import Webex, WebexError


class DummyResponse:
    """A minimal fake httpx.Response-like object for testing."""

    def __init__(self, status_code: int, data: Any):
        self.status_code = status_code
        self._data = data

    def json(self) -> Any:
        """Return JSON-serializable data."""
        return self._data

    @property
    def text(self) -> str:
        """Return a text representation of the response body."""
        try:
            return json.dumps(self._data)
        except Exception:
            return str(self._data)


class DummyClient:
    """A fake httpx.Client that records requests and returns DummyResponse.

    Enhancements:
    - Accepts `json` and `headers` kwargs (to match httpx.Client.post signature used
      by the module after UTF-8 fixes).
    - Registers created instances in `DummyClient.instances` so tests can inspect the
      last client used.
    """

    instances: List["DummyClient"] = []

    def __init__(self, *args, **kwargs):
        self.posts: List[Dict[str, Any]] = []
        DummyClient.instances.append(self)

    def post(
        self,
        url: str,
        data: Optional[Dict] = None,
        files: Optional[Dict] = None,
        json: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ):
        """Record the call and return a successful dummy response."""
        # Record all provided parameters so tests can assert on encoding/path used.
        record = {
            "url": url,
            "data": data,
            "files": files,
            "json": json,
            "headers": headers,
        }
        self.posts.append(record)
        # Return a JSON payload similar to Webex messages API
        return DummyResponse(200, {"id": "dummy-id", "created": True})

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        # Do not suppress exceptions
        return False


def test_missing_token_and_env(monkeypatch):
    """When no access token is provided via constructor or environment, raise WebexError."""
    monkeypatch.delenv("WEBEX_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("WEBEX_ROOM_ID", raising=False)
    monkeypatch.delenv("WEBEX_TO_EMAIL", raising=False)

    with pytest.raises(WebexError):
        Webex()


def test_missing_target(monkeypatch):
    """When token exists but neither room_id nor to_email is provided, raise WebexError."""
    monkeypatch.setenv("WEBEX_ACCESS_TOKEN", "token")
    monkeypatch.delenv("WEBEX_ROOM_ID", raising=False)
    monkeypatch.delenv("WEBEX_TO_EMAIL", raising=False)

    with pytest.raises(WebexError):
        Webex()


def test_send_plain_message(monkeypatch):
    """Sending a plain message (no files) should return the parsed JSON response (dict)."""
    monkeypatch.setenv("WEBEX_ACCESS_TOKEN", "token")
    monkeypatch.setenv("WEBEX_TO_EMAIL", "to@example.com")

    # Patch httpx.Client used in the module to our dummy implementation
    monkeypatch.setattr(
        "notify_to_cisco_webex.notify_to_cisco_webex.httpx.Client", DummyClient
    )

    client = Webex()
    resp = client.send_message(message="hello", format="text")
    assert isinstance(resp, dict)
    assert resp.get("id") == "dummy-id"
    assert resp.get("created") is True


def test_send_with_files(monkeypatch, tmp_path):
    """When multiple files are provided, the client should send one request per file."""
    monkeypatch.setenv("WEBEX_ACCESS_TOKEN", "token")
    monkeypatch.setenv("WEBEX_ROOM_ID", "room123")

    # Create two test files
    f1 = tmp_path / "1.txt"
    f1.write_text("one")
    f2 = tmp_path / "2.txt"
    f2.write_text("two")

    # Patch httpx.Client to DummyClient
    monkeypatch.setattr(
        "notify_to_cisco_webex.notify_to_cisco_webex.httpx.Client", DummyClient
    )

    client = Webex()
    result = client.send_message(
        message="hi", format="markdown", files=[str(f1), str(f2)]
    )

    # Because two files were provided, the result should be a list of responses
    assert isinstance(result, list)
    assert len(result) == 2
    for item in result:
        assert isinstance(item, dict)
        assert item.get("id") == "dummy-id"


def test_send_single_file_returns_dict(monkeypatch, tmp_path):
    """When a single file is provided, convenience return value should be a dict (not list)."""
    monkeypatch.setenv("WEBEX_ACCESS_TOKEN", "token")
    monkeypatch.setenv("WEBEX_ROOM_ID", "room123")

    f1 = tmp_path / "single.txt"
    f1.write_text("payload")

    monkeypatch.setattr(
        "notify_to_cisco_webex.notify_to_cisco_webex.httpx.Client", DummyClient
    )

    client = Webex()
    resp = client.send_message(message="one file", format="markdown", files=[str(f1)])
    assert isinstance(resp, dict)
    assert resp.get("id") == "dummy-id"


def test_file_not_found(monkeypatch):
    """If an attached file path does not exist, raise WebexError."""
    monkeypatch.setenv("WEBEX_ACCESS_TOKEN", "token")
    monkeypatch.setenv("WEBEX_ROOM_ID", "room123")
    monkeypatch.setenv("WEBEX_TO_EMAIL", "to@example.com")

    # Ensure httpx.Client is patched even though code should error before network call
    monkeypatch.setattr(
        "notify_to_cisco_webex.notify_to_cisco_webex.httpx.Client", DummyClient
    )

    client = Webex()
    with pytest.raises(WebexError):
        client.send_message(message="hi", files=["/nonexistent/file.txt"])


def test_send_japanese_plain_message(monkeypatch):
    """Sending a plain Japanese message (no files) should be encoded as UTF-8 in JSON and headers."""
    monkeypatch.setenv("WEBEX_ACCESS_TOKEN", "token")
    monkeypatch.setenv("WEBEX_TO_EMAIL", "to@example.com")

    # Patch httpx.Client to our enhanced DummyClient
    monkeypatch.setattr(
        "notify_to_cisco_webex.notify_to_cisco_webex.httpx.Client", DummyClient
    )

    client = Webex()
    message = "こんにちは、世界"  # Japanese for "Hello, world"
    resp = client.send_message(message=message, format="markdown")
    assert isinstance(resp, dict)
    assert resp.get("id") == "dummy-id"

    # Inspect the last DummyClient instance and its recorded posts
    last_client = DummyClient.instances[-1]
    assert len(last_client.posts) >= 1
    post = last_client.posts[0]
    # The module sends JSON body for non-file messages
    assert post.get("json") is not None
    assert post["json"].get("toPersonEmail") == "to@example.com"
    assert post["json"].get("markdown") == message
    # Headers should include charset utf-8
    headers = post.get("headers") or {}
    content_type = headers.get("Content-Type", "")
    assert "charset=utf-8" in content_type.lower()


def test_send_japanese_with_file(monkeypatch, tmp_path):
    """Sending a Japanese message together with a file should include the text as a form field (strings)."""
    monkeypatch.setenv("WEBEX_ACCESS_TOKEN", "token")
    monkeypatch.setenv("WEBEX_ROOM_ID", "room-jp")

    # Create a test file
    f1 = tmp_path / "jp.txt"
    f1.write_text("ファイル内容")  # some japanese content

    monkeypatch.setattr(
        "notify_to_cisco_webex.notify_to_cisco_webex.httpx.Client", DummyClient
    )

    client = Webex()
    message = "日本語のメッセージ"
    resp = client.send_message(message=message, format="markdown", files=[str(f1)])
    assert isinstance(resp, dict)
    assert resp.get("id") == "dummy-id"

    last_client = DummyClient.instances[-1]
    assert len(last_client.posts) >= 1
    post = last_client.posts[0]
    # For file uploads, the module sends 'data' for form fields and 'files' for file tuple
    assert post.get("data") is not None
    # payload keys should include roomId and markdown
    assert post["data"].get("roomId") == "room-jp"
    assert post["data"].get("markdown") == message
    # files should be present and contain the basename as first element of tuple
    files_param = post.get("files")
    assert files_param is not None
    # Depending on httpx behavior we expect a mapping with 'files' key
    assert "files" in files_param
    assert files_param["files"][0] == os.path.basename(str(f1))
