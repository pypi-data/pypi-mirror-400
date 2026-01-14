# tests/test_dify_files.py

import base64
import os
from typing import Any, Dict, List, Optional, Tuple

import pytest

from notify_to_cisco_webex.notify_to_cisco_webex import Webex, WebexError


class FakeResponse:
    def __init__(self, status_code: int, payload: Dict[str, Any]) -> None:
        self.status_code = status_code
        self._payload = payload

    def json(self) -> Dict[str, Any]:
        return self._payload

    @property
    def text(self) -> str:
        return str(self._payload)


class FakeClient:
    """
    Minimal stand-in for `httpx.Client` used by the module.

    It records post calls into a shared list supplied at construction time.
    Each recorded entry is a dict containing keys: url, data, json, headers, files.
    The 'files' entry is normalized to (basename, mime) when available.
    """

    def __init__(self, posts: List[Dict[str, Any]], *args, **kwargs) -> None:
        self._posts = posts
        self._args = args
        self._kwargs = kwargs

    def __enter__(self) -> "FakeClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def post(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        files: Optional[Dict[str, Tuple[str, Any, str]]] = None,
        **kwargs,
    ) -> FakeResponse:
        recorded_files = None
        if files and "files" in files:
            f = files["files"]
            # f is expected to be tuple (basename, fileobj, mime)
            recorded_files = (f[0], f[2])
        self._posts.append(
            {
                "url": url,
                "data": data,
                "json": json,
                "headers": headers,
                "files": recorded_files,
            }
        )
        payload = {"ok": True}
        if recorded_files:
            payload["file"] = recorded_files[0]
        return FakeResponse(200, payload)


def _patch_httpx_client(monkeypatch, posts: List[Dict[str, Any]]):
    """
    Monkeypatch the httpx.Client used by the module to our FakeClient.
    The factory returns a new FakeClient bound to the shared `posts` list.
    """

    def _factory(*args, **kwargs):
        return FakeClient(posts, *args, **kwargs)

    # Patch the httpx.Client used inside the module
    monkeypatch.setattr(
        "notify_to_cisco_webex.notify_to_cisco_webex.httpx.Client", _factory
    )


class DummyHTTPGetResponse:
    def __init__(self, content: bytes, status: int = 200):
        self.content = content
        self._status = status

    def raise_for_status(self):
        if not (200 <= self._status < 300):
            raise RuntimeError(f"HTTP status {self._status}")


def test_send_from_dify_file_objects_in_memory(monkeypatch):
    """send_message_from_dify_files_in_memory accepts objects with a `blob` property."""
    monkeypatch.setenv("WEBEX_ACCESS_TOKEN", "token")
    monkeypatch.setenv("WEBEX_ROOM_ID", "room-dify-obj")

    posts: List[Dict[str, Any]] = []
    _patch_httpx_client(monkeypatch, posts)

    class DifyFile:
        def __init__(self, filename: str, data: bytes):
            self.filename = filename
            self._data = data

        @property
        def blob(self) -> bytes:
            # Emulate Dify File model exposing `blob` property
            return self._data

    f1 = DifyFile("alpha.txt", b"alpha-content")
    f2 = DifyFile("beta.jpg", b"\xff\xd8\xff")

    client = Webex(access_token="token", room_id="room-dify-obj")
    result = client.send_message_from_dify_files_in_memory(
        message="dify hello", format="markdown", dify_files=[f1, f2]
    )

    # Two posts should have been made (one per file)
    assert len(posts) == 2

    first = posts[0]
    second = posts[1]

    assert first["files"] is not None
    assert first["files"][0] == "alpha.txt"
    assert second["files"] is not None
    assert second["files"][0] == "beta.jpg"

    # Message should be included only in the first multipart POST (form fields)
    assert first["data"] is not None and "markdown" in first["data"]
    assert first["data"]["markdown"] == "dify hello"
    assert second["data"] is not None
    assert "markdown" not in second["data"]


def test_send_from_dify_dicts_with_url_and_base64_in_memory(monkeypatch):
    """send_message_from_dify_files_in_memory accepts dicts with 'url' and base64 'content'."""
    monkeypatch.setenv("WEBEX_ACCESS_TOKEN", "token")
    monkeypatch.setenv("WEBEX_ROOM_ID", "room-dify-dict")

    posts: List[Dict[str, Any]] = []
    _patch_httpx_client(monkeypatch, posts)

    # Patch the httpx.get used in the module to return predictable content
    def fake_get(url: str):
        if url == "http://example.test/x.txt":
            return DummyHTTPGetResponse(b"xxxx")
        raise RuntimeError("unknown url")

    monkeypatch.setattr(
        "notify_to_cisco_webex.notify_to_cisco_webex.httpx.get", fake_get
    )

    dict_url = {"url": "http://example.test/x.txt", "filename": "x.txt"}
    dict_b64 = {
        "filename": "y.bin",
        "content": base64.b64encode(b"\x01\x02\x03").decode("utf-8"),
    }

    client = Webex(access_token="token", room_id="room-dify-dict")
    result = client.send_message_from_dify_files_in_memory(
        message="files via dicts", format="markdown", dify_files=[dict_url, dict_b64]
    )

    assert len(posts) == 2
    assert posts[0]["files"] is not None
    assert posts[0]["files"][0] == "x.txt"
    assert posts[1]["files"] is not None
    assert posts[1]["files"][0] == "y.bin"
    assert posts[0]["data"] is not None and "markdown" in posts[0]["data"]
    assert posts[0]["data"]["markdown"] == "files via dicts"
