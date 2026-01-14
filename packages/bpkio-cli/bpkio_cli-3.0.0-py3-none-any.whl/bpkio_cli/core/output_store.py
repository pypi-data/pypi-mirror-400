import json
import os
import re
from datetime import datetime, timezone
from importlib.metadata import version
from urllib.parse import parse_qs, urlparse

import click
import requests
from bpkio_api.models.common import BaseResource
from bpkio_cli.utils.strings import strip_ansi
from pydantic import HttpUrl


class OutputStore:
    """
    Lazy output store that materializes its output bundle folder only when something
    is actually written.

    Instances can act as "pointers" to sub-folders within the same output bundle.
    Use `subfolder(...)` to create nested pointers; all pointers share the same
    root bundle directory (bic-outputs-*), and the same resource.json (created once).
    """

    def __init__(
        self,
        output_directory: str | None = None,
        *,
        bundle_prefix: str = "bic-outputs",
    ):
        self._base_dir = output_directory or os.getcwd()
        datetime_str = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        self._bundle_name = f"{bundle_prefix}-{datetime_str}"

        # Pointer state
        self._rel_parts: tuple[str, ...] = ()
        self._root: "OutputStore" = self
        self._root_materialized = False

        # Per-pointer request index (keeps request_1.. in each pointer folder)
        self._request_index = 0

    def path(self, *, ensure: bool = False) -> str:
        """Return the current pointer folder path; optionally ensure it exists."""
        if ensure:
            self._ensure_folder()
        return self.folder

    def subfolder(self, *sub_folders: str) -> "OutputStore":
        """Create a new OutputStore pointer to a sub-folder under the same root."""
        sub_folders = tuple(s for s in sub_folders if s)
        child = OutputStore.__new__(OutputStore)
        child._base_dir = self._root._base_dir
        child._bundle_name = self._root._bundle_name
        child._root = self._root
        child._rel_parts = self._rel_parts + sub_folders
        child._root_materialized = False  # unused for children, but keep attribute
        child._request_index = 0
        return child

    @property
    def root_folder(self) -> str:
        """Top-level output bundle folder (bic-support-*), regardless of pointer depth."""
        return os.path.join(self._base_dir, self._bundle_name)

    @property
    def folder(self) -> str:
        """Current pointer folder (root_folder + relative parts)."""
        return os.path.join(self.root_folder, *self._rel_parts)

    def _ensure_folder(self) -> None:
        """Materialize the root bundle folder + resource.json once, then pointer folder."""
        root = self._root
        if not root._root_materialized:
            os.makedirs(root.root_folder, exist_ok=True)
            root._save_resource_info()
            root._root_materialized = True
        os.makedirs(self.folder, exist_ok=True)

    def _extract_resource_metadata(self):
        """Extract metadata from the current resource for storage in resource.json"""
        metadata = {
            "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }

        try:
            ctx = click.get_current_context()
            if res := ctx.obj.current_resource:
                if isinstance(res, BaseResource):
                    metadata["resource_type"] = res.__class__.__name__
                    metadata["resource_id"] = res.id
                    # Include name if available
                    if hasattr(res, "name"):
                        metadata["resource_name"] = res.name
                elif isinstance(res, HttpUrl):
                    metadata["url"] = str(res)
        except Exception:
            # If we can't get the resource, just leave metadata with timestamp
            pass

        return metadata

    def _save_resource_info(self):
        """Save resource.json file with resource information in the root folder."""
        metadata = self._extract_resource_metadata()
        resource_json_path = os.path.join(self.root_folder, "resource.json")
        with open(resource_json_path, "w") as f:
            f.write(json.dumps(metadata, indent=2))

    def save_text(self, filename: str, content: str):
        self._ensure_folder()
        with open(os.path.join(self.folder, filename), "w") as f:
            f.write(content)

    def append_text(self, filename: str, content: str, new_line: bool = True):
        self._ensure_folder()
        file_path = os.path.join(self.folder, filename)
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                pass
        with open(file_path, "a") as f:
            f.write(strip_ansi(content) + "\n" if new_line else content)

    def save_request_response(
        self,
        response: requests.Response,
        extension: str = ".body",
        excerpts: dict = {},
    ):
        basename = f"request_{self._request_index + 1}"
        self._request_index += 1

        self.save_text(f"{basename}.body{extension}", response.text)

        # request and response as JSON
        exchange = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "request": {
                "url": response.request.url,
                "headers": dict(response.request.headers),
            },
            "response": {
                "status_code": response.status_code,
                "reason": response.reason,
                "headers": dict(response.headers),
                # "body": r.text,
            },
            "excerpts": excerpts,
            "elapsed_ms": int(response.elapsed.total_seconds() * 1000),
        }

        self.save_text(f"{basename}.json", json.dumps(exchange, indent=4))

    def _process_request_to_har_entry(self, index: int, json_path: str, body_path: str):
        """Process a single request/response pair and convert it to a HAR entry.

        Args:
            index: The request index number
            json_path: Path to the JSON exchange file
            body_path: Path to the response body file

        Returns:
            A HAR entry dictionary, or None if processing fails
        """
        # Read JSON file
        try:
            with open(json_path, "r") as f:
                exchange = json.load(f)
        except (json.JSONDecodeError, IOError):
            return None  # Skip corrupted JSON files

        # Read body file
        try:
            with open(body_path, "r", encoding="utf-8") as f:
                body_content = f.read()
        except UnicodeDecodeError:
            # Try reading as binary and skip if not decodable
            try:
                with open(body_path, "rb") as f:
                    body_bytes = f.read()
                body_content = body_bytes.decode("utf-8")
            except (UnicodeDecodeError, IOError):
                return None  # Skip binary files that can't be decoded
        except IOError:
            return None  # Skip if file can't be read

        # Parse URL to extract query string
        url = exchange["request"]["url"]
        parsed_url = urlparse(url)
        query_string = []
        if parsed_url.query:
            parsed_qs = parse_qs(parsed_url.query)
            for name, values in parsed_qs.items():
                for value in values:
                    query_string.append({"name": name, "value": value})

        # Convert headers to HAR format
        request_headers = [
            {"name": name, "value": value}
            for name, value in exchange["request"]["headers"].items()
        ]

        response_headers = [
            {"name": name, "value": value}
            for name, value in exchange["response"]["headers"].items()
        ]

        # Add additional information extracted from the response
        try:
            response_headers.extend(
                [{"name": k, "value": str(v)} for k, v in exchange["excerpts"].items()]
            )
        except Exception:
            pass

        # Determine content type
        content_type = exchange["response"]["headers"].get("Content-Type", "text/plain")
        # Remove charset if present (e.g., "text/html; charset=utf-8" -> "text/html")
        if ";" in content_type:
            content_type = content_type.split(";")[0].strip()

        # Create HAR entry
        entry = {
            "_id": str(index),
            "_name": parsed_url.path or "/",
            "startedDateTime": exchange["timestamp"],
            "time": exchange["elapsed_ms"],
            "request": {
                "method": "GET",
                "url": url,
                "httpVersion": "HTTP/1.1",
                "cookies": [],
                "headers": request_headers,
                "queryString": query_string,
                "headersSize": -1,
                "bodySize": 0,
            },
            "response": {
                "status": exchange["response"]["status_code"],
                "statusText": exchange["response"].get("reason", "OK"),
                "httpVersion": "HTTP/1.1",
                "cookies": [],
                "headers": response_headers,
                "content": {
                    "size": len(body_content.encode("utf-8")),
                    "mimeType": content_type,
                    "text": body_content,
                },
                "redirectURL": "",
                "headersSize": -1,
                "bodySize": len(body_content.encode("utf-8")),
            },
            "cache": {},
            "timings": {
                "send": 0,
                "wait": exchange["elapsed_ms"],
                "receive": 0,
            },
            # "comment": exchange["comment"],
        }

        return entry

    def save_har(self, filename: str = None):
        """Scan the output folder for request files and create a HAR file.
        If HAR file already exists, only processes new requests incrementally.
        """
        self._ensure_folder()
        if filename is None:
            # Use the basename of the folder as the HAR filename
            folder_basename = os.path.basename(self.folder)
            filename = f"{folder_basename}.har"

        har_path = os.path.join(self.folder, filename)

        # Check if HAR file already exists for incremental updates
        last_processed_index = 0
        har_log = None
        if os.path.exists(har_path):
            try:
                with open(har_path, "r") as f:
                    har_log = json.load(f)
                # Find the highest index already processed
                if har_log.get("log", {}).get("entries"):
                    processed_ids = [
                        int(entry.get("_id", 0))
                        for entry in har_log["log"]["entries"]
                        if entry.get("_id", "").isdigit()
                    ]
                    if processed_ids:
                        last_processed_index = max(processed_ids)
            except (json.JSONDecodeError, KeyError, ValueError):
                # If HAR file is corrupted, start fresh
                har_log = None

        # Initialize HAR structure if needed
        if har_log is None:
            har_log = {
                "log": {
                    "version": "1.2",
                    "creator": {
                        "name": "bpkio-cli",
                        "version": f"bpkio-cli/{version('bpkio-cli')}",
                    },
                    "entries": [],
                }
            }

        # Scan directory once and build maps for efficient lookup
        all_files = os.listdir(self.folder)
        json_files_map = {}  # index -> filename
        body_files_map = {}  # index -> filename

        for file in all_files:
            if file.startswith("request_") and file.endswith(".json"):
                match = re.match(r"request_(\d+)\.json", file)
                if match:
                    index = int(match.group(1))
                    if index > last_processed_index:  # Only track new files
                        json_files_map[index] = file
            elif file.startswith("request_") and ".body" in file:
                # Extract index from request_N.body* patterns
                match = re.match(r"request_(\d+)\.body", file)
                if match:
                    index = int(match.group(1))
                    if index > last_processed_index:  # Only track new files
                        body_files_map[index] = file

        # Get sorted list of new indices to process
        new_indices = sorted(set(json_files_map.keys()) & set(body_files_map.keys()))

        # Process only new request/response pairs
        for index in new_indices:
            json_file = json_files_map[index]
            body_file = body_files_map[index]
            json_path = os.path.join(self.folder, json_file)
            body_path = os.path.join(self.folder, body_file)

            entry = self._process_request_to_har_entry(index, json_path, body_path)
            if entry:
                har_log["log"]["entries"].append(entry)

        # Save HAR file (only if we processed new entries or it's a new file)
        if new_indices or not os.path.exists(har_path):
            with open(har_path, "w") as f:
                json.dump(har_log, f, indent=2)

        return har_path
