# tests/test_attachments.py

import base64
import json
import os
from typing import Any, Dict, List, Optional, Tuple

import httpx
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
        return json.dumps(self._payload)


class FakeClient:
    """
    A minimal stand-in for `httpx.Client` that records `post` calls.

    Usage:
        - Instantiate with a shared `posts` list that will collect tuples of:
          (url, data, json, headers, files)
        - Act as a context manager (used with `with httpx.Client(...) as client:`)
    """

    def __init__(self, posts: List[Tuple], *args, **kwargs) -> None:
        # posts is a list provided by the tests to capture calls
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
        # Record the call
        # Normalize recorded files to contain only the basename of the uploaded file
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
        # Return a simple success response. If file was present include its name.
        payload = {"ok": True}
        if recorded_files:
            payload["file"] = recorded_files[0]
        return FakeResponse(200, payload)


@pytest.fixture
def fake_client_factory(monkeypatch):
    """
    Fixture that patches httpx.Client to our FakeClient that captures posts.
    Yields the list that will contain recorded post calls so tests can inspect it.
    """
    posts: List[Dict[str, Any]] = []

    def _factory(*args, **kwargs):
        # Return a new FakeClient bound to the shared posts list
        return FakeClient(posts, *args, **kwargs)

    monkeypatch.setattr(httpx, "Client", _factory)
    return posts


def test_send_local_files_multiple_posts_and_message_only_first(
    tmp_path, fake_client_factory
):
    # Prepare two local files
    f1 = tmp_path / "one.txt"
    f2 = tmp_path / "two.txt"
    f1.write_bytes(b"first")
    f2.write_bytes(b"second")

    client = Webex(access_token="token", room_id="room")
    result = client.send_message(
        message="hello", format="markdown", files=[str(f1), str(f2)]
    )

    # Ensure two posts were made
    posts = fake_client_factory
    assert len(posts) == 2

    # First post should contain 'data' (multipart) with message included as payload
    first = posts[0]
    assert first["files"] is not None
    assert first["files"][0] == os.path.basename(str(f1))
    # For file uploads, the code uses 'data' for form fields; markdown should be present there
    assert first["data"] is not None and "markdown" in first["data"]
    assert first["data"]["markdown"] == "hello"

    # Second post should not include the message body
    second = posts[1]
    assert second["files"] is not None
    assert second["files"][0] == os.path.basename(str(f2))
    # The subsequent posts shouldn't include 'markdown' in data
    assert second["data"] is not None
    assert "markdown" not in second["data"]


def test_send_base64_object_list_as_list_of_dicts(fake_client_factory):
    # Prepare two objects with filename/content (content is base64)
    obj1 = {"filename": "a.txt", "content": base64.b64encode(b"alpha").decode("utf-8")}
    obj2 = {"filename": "b.txt", "content": base64.b64encode(b"beta").decode("utf-8")}

    client = Webex(access_token="token", room_id="room")
    result = client.send_message(message="hi", format="text", files=[obj1, obj2])

    posts = fake_client_factory
    assert len(posts) == 2
    assert posts[0]["files"][0] == "a.txt"
    assert posts[1]["files"][0] == "b.txt"
    # For text format the message should be placed under 'text' field in payload data
    assert posts[0]["data"] is not None and "text" in posts[0]["data"]
    assert posts[0]["data"]["text"] == "hi"
    assert "text" not in posts[1]["data"] or posts[1]["data"].get("text") in (
        "None",
        None,
    )


def test_send_base64_object_list_as_base64_encoded_json_str(fake_client_factory):
    # Create the same objects, but pass them as a base64-encoded JSON string
    objs = [
        {"filename": "x.txt", "content": base64.b64encode(b"xxx").decode("utf-8")},
        {"filename": "y.bin", "content": base64.b64encode(b"\x01\x02").decode("utf-8")},
    ]
    encoded = base64.b64encode(json.dumps(objs).encode("utf-8")).decode("utf-8")

    client = Webex(access_token="token", room_id="room")
    result = client.send_message(message="m", format="markdown", files=encoded)

    posts = fake_client_factory
    assert len(posts) == 2
    assert posts[0]["files"][0] == "x.txt"
    assert posts[1]["files"][0] == "y.bin"
    # Ensure first post carried the message
    assert posts[0]["data"] is not None and "markdown" in posts[0]["data"]
    assert posts[0]["data"]["markdown"] == "m"
