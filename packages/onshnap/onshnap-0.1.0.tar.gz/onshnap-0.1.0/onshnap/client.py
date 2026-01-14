"""Onshape API Client."""

from __future__ import annotations

import base64
import datetime
import hashlib
import hmac
import logging
import os
import random
import re
import string
import urllib.parse
from dataclasses import dataclass
from typing import Any, Literal

import requests

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://cad.onshape.com"
Method = Literal["GET", "POST", "PUT", "DELETE"]


@dataclass
class DocumentInfo:
    """Parsed Onshape document URL information."""

    document_id: str
    workspace_type: Literal["w", "v", "m"]  # workspace, version, microversion
    workspace_id: str
    element_id: str

    def get_url(self, base_url: str = DEFAULT_BASE_URL) -> str:
        """Reconstruct the document URL."""
        return f"{base_url}/documents/{self.document_id}/{self.workspace_type}/{self.workspace_id}/e/{self.element_id}"


class OnshapeClient:
    """Onshape API client."""

    def __init__(
        self,
        access_key: str | None = None,
        secret_key: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 60.0,
    ) -> None:
        """Initialize the Onshape client.

        Args:
            access_key: Onshape API access key (or set ONSHAPE_ACCESS_KEY env var)
            secret_key: Onshape API secret key (or set ONSHAPE_SECRET_KEY env var)
            base_url: Base URL for Onshape API
            timeout: Request timeout in seconds
        """
        # Get credentials from environment if not provided
        if access_key is None:
            access_key = os.environ.get("ONSHAPE_ACCESS_KEY")
        if secret_key is None:
            secret_key = os.environ.get("ONSHAPE_SECRET_KEY")

        if access_key is None or secret_key is None:
            raise ValueError(
                "Onshape API credentials required. Set ONSHAPE_ACCESS_KEY and ONSHAPE_SECRET_KEY "
                "environment variables, or pass them to the constructor."
            )

        self.access_key = access_key.encode("utf-8")
        self.secret_key = secret_key.encode("utf-8")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        # Create a session for connection pooling
        self.session = requests.Session()
        # Note: We handle 307 redirects manually by setting allow_redirects=False in requests

    def parse_url(self, document_url: str) -> DocumentInfo:
        """Parse an Onshape document URL into its components.

        Args:
            document_url: Full Onshape document URL

        Returns:
            DocumentInfo with parsed components

        Raises:
            ValueError: If URL format is invalid
        """
        # Support URLs with different base domains (cad.onshape.com, etc.)
        pattern = r"https?://[^/]+/documents/([\w\d]+)/(w|v|m)/([\w\d]+)/e/([\w\d]+)"
        match = re.match(pattern, document_url)

        if match is None:
            raise ValueError(
                f"Invalid Onshape document URL: {document_url}\n"
                "Expected format: https://cad.onshape.com/documents/{did}/{w|v|m}/{wid}/e/{eid}"
            )

        return DocumentInfo(
            document_id=match.group(1),
            workspace_type=match.group(2),  # type: ignore[arg-type]
            workspace_id=match.group(3),
            element_id=match.group(4),
        )

    def _make_nonce(self) -> str:
        """Generate a unique 25-character nonce for request signing."""
        chars = string.digits + string.ascii_letters
        return "".join(random.choice(chars) for _ in range(25))

    def _make_auth(
        self,
        method: str,
        date: str,
        nonce: str,
        path: str,
        query: dict[str, Any] | None = None,
        content_type: str = "application/json",
    ) -> str:
        r"""Create the HMAC-SHA256 authentication signature.

        The signature string format (all lowercase):
        {method}\n{nonce}\n{date}\n{content_type}\n{path}\n{query_string}\n

        Args:
            method: HTTP method (GET, POST, etc.)
            date: RFC 2822 formatted date string
            nonce: Unique request nonce
            path: API path (e.g., /api/assemblies/d/{did}/...)
            query: Query parameters as dict
            content_type: Content-Type header value (empty for GET requests)

        Returns:
            The Authorization header value
        """
        # Build query string (do NOT sort - use order from dict)
        query_str = urllib.parse.urlencode(query) if query else ""

        # Build the string to sign (all lowercase)
        # Format: method\nnonce\ndate\ncontent_type\npath\nquery_string\n
        hmac_str = (f"{method}\n{nonce}\n{date}\n{content_type}\n{path}\n{query_str}\n").lower().encode("utf-8")

        logger.debug("HMAC string to sign:\n%s", hmac_str.decode())

        # Compute HMAC-SHA256 signature
        signature = base64.b64encode(hmac.new(self.secret_key, hmac_str, digestmod=hashlib.sha256).digest())

        # Build Authorization header
        auth = f"On {self.access_key.decode('utf-8')}:HmacSHA256:{signature.decode('utf-8')}"
        logger.debug("Authorization header: %s", auth)

        return auth

    def _make_headers(
        self,
        method: str,
        path: str,
        query: dict[str, Any] | None = None,
        content_type: str | None = None,
        accept: str = "application/json",
    ) -> dict[str, str]:
        """Create signed request headers.

        Args:
            method: HTTP method
            path: API path
            query: Query parameters
            content_type: Content-Type header (defaults to "application/json")
            accept: Accept header value

        Returns:
            Dictionary of request headers
        """
        # Use UTC time in RFC 2822 format
        date = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
        nonce = self._make_nonce()

        # Always use "application/json" in signature (even for GET requests)
        # This matches the reference implementation
        sign_content_type = content_type if content_type else "application/json"

        auth = self._make_auth(
            method=method,
            date=date,
            nonce=nonce,
            path=path,
            query=query or {},
            content_type=sign_content_type,
        )

        headers = {
            "Content-Type": "application/json",
            "Date": date,
            "On-Nonce": nonce,
            "Authorization": auth,
            "Accept": accept,
            "User-Agent": "onshnap/1.0",
        }

        # Override Content-Type if explicitly provided
        if content_type:
            headers["Content-Type"] = content_type

        return headers

    def request(
        self,
        method: Method,
        path: str,
        query: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
        base_url: str | None = None,
        accept: str = "application/json",
        max_redirects: int = 5,
    ) -> requests.Response:
        """Make an authenticated request to the Onshape API.

        This method handles 307 redirects by re-signing requests for the new host.
        Standard requests library auto-redirects fail because they don't re-sign.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: API path (e.g., /api/assemblies/d/{did}/...)
            query: Query parameters
            body: Request body (for POST/PUT)
            base_url: Override base URL (used for redirects)
            accept: Accept header value
            max_redirects: Maximum number of redirects to follow

        Returns:
            Response object

        Raises:
            requests.HTTPError: For non-2xx responses
            ValueError: For too many redirects
        """
        if base_url is None:
            base_url = self.base_url

        # Determine content type (always "application/json" for signature)
        content_type = "application/json" if body else None

        # Build headers with signature
        headers = self._make_headers(
            method=method,
            path=path,
            query=query,
            content_type=content_type,
            accept=accept,
        )

        # Build full URL
        url = base_url + path
        if query:
            url += "?" + urllib.parse.urlencode(query)

        logger.debug("Making %s request to %s", method, url)

        # Make request
        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                json=body,
                timeout=self.timeout,
                allow_redirects=False,
            )
        except requests.exceptions.TooManyRedirects as e:
            raise RuntimeError("Unexpected redirect error") from e

        # Handle 307 Temporary Redirect
        if response.status_code == 307:
            if max_redirects <= 0:
                raise ValueError("Too many redirects")

            location = response.headers.get("Location")
            if not location:
                raise ValueError("307 redirect without Location header")

            # Parse the new URL
            parsed = urllib.parse.urlparse(location)
            new_base_url = f"{parsed.scheme}://{parsed.netloc}"
            new_path = parsed.path

            # Parse new query parameters
            new_query = dict(urllib.parse.parse_qsl(parsed.query))

            logger.debug("Following 307 redirect to %s", location)

            # Recursively make request to new URL with re-signed headers
            return self.request(
                method=method,
                path=new_path,
                query=new_query if new_query else query,
                body=body,
                base_url=new_base_url,
                accept=accept,
                max_redirects=max_redirects - 1,
            )

        # Log non-success responses
        if not response.ok:
            logger.error(
                "Request failed: %s %s -> %d: %s",
                method,
                path,
                response.status_code,
                response.text[:500],
            )

            if response.status_code == 401:
                logger.error(
                    "401 Unauthorized. Check that:\n"
                    "  1. ONSHAPE_ACCESS_KEY and ONSHAPE_SECRET_KEY are correct\n"
                    "  2. The API keys have not expired\n"
                    "  3. The signature is being computed correctly"
                )
            elif response.status_code == 403:
                logger.error(
                    "403 Forbidden. Check that:\n"
                    "  1. The document exists and is accessible\n"
                    "  2. The document is shared with your account\n"
                    "  3. Your API key has read permissions"
                )

        return response

    def get(
        self,
        path: str,
        query: dict[str, Any] | None = None,
        accept: str = "application/json",
    ) -> requests.Response:
        """Make a GET request."""
        return self.request("GET", path, query=query, accept=accept)

    def get_json(
        self,
        path: str,
        query: dict[str, Any] | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Make a GET request and return JSON response."""
        response = self.get(path, query=query)
        response.raise_for_status()
        return response.json()

    def get_binary(
        self,
        path: str,
        query: dict[str, Any] | None = None,
    ) -> bytes:
        """Make a GET request and return binary response."""
        response = self.get(path, query=query, accept="*/*")
        response.raise_for_status()
        return response.content

    # -------------------------------------------------------------------------
    # High-level API methods
    # -------------------------------------------------------------------------

    def get_assembly_occurrences(
        self,
        doc: DocumentInfo,
        include_hidden: bool = False,
    ) -> list[dict[str, Any]]:
        """Get all part occurrences with their global transforms.

        This is the key endpoint for the "frozen snapshot" approach.
        Each occurrence includes the World_T_Part transform.

        Args:
            doc: Document information
            include_hidden: Whether to include hidden instances

        Returns:
            List of occurrence dictionaries with 'path' and 'transform' keys
        """
        path = (
            f"/api/assemblies/d/{doc.document_id}/"
            f"{doc.workspace_type}/{doc.workspace_id}/e/{doc.element_id}/occurrences"
        )

        query = {
            "includeHidden": str(include_hidden).lower(),
        }

        result = self.get_json(path, query=query)
        if not isinstance(result, list):
            raise ValueError(f"Expected list from occurrences API, got {type(result)}")
        return result

    def get_assembly(
        self,
        doc: DocumentInfo,
        include_mate_features: bool = False,
        include_mate_connectors: bool = False,
    ) -> dict[str, Any]:
        """Get the assembly definition including parts and instances.

        Args:
            doc: Document information
            include_mate_features: Whether to include mate features
            include_mate_connectors: Whether to include mate connectors

        Returns:
            Assembly definition dictionary
        """
        path = f"/api/assemblies/d/{doc.document_id}/{doc.workspace_type}/{doc.workspace_id}/e/{doc.element_id}"

        query = {
            "includeMateFeatures": str(include_mate_features).lower(),
            "includeMateConnectors": str(include_mate_connectors).lower(),
            "includeNonSolids": "false",
        }

        result = self.get_json(path, query=query)
        if not isinstance(result, dict):
            raise ValueError(f"Expected dict from assembly API, got {type(result)}")
        return result

    def download_stl(
        self,
        document_id: str,
        workspace_type: str,
        workspace_id: str,
        element_id: str,
        part_id: str,
        units: str = "meter",
    ) -> bytes:
        """Download an STL mesh for a specific part.

        Args:
            document_id: Document ID
            workspace_type: Workspace type (w, v, m)
            workspace_id: Workspace ID
            element_id: Element ID (Part Studio)
            part_id: Part ID within the Part Studio
            units: Output units (meter, millimeter, inch, etc.)

        Returns:
            Binary STL data
        """
        # URL-encode the part ID (may contain special characters)
        encoded_part_id = urllib.parse.quote(part_id, safe="")

        path = f"/api/parts/d/{document_id}/{workspace_type}/{workspace_id}/e/{element_id}/partid/{encoded_part_id}/stl"

        query = {
            "mode": "binary",
            "grouping": "true",
            "units": units,
        }

        return self.get_binary(path, query=query)

    def get_part_metadata(
        self,
        document_id: str,
        workspace_type: str,
        workspace_id: str,
        element_id: str,
        part_id: str,
        configuration: str = "",
    ) -> dict[str, Any]:
        """Get metadata for a specific part, including appearance/color.

        Args:
            document_id: Document ID
            workspace_type: Workspace type (w, v, m)
            workspace_id: Workspace ID
            element_id: Element ID (Part Studio)
            part_id: Part ID within the Part Studio
            configuration: Configuration string (optional)

        Returns:
            Part metadata dictionary
        """
        # URL-encode the part ID (may contain special characters)
        encoded_part_id = urllib.parse.quote(part_id, safe="")

        path = f"/api/metadata/d/{document_id}/{workspace_type}/{workspace_id}/e/{element_id}/p/{encoded_part_id}"

        query: dict[str, Any] = {}
        if configuration:
            query["configuration"] = configuration

        result = self.get_json(path, query=query)
        if not isinstance(result, dict):
            raise ValueError(f"Expected dict from metadata API, got {type(result)}")
        return result

    def get_part_mass_properties(
        self,
        document_id: str,
        workspace_type: str,
        workspace_id: str,
        element_id: str,
        part_id: str,
        configuration: str = "",
    ) -> dict[str, Any]:
        """Get mass properties for a specific part, including mass, inertia, and center of mass.

        Args:
            document_id: Document ID
            workspace_type: Workspace type (w, v, m)
            workspace_id: Workspace ID
            element_id: Element ID (Part Studio)
            part_id: Part ID within the Part Studio
            configuration: Configuration string (optional)

        Returns:
            Mass properties dictionary with 'bodies' containing mass/inertia data
        """
        # URL-encode the part ID (may contain special characters)
        encoded_part_id = urllib.parse.quote(part_id, safe="")

        path = (
            f"/api/parts/d/{document_id}/{workspace_type}/{workspace_id}/"
            f"e/{element_id}/partid/{encoded_part_id}/massproperties"
        )

        query: dict[str, Any] = {
            "useMassPropertyOverrides": "true",
        }
        if configuration:
            query["configuration"] = configuration

        result = self.get_json(path, query=query)
        if not isinstance(result, dict):
            raise ValueError(f"Expected dict from massproperties API, got {type(result)}")
        return result
