#!/usr/bin/env python3
"""
notify_to_cisco_webex module

Provides the Webex client for sending messages (with optional attachments)
to Cisco Webex, and a CLI entrypoint.

Attachment behavior (summary):
- CLI usage (via --file) accepts one or more local filesystem paths (strings).
- Programmatic usage (calling Webex.send_message):
  - Accepts a list of local filesystem path strings, and/or
  - Accepts a list of objects (dicts) each with keys:
      - "filename": desired filename (string)
      - "content": base64-encoded bytes (string)
  - Accepts a single string which is a base64-encoded JSON list of the objects
    described above (useful when passing via env or other string channels).
  - For object-style attachments the client will create temporary files from the
    decoded content, attach them, and remove the temp files after the requests.

Only external dependencies:
- dotenv
- httpx
"""

from __future__ import annotations

import base64
import io
import json
import logging
import mimetypes
import os
import tempfile
from typing import Dict, List, Optional, Tuple, Union

import httpx
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class WebexError(Exception):
    """Generic error for Webex operations."""


class Webex:
    """Client for sending messages to Cisco Webex.

    Configuration priority:
      1. Constructor arguments
      2. OS environment variables
      3. .env file

    Environment variables used:
      - WEBEX_ACCESS_TOKEN
      - WEBEX_ROOM_ID
      - WEBEX_TO_EMAIL
      - WEBEX_PROXY
    """

    API_BASE = "https://webexapis.com/v1"

    def __init__(
        self,
        access_token: Optional[str] = None,
        room_id: Optional[str] = None,
        to_email: Optional[str] = None,
        proxy: Optional[str] = None,
        timeout: float = 10.0,
        verify: bool = True,
        verbose: bool = False,
    ) -> None:
        load_dotenv(override=False)

        self.access_token = access_token or os.environ.get("WEBEX_ACCESS_TOKEN")
        self.room_id = room_id or os.environ.get("WEBEX_ROOM_ID")
        self.to_email = to_email or os.environ.get("WEBEX_TO_EMAIL")
        self.proxy = proxy or os.environ.get("WEBEX_PROXY")
        self.timeout = timeout
        self.verify = verify
        self.verbose = verbose

        if not self.access_token:
            raise WebexError(
                "WEBEX access token is required (constructor arg or WEBEX_ACCESS_TOKEN env)"
            )
        if not (self.room_id or self.to_email):
            raise WebexError(
                "Either room_id or to_email must be provided (constructor arg or env)"
            )

        if self.verbose:
            logging.basicConfig()
            logger.setLevel(logging.DEBUG)

        self.headers = {"Authorization": f"Bearer {self.access_token}"}

    def _build_target_payload(self) -> Dict[str, str]:
        if self.room_id:
            return {"roomId": self.room_id}
        return {"toPersonEmail": self.to_email}  # type: ignore[return-value]

    def _normalize_files(
        self, files: Optional[Union[List[Union[str, Dict[str, str]]], str]]
    ) -> Tuple[List[str], List[str]]:
        """Normalize the files parameter into filesystem paths.

        Returns a tuple (file_paths, temp_paths) where:
          - file_paths: list of paths (strings) to be attached
          - temp_paths: subset of file_paths created temporarily and should be removed
        """
        if not files:
            return [], []

        file_paths: List[str] = []
        temp_paths: List[str] = []

        # If the caller provided a single base64-encoded JSON string, decode it.
        if isinstance(files, str):
            # The CLI passes strings as a list (action=append), so a plain string
            # here is interpreted as the programmatic base64-encoded JSON format.
            try:
                decoded = base64.b64decode(files)
                parsed = json.loads(decoded.decode("utf-8"))
            except Exception as e:
                raise WebexError(
                    f"Failed to decode base64-encoded files list: {e}"
                ) from e

            if not isinstance(parsed, list):
                raise WebexError("Decoded base64 payload is not a JSON list")

            items = parsed
        else:
            items = list(files)  # type: ignore[arg-type]

        for item in items:
            # If it's a string, treat as local filesystem path
            if isinstance(item, str):
                file_paths.append(item)
                continue

            # If it's a dict/object, expect 'filename' and 'content' (base64)
            if isinstance(item, dict):
                filename = item.get("filename") or item.get("name")
                content_b64 = item.get("content") or item.get("data")
                if not filename or not content_b64:
                    raise WebexError(
                        "File object must contain 'filename' and 'content' (base64)"
                    )
                try:
                    data = base64.b64decode(content_b64)
                except Exception as e:
                    raise WebexError(
                        f"Failed to decode base64 content for {filename}: {e}"
                    ) from e

                suffix = os.path.splitext(filename)[1]
                try:
                    tf = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                    tf.write(data)
                    tf.flush()
                    tf.close()
                    file_paths.append(tf.name)
                    temp_paths.append(tf.name)
                except OSError as e:
                    raise WebexError(
                        f"Failed to create temporary file for {filename}: {e}"
                    ) from e
                continue

            raise WebexError(
                "Unsupported file item type; must be a path string or an object with 'filename'/'content'"
            )

        return file_paths, temp_paths

    def send_message(
        self,
        message: Optional[str] = None,
        format: str = "markdown",
        files: Optional[Union[List[Union[str, Dict[str, str]]], str]] = None,
    ) -> Union[Dict, List[Dict]]:
        """Send a message to Webex with optional attachments.

        Behavior:
          - If no files provided, send a single JSON POST.
          - If files provided, send one multipart POST per file.
          - If multiple files, the message body is included only on the first POST.
        """
        fmt = (format or "markdown").lower()
        if fmt not in ("markdown", "text"):
            raise WebexError("format must be 'markdown' or 'text'")

        # Normalize files input (handles local paths and programmatic base64 objects)
        file_paths, temp_paths = self._normalize_files(files)

        try:
            if not file_paths:
                return self._post_message(message=message, format=fmt)

            results: List[Dict] = []
            for idx, fpath in enumerate(file_paths):
                send_text = message if idx == 0 else None
                resp_json = self._post_message(
                    message=send_text, format=fmt, file_path=fpath
                )
                results.append(resp_json)

            if len(results) == 1:
                return results[0]
            return results
        finally:
            # Clean up any temporary files created from base64 objects
            for p in temp_paths:
                try:
                    os.unlink(p)
                    logger.debug("Removed temporary file %s", p)
                except Exception:
                    logger.debug("Failed to remove temporary file %s", p)

    def send_message_from_dify_files_in_memory(
        self,
        message: Optional[str] = None,
        format: str = "markdown",
        dify_files: Optional[List[object]] = None,
    ) -> Union[Dict, List[Dict]]:
        """Send a message using Dify 'files' variable without writing to disk.

        This method is intended for use inside Dify plugin environments where
        writing to the local filesystem may not be permitted. It accepts the
        same kinds of entries as `send_message_from_dify_files` (objects
        exposing `.blob` or dicts with `blob`/`url`/`content`) but performs
        uploads entirely in memory using file-like objects (BytesIO). The
        semantics (one multipart POST per file, message included only on the
        first POST) mirror `send_message`.
        """
        fmt = (format or "markdown").lower()
        if fmt not in ("markdown", "text"):
            raise WebexError("format must be 'markdown' or 'text'")

        if not dify_files:
            return self.send_message(message=message, format=fmt, files=None)

        # Prepare list of (filename, data_bytes)
        items: List[Tuple[str, bytes]] = []

        for item in list(dify_files):
            data: Optional[bytes] = None
            filename: Optional[str] = None

            if hasattr(item, "blob"):
                # Dify File model instance: use its blob property (may fetch via httpx)
                try:
                    maybe_blob = getattr(item, "blob")
                    maybe_value = maybe_blob() if callable(maybe_blob) else maybe_blob
                    # Convert only known/appropriate types to bytes explicitly to avoid
                    # calling bytes() on arbitrary objects that don't implement the
                    # buffer protocol.
                    try:
                        if isinstance(maybe_value, (bytes, bytearray, memoryview)):
                            data = bytes(maybe_value)
                        elif isinstance(maybe_value, str):
                            data = maybe_value.encode("utf-8")
                        else:
                            # As a last resort, attempt bytes() but surface a clear error
                            # if the object isn't convertible.
                            try:
                                data = bytes(maybe_value)
                            except TypeError:
                                raise WebexError(
                                    f"Failed to convert blob to bytes for dify file object: unsupported type {type(maybe_value)}"
                                )
                    except WebexError:
                        # Re-raise our WebexError unchanged
                        raise
                    except Exception as e:
                        raise WebexError(
                            f"Failed to convert blob to bytes for dify file object: {e}"
                        ) from e
                except Exception as e:
                    raise WebexError(
                        f"Failed to read blob from dify file object: {e}"
                    ) from e
                filename = (
                    getattr(item, "filename", None)
                    or getattr(item, "name", None)
                    or "file"
                )
            elif isinstance(item, dict):
                # dict may contain raw bytes under 'blob', a 'url' to fetch, or base64 'content'
                if item.get("blob") is not None:
                    data = item.get("blob")
                elif item.get("url"):
                    try:
                        resp = httpx.get(item["url"])
                        resp.raise_for_status()
                        data = resp.content
                    except Exception as e:
                        raise WebexError(
                            f"Failed to fetch file from URL {item.get('url')}: {e}"
                        ) from e
                elif item.get("content"):
                    try:
                        data = base64.b64decode(item["content"])
                    except Exception as e:
                        raise WebexError(
                            f"Failed to decode base64 content for {item.get('filename') or 'file'}: {e}"
                        ) from e
                else:
                    raise WebexError(
                        "Unsupported dify file dict; expected 'blob', 'url' or 'content'"
                    )
                filename = item.get("filename") or item.get("name") or "file"
            else:
                raise WebexError(
                    "Unsupported dify file entry type; expected object with 'blob' or a dict"
                )

            if data is None:
                raise WebexError(f"No data available for file {filename or 'unknown'}")

            if isinstance(data, str):
                data_bytes = data.encode("utf-8")
            elif isinstance(data, (bytes, bytearray)):
                data_bytes = bytes(data)
            else:
                try:
                    data_bytes = bytes(data)
                except Exception as e:
                    raise WebexError(
                        f"Unsupported data type for file {filename or 'unknown'}: {type(data)}"
                    ) from e

            items.append((filename or "file", data_bytes))

        # Perform one multipart POST per file, using in-memory file objects
        url = f"{self.API_BASE}/messages"
        timeout = httpx.Timeout(self.timeout)
        client_kwargs = {
            "timeout": timeout,
            "verify": self.verify,
            "headers": self.headers,
        }
        if self.proxy:
            client_kwargs["proxies"] = self.proxy

        results: List[Dict] = []
        try:
            with httpx.Client(**client_kwargs) as client:
                for idx, (fname, data_bytes) in enumerate(items):
                    payload = self._build_target_payload()
                    send_text = message if idx == 0 else None
                    if send_text:
                        if fmt == "markdown":
                            payload["markdown"] = send_text
                        else:
                            payload["text"] = send_text

                    # form fields must be strings
                    payload_encoded = {k: str(v) for k, v in payload.items()}

                    mime_type, _ = mimetypes.guess_type(fname)
                    mime_type = mime_type or "application/octet-stream"

                    bio = io.BytesIO(data_bytes)
                    bio.seek(0)
                    files_param = {"files": (os.path.basename(fname), bio, mime_type)}

                    logger.debug(
                        "POST %s payload=%s in-memory file=%s",
                        url,
                        payload_encoded,
                        fname,
                    )
                    try:
                        resp = client.post(url, data=payload_encoded, files=files_param)
                    finally:
                        try:
                            bio.close()
                        except Exception:
                            pass

                    if resp.status_code >= 400:
                        body = None
                        try:
                            body = resp.json()
                        except Exception:
                            body = resp.text
                        raise WebexError(
                            f"Webex API returned error status {resp.status_code}: {body}"
                        )

                    try:
                        results.append(resp.json())
                    except Exception:
                        raise WebexError("Response is not valid JSON")

            if len(results) == 1:
                return results[0]
            return results
        except httpx.RequestError as e:
            raise WebexError(f"Request failed: {e}") from e

    def _post_message(
        self,
        message: Optional[str] = None,
        format: str = "markdown",
        file_path: Optional[str] = None,
    ) -> Dict:
        """Perform the HTTP POST to the Webex Messages API."""

        url = f"{self.API_BASE}/messages"
        payload = self._build_target_payload()
        if message:
            if format == "markdown":
                payload["markdown"] = message
            else:
                payload["text"] = message

        timeout = httpx.Timeout(self.timeout)
        client_kwargs = {
            "timeout": timeout,
            "verify": self.verify,
            "headers": self.headers,
        }
        if self.proxy:
            client_kwargs["proxies"] = self.proxy

        try:
            with httpx.Client(**client_kwargs) as client:
                if file_path:
                    # Ensure file exists
                    if not os.path.exists(file_path):
                        raise WebexError(f"File not found: {file_path}")

                    mime_type, _ = mimetypes.guess_type(file_path)
                    mime_type = mime_type or "application/octet-stream"
                    try:
                        with open(file_path, "rb") as f:
                            # Ensure payload values are strings to preserve encoding
                            payload_encoded = {k: str(v) for k, v in payload.items()}
                            files_param = {
                                "files": (os.path.basename(file_path), f, mime_type)
                            }
                            logger.debug(
                                "POST %s payload=%s file=%s",
                                url,
                                payload_encoded,
                                file_path,
                            )
                            resp = client.post(
                                url, data=payload_encoded, files=files_param
                            )
                    except OSError as e:
                        raise WebexError(
                            f"Failed to open/read file {file_path}: {e}"
                        ) from e
                else:
                    # Send JSON with utf-8 charset
                    logger.debug("POST %s payload=%s", url, payload)
                    headers = self.headers.copy()
                    headers["Content-Type"] = "application/json; charset=utf-8"
                    resp = client.post(url, json=payload, headers=headers)
        except httpx.RequestError as e:
            raise WebexError(f"Request failed: {e}") from e

        if resp.status_code >= 400:
            body = None
            try:
                body = resp.json()
            except Exception:
                body = resp.text
            raise WebexError(
                f"Webex API returned error status {resp.status_code}: {body}"
            )

        try:
            return resp.json()
        except Exception as e:
            raise WebexError("Response is not valid JSON") from e


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entrypoint for the module."""
    import argparse

    parser = argparse.ArgumentParser(prog="notify-to-cisco-webex")
    parser.add_argument("-t", "--token", help="Webex access token")
    parser.add_argument("-r", "--room-id", help="Webex room id")
    parser.add_argument("-e", "--to-email", help="Recipient email address")
    parser.add_argument("-m", "--message", help="Message body", default=None)
    parser.add_argument(
        "-f",
        "--format",
        help="Message format ('text' or 'markdown')",
        default="Markdown",
    )
    parser.add_argument(
        "--timeout", type=float, help="HTTP timeout in seconds", default=10.0
    )
    parser.add_argument(
        "--no-verify", action="store_true", help="Disable SSL verification"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )
    parser.add_argument("-p", "--proxy", help="HTTP proxy URL")
    parser.add_argument(
        "--file",
        action="append",
        help="File to attach. Can be specified multiple times.",
    )

    args = parser.parse_args(argv)

    fmt = (args.format or "markdown").lower()
    if fmt not in ("markdown", "text"):
        raise SystemExit(2)

    try:
        client = Webex(
            access_token=args.token,
            room_id=args.room_id,
            to_email=args.to_email,
            proxy=args.proxy,
            timeout=args.timeout,
            verify=not args.no_verify,
            verbose=args.verbose,
        )
    except WebexError as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        return 2

    try:
        result = client.send_message(message=args.message, format=fmt, files=args.file)
    except WebexError as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        return 3

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
