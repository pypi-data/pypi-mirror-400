"""
DataDome Middleware for ASGI Applications

This middleware intercepts HTTP requests at the ASGI layer,
allowing access to HTTP headers, IP addresses, and other transport-level information.

Compatible with any ASGI 3.0 application.
"""

import json
import logging
import re
import time
from collections.abc import Callable
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class DataDomeMiddleware:
    """
    DataDome middleware at the ASGI layer that intercepts HTTP requests.

    Compatible with any ASGI 3.0 application.

    Args:
        app: The ASGI application
        server_side_key: DataDome server-side key (required)
        url_pattern_exclusion: Regex pattern for URLs to exclude from DataDome checks
        url_pattern_inclusion: Regex pattern for URLs to include in DataDome checks
        endpoint_host: DataDome API endpoint host (default: "api.datadome.co")
        timeout: Timeout in milliseconds for request to the DataDome API (default: 150)
        enable_mcp_support: Enable MCP (Model Context Protocol) information extraction (default: False)
    """

    def __init__(
        self,
        app: Callable,
        server_side_key: str,
        url_pattern_exclusion: str = r"\.(avi|avif|bmp|css|eot|flac|flv|gif|gz|ico|jpeg|jpg|js|json|less|map|mka|mkv|mov|mp3|mp4|mpeg|mpg|ogg|ogm|opus|otf|png|svg|svgz|swf|tiff|ttf|wav|webm|webp|woff|woff2|xml|zip)$",
        url_pattern_inclusion: str = "",
        endpoint_host: str = "api.datadome.co",
        timeout: float = 150,
        enable_mcp_support: bool = False,
    ):
        self.app = app
        self.server_side_key = server_side_key

        if url_pattern_exclusion == "":
            self.url_pattern_exclusion = None
        else:
            self.url_pattern_exclusion = re.compile(url_pattern_exclusion)

        if url_pattern_inclusion == "":
            self.url_pattern_inclusion = None
        else:
            self.url_pattern_inclusion = re.compile(url_pattern_inclusion)

        self.endpoint_host = endpoint_host
        self.timeout = timeout
        self.enable_mcp_support = enable_mcp_support
        self.module_name = "Python ASGI"
        self.module_version = "1.0.0"

        # Create an httpx client for connection pooling and reuse
        # Convert milliseconds to seconds for httpx
        timeout_seconds = timeout / 1000.0
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout=timeout_seconds), follow_redirects=False
        )

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - cleanup resources."""
        await self.http_client.aclose()

    async def __call__(self, scope: dict[str, Any], receive: Callable, send: Callable):
        """
        ASGI application callable.

        Args:
            scope: ASGI connection scope
            receive: ASGI receive callable
            send: ASGI send callable
        """
        if scope["type"] != "http":
            # Not an HTTP request, pass through
            await self.app(scope, receive, send)
            return

        # Process HTTP request
        await self._process_http_request(scope, receive, send)

    def _parse_headers(self, headers: list[tuple[bytes, bytes]]) -> dict[str, str]:
        """
        Parse ASGI headers into a dictionary.

        Args:
            headers: List of (name, value) tuples in bytes

        Returns:
            Dictionary with lowercase header names as keys
        """
        return {name.decode("utf-8").lower(): value.decode("utf-8") for name, value in headers}

    def _get_header(self, headers: dict[str, str], header_name: str) -> str | None:
        """
        Get a header value (case-insensitive).

        Args:
            headers: Dictionary of headers
            header_name: Header name to retrieve

        Returns:
            Header value or None if not found
        """
        return headers.get(header_name.lower())

    def _get_client_ip(self, scope: dict[str, Any]) -> str | None:
        """
        Extract client IP from ASGI scope.

        Args:
            scope: ASGI connection scope

        Returns:
            Client IP address or None if not found
        """
        client = scope.get("client")
        if client:
            return client[0]
        return None

    def _build_url(self, scope: dict[str, Any]) -> str:
        """
        Build URL from ASGI scope (host + path, excluding query params).

        Args:
            scope: ASGI connection scope

        Returns:
            URL string
        """
        headers = self._parse_headers(scope.get("headers", []))
        host = self._get_header(headers, "host") or ""
        path = scope.get("path", "/")
        return f"{host}{path}"

    def _get_current_micro_time(self) -> float:
        """
        Get current time in microseconds.

        Returns:
            Current timestamp in microseconds
        """
        return time.time_ns() / 1000.0

    def _get_headers_list(self, headers: dict[str, str]) -> str:
        """
        Get a formatted list of all headers.

        Args:
            headers: Dictionary of headers

        Returns:
            Comma-separated list of header names
        """
        return ",".join(headers.keys())

    def _get_authorization_length(self, headers: dict[str, str]) -> int:
        """
        Get the length of the Authorization header.

        Args:
            headers: Dictionary of headers

        Returns:
            Length of Authorization header or 0 if not present
        """
        auth_header = self._get_header(headers, "authorization")
        return len(auth_header) if auth_header else 0

    def _get_client_id_and_cookies_length(self, headers: dict[str, str]) -> dict[str, Any]:
        """
        Extract DataDome client ID and calculate total cookies length.

        Args:
            headers: Dictionary of headers

        Returns:
            Dictionary with 'clientId' (str) and 'cookiesLength' (int)
        """
        client_id = ""
        cookies_length = 0

        cookie_header = self._get_header(headers, "cookie")

        if cookie_header:
            # Calculate total length
            cookies_length = len(cookie_header)

            # Parse cookies to find 'datadome' cookie
            cookies_list = cookie_header.split(";")

            for cookie_string in cookies_list:
                cookie_string = cookie_string.strip()

                # Split by first '=' to handle values with '=' in them
                if "=" in cookie_string:
                    cookie_parts = cookie_string.split("=", 1)
                    cookie_name = cookie_parts[0].strip()

                    if cookie_name == "datadome":
                        # Extract value after 'datadome='
                        client_id = cookie_parts[1] if len(cookie_parts) > 1 else ""
                        break

        return {"clientId": client_id, "cookiesLength": cookies_length}

    def _is_mcp_request(self, scope: dict[str, Any], headers: dict[str, str]) -> bool:
        """
        Determine if the request is an MCP request based on the specification of the MCP protocol.
        For more information, refer to: https://modelcontextprotocol.io/specification/latest/basic/transports

        Args:
            scope: ASGI connection scope
            headers: Dictionary of headers

        Returns:
            True if the request is an MCP request, False otherwise
        """
        path = scope.get("path", "/")
        if "/mcp" not in path.lower():
            return False

        method = scope.get("method", "")
        if method not in ["POST", "GET", "DELETE"]:
            return False

        accept_header = self._get_header(headers, "accept")
        if not accept_header:
            return False

        accept_lower = accept_header.lower()

        if method == "GET" and "text/event-stream" in accept_lower:
            return True

        if "application/json" in accept_lower and "text/event-stream" in accept_lower:
            if method == "DELETE":
                return True

            content_type = self._get_header(headers, "content-type")
            if content_type and "application/json" in content_type.lower():
                return True

        return False

    async def _collect_mcp_data(self, body: bytes) -> dict[str, str | None]:
        """
        Extract MCP information from the request body.

        Args:
            body: Request body bytes

        Returns:
            Dictionary with extracted MCP properties
        """
        result: dict[str, str | None] = {
            "jsonRpcRequestId": None,
            "jsonRpcVersion": None,
            "mcpMethod": None,
            "mcpParamsClientInfoName": None,
            "mcpParamsClientInfoVersion": None,
            "mcpParamsToolName": None,
        }

        try:
            if not body:
                return result

            # Parse JSON body
            json_body = json.loads(body.decode("utf-8"))

            # Extract id, method, and RPC version from root level
            if "id" in json_body and json_body["id"] is not None:
                result["jsonRpcRequestId"] = str(json_body["id"])

            if "method" in json_body:
                result["mcpMethod"] = json_body["method"]

            if "jsonrpc" in json_body:
                result["jsonRpcVersion"] = json_body["jsonrpc"]

            # If method is 'initialize', extract clientName and clientVersion from params.clientInfo
            if (
                json_body.get("method") == "initialize"
                and "params" in json_body
                and "clientInfo" in json_body["params"]
            ):
                client_info = json_body["params"]["clientInfo"]

                if "name" in client_info and client_info["name"] is not None:
                    result["mcpParamsClientInfoName"] = client_info["name"]

                if "version" in client_info and client_info["version"] is not None:
                    result["mcpParamsClientInfoVersion"] = client_info["version"]

            # If method is 'tools/call', extract tool name from params.name
            if (
                json_body.get("method") == "tools/call"
                and "params" in json_body
                and "name" in json_body["params"]
            ):
                result["mcpParamsToolName"] = json_body["params"]["name"]

        except (json.JSONDecodeError, UnicodeDecodeError, KeyError, AttributeError):
            # If JSON parsing fails or any other error, return result with None values
            pass

        return result

    async def _read_body(self, receive: Callable) -> bytes:
        """
        Read the entire request body from ASGI receive callable.

        Args:
            receive: ASGI receive callable

        Returns:
            Complete request body as bytes
        """
        body = b""
        more_body = True

        while more_body:
            message = await receive()
            body += message.get("body", b"")
            more_body = message.get("more_body", False)

        return body

    async def _send_response(
        self, send: Callable, status_code: int, headers: list[tuple[bytes, bytes]], body: bytes
    ):
        """
        Send an HTTP response via ASGI send callable.

        Args:
            send: ASGI send callable
            status_code: HTTP status code
            headers: List of header tuples
            body: Response body
        """
        await send(
            {
                "type": "http.response.start",
                "status": status_code,
                "headers": headers,
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": body,
            }
        )

    def _add_datadome_request_headers(
        self, dd_headers: dict[str, str], scope: dict[str, Any]
    ) -> None:
        """
        Add DataDome headers to the original request scope.

        Args:
            dd_headers: Headers from DataDome API response
            scope: ASGI connection scope (modified in-place)
        """
        # Check if x-datadome-request-headers exists
        if "x-datadome-request-headers" not in dd_headers:
            return

        datadome_headers_str = dd_headers["x-datadome-request-headers"]

        try:
            # Get mutable headers from scope
            headers = dict(scope.get("headers", []))

            # Split the header list by spaces
            datadome_header_names = datadome_headers_str.split(" ")

            for datadome_header_name in datadome_header_names:
                # Check if the header exists in DataDome response
                if datadome_header_name.lower() not in dd_headers:
                    # Skip this header and continue with the next one
                    continue

                datadome_header_value = dd_headers[datadome_header_name.lower()]

                # Convert header name to bytes (lowercase)
                header_key = datadome_header_name.lower().encode("utf-8")
                header_val = datadome_header_value.encode("utf-8")
                headers[header_key] = header_val

            # Update the scope headers
            scope["headers"] = list(headers.items())

        except Exception as e:
            logger.error("Error adding DataDome headers to request: %s", e, exc_info=True)

    def _add_datadome_response_headers(
        self, dd_headers: dict[str, str], base_headers: list[tuple[bytes, bytes]] | None = None
    ) -> list[tuple[bytes, bytes]] | None:
        """
        Add DataDome headers to response headers.

        Args:
            dd_headers: Headers from DataDome API response
            base_headers: Existing headers to add to (optional)

        Returns:
            List of header tuples or None if failed
        """
        # Check if x-datadome-headers exists
        if "x-datadome-headers" not in dd_headers:
            return None

        datadome_headers_str = dd_headers["x-datadome-headers"]

        try:
            headers = list(base_headers) if base_headers else []

            # Split the header list by spaces
            datadome_header_names = datadome_headers_str.split(" ")

            for datadome_header_name in datadome_header_names:
                # Check if the header exists in DataDome response
                if datadome_header_name.lower() not in dd_headers:
                    # Skip this header and continue with the next one
                    continue

                datadome_header_value = dd_headers[datadome_header_name.lower()]

                # Add header as bytes tuple
                header_key = datadome_header_name.encode("utf-8")
                header_val = datadome_header_value.encode("utf-8")
                headers.append((header_key, header_val))

            return headers
        except Exception as e:
            logger.error("Error adding DataDome headers to response: %s", e, exc_info=True)
            return None

    async def _process_http_request(self, scope: dict[str, Any], receive: Callable, send: Callable):
        """
        Process an HTTP request through the DataDome middleware.

        Args:
            scope: ASGI connection scope
            receive: ASGI receive callable
            send: ASGI send callable
        """
        # Build URL (host + path, excluding query params)
        url = self._build_url(scope)

        # Check if URL matches exclusion pattern - if yes, skip DataDome
        if self.url_pattern_exclusion is not None and self.url_pattern_exclusion.search(url):
            await self.app(scope, receive, send)
            return

        # Check if URL matches inclusion pattern - if no, skip DataDome
        if self.url_pattern_inclusion is not None and not self.url_pattern_inclusion.search(url):
            await self.app(scope, receive, send)
            return

        # URL passed verification, continue with DataDome processing

        # Extract client IP
        client_ip = self._get_client_ip(scope)
        if not client_ip:
            logger.warning("Unable to determine client IP, skipping DataDome")
            await self.app(scope, receive, send)
            return

        # Parse headers
        headers = self._parse_headers(scope.get("headers", []))

        # Get host
        host_header = self._get_header(headers, "host")
        host = host_header[0:512] if host_header else ""

        # Get scheme
        scheme = scope.get("scheme", "http")
        x_forwarded_proto = self._get_header(headers, "x-forwarded-proto")
        if x_forwarded_proto and x_forwarded_proto in ["http", "https"]:
            scheme = x_forwarded_proto

        # Get path and query string
        path = scope.get("path", "/")
        query_string = scope.get("query_string", b"").decode("utf-8")
        request_uri = path + ("?" + query_string if query_string else "")

        # Get method
        method = scope.get("method", "GET")

        # Get port
        server = scope.get("server")
        port = server[1] if server and len(server) > 1 else (443 if scheme == "https" else 80)

        client_id_and_cookies_length = self._get_client_id_and_cookies_length(headers)

        # Build the DataDome request payload
        request_data = {
            "Key": self.server_side_key,
            "IP": client_ip,
            "APIConnectionState": "new",
            "AuthorizationLen": self._get_authorization_length(headers),
            "CookiesLen": client_id_and_cookies_length["cookiesLength"],
            "HeadersList": self._get_headers_list(headers)[0:512],
            "Host": host,
            "Method": method,
            "ModuleVersion": self.module_version,
            "Port": port,
            "Protocol": scheme,
            "Request": request_uri[0:2048],
            "RequestModuleName": self.module_name,
            "ServerHostname": host[0:512],
            "ServerName": host[0:512],
            "TimeRequest": self._get_current_micro_time(),
        }

        # Read body if needed for MCP support
        body = b""
        body_consumed = False
        if self.enable_mcp_support and self._is_mcp_request(scope, headers):
            # Extract MCP session and protocol headers
            mcp_session_id = self._get_header(headers, "mcp-session-id")
            if mcp_session_id:
                request_data["McpSessionId"] = mcp_session_id[0:64]

            mcp_protocol_version = self._get_header(headers, "mcp-protocol-version")
            if mcp_protocol_version:
                request_data["McpProtocolVersion"] = mcp_protocol_version[0:16]

            # Extract MCP data from body for POST requests
            if method == "POST":
                body = await self._read_body(receive)
                body_consumed = True
                mcp_data = await self._collect_mcp_data(body)
                if mcp_data["jsonRpcRequestId"]:
                    request_data["JsonRpcRequestId"] = mcp_data["jsonRpcRequestId"][0:64]
                if mcp_data["jsonRpcVersion"]:
                    request_data["JsonRpcVersion"] = mcp_data["jsonRpcVersion"][0:8]
                if mcp_data["mcpMethod"]:
                    request_data["McpMethod"] = mcp_data["mcpMethod"][0:64]
                if mcp_data["mcpParamsClientInfoName"]:
                    request_data["McpParamsClientInfoName"] = mcp_data["mcpParamsClientInfoName"][
                        0:64
                    ]
                if mcp_data["mcpParamsClientInfoVersion"]:
                    request_data["McpParamsClientInfoVersion"] = mcp_data[
                        "mcpParamsClientInfoVersion"
                    ][0:16]
                if mcp_data["mcpParamsToolName"]:
                    request_data["McpParamsToolName"] = mcp_data["mcpParamsToolName"][0:64]

        # Define optional header mappings (header_key, payload_key, limit)
        # limit > 0: truncate from start (keep first N chars)
        # limit < 0: truncate from end (keep last N chars)
        # limit = 0: no truncation
        optional_header_mappings = [
            ("accept", "Accept", 512),
            ("accept-charset", "AcceptCharset", 128),
            ("accept-encoding", "AcceptEncoding", 128),
            ("accept-language", "AcceptLanguage", 256),
            ("cache-control", "CacheControl", 128),
            ("connection", "Connection", 128),
            ("content-length", "PostParamLen", 0),
            ("content-type", "ContentType", 64),
            ("from", "From", 128),
            ("origin", "Origin", 512),
            ("pragma", "Pragma", 128),
            ("referer", "Referer", 1024),
            ("sec-ch-device-memory", "SecCHDeviceMemory", 8),
            ("sec-ch-ua", "SecCHUA", 128),
            ("sec-ch-ua-arch", "SecCHUAArch", 16),
            ("sec-ch-ua-full-version-list", "SecCHUAFullVersionList", 256),
            ("sec-ch-ua-mobile", "SecCHUAMobile", 8),
            ("sec-ch-ua-model", "SecCHUAModel", 128),
            ("sec-ch-ua-platform", "SecCHUAPlatform", 32),
            ("sec-fetch-dest", "SecFetchDest", 32),
            ("sec-fetch-mode", "SecFetchMode", 32),
            ("sec-fetch-site", "SecFetchSite", 64),
            ("sec-fetch-user", "SecFetchUser", 8),
            ("signature", "Signature", 512),
            ("signature-agent", "SignatureAgent", 512),
            ("signature-input", "SignatureInput", 2048),
            ("true-client-ip", "TrueClientIP", 128),
            ("user-agent", "UserAgent", 768),
            ("via", "Via", 256),
            ("x-forwarded-for", "XForwardedForIP", -512),
            ("x-real-ip", "X-Real-IP", 128),
            ("x-requested-with", "X-Requested-With", 128),
        ]

        # Extract optional headers and apply limits
        for header_key, payload_key, limit in optional_header_mappings:
            header_value = self._get_header(headers, header_key)
            if header_value is not None:
                if limit > 0:
                    request_data[payload_key] = header_value[:limit]
                elif limit < 0:
                    request_data[payload_key] = header_value[limit:]
                else:
                    request_data[payload_key] = header_value

        datadome_headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "DataDome",
        }

        datadome_client_id = self._get_header(headers, "x-datadome-clientid")
        if datadome_client_id is not None and datadome_client_id != "":
            request_data["ClientID"] = datadome_client_id[0:128]
            datadome_headers["X-DataDome-X-Set-Cookie"] = "true"
        else:
            request_data["ClientID"] = client_id_and_cookies_length["clientId"][0:128]

        # Perform HTTP request to DataDome's API
        try:
            datadome_url = f"https://{self.endpoint_host}/validate-request"

            dd_response = await self.http_client.post(
                datadome_url, data=request_data, headers=datadome_headers
            )

        except (
            httpx.TimeoutException,
            httpx.ConnectTimeout,
            httpx.ReadTimeout,
            httpx.PoolTimeout,
            httpx.WriteTimeout,
        ) as e:
            # If DataDome API call times out, skip DataDome
            logger.warning("DataDome API timeout, skipping DataDome: %s", e)
            await self._forward_request(scope, receive, send, body_consumed, body)
            return

        except httpx.RequestError as e:
            # If DataDome API call fails, skip DataDome
            logger.error("DataDome API request error, skipping DataDome: %s", e, exc_info=True)
            await self._forward_request(scope, receive, send, body_consumed, body)
            return

        except Exception as e:
            # Catch any other unexpected errors and skip DataDome to ensure availability
            logger.error(
                "Unexpected error calling DataDome API, skipping DataDome: %s", e, exc_info=True
            )
            await self._forward_request(scope, receive, send, body_consumed, body)
            return

        # Parse response headers
        dd_headers_parsed = {k.lower(): v for k, v in dd_response.headers.items()}
        x_datadome_response = dd_headers_parsed.get("x-datadomeresponse")
        if not x_datadome_response:
            logger.error(
                'Header "x-datadomeresponse" not found in DataDome API response, skipping DataDome'
            )
            await self._forward_request(scope, receive, send, body_consumed, body)
            return

        # Verify the header value is numeric
        if not x_datadome_response.isdigit():
            logger.error(
                'Invalid "x-datadomeresponse" header value: %s, skipping DataDome',
                x_datadome_response,
            )
            await self._forward_request(scope, receive, send, body_consumed, body)
            return

        datadome_status = int(x_datadome_response)
        # Verify status code matches x-datadomeresponse header
        if dd_response.status_code != datadome_status:
            logger.error(
                'Status code mismatch, skipping DataDome. Status code: %d - "x-datadomeresponse": %d',
                dd_response.status_code,
                datadome_status,
            )
            await self._forward_request(scope, receive, send, body_consumed, body)
            return

        # Handle response based on DataDome status
        match datadome_status:
            case 200:
                # Add DataDome headers to original request and continue
                self._add_datadome_request_headers(dd_headers_parsed, scope)

                # Intercept response to add DataDome headers
                response_headers = []
                response_started = False

                async def send_wrapper(message):
                    nonlocal response_started, response_headers
                    if message["type"] == "http.response.start" and not response_started:
                        response_started = True
                        # Add DataDome headers to response
                        original_headers = message.get("headers", [])
                        dd_response_headers = self._add_datadome_response_headers(
                            dd_headers_parsed, original_headers
                        )
                        if dd_response_headers is not None:
                            message["headers"] = dd_response_headers
                    await send(message)

                await self._forward_request(scope, receive, send_wrapper, body_consumed, body)

            case 301 | 302 | 401 | 403:
                # Return blocking response
                response_body = dd_response.content
                response_headers = self._add_datadome_response_headers(dd_headers_parsed)
                if response_headers is None:
                    response_headers = []

                await self._send_response(send, 403, response_headers, response_body)

            case _:
                # Unknown status: skip DataDome
                logger.warning("Unknown DataDome status: %d, skipping DataDome", datadome_status)
                await self._forward_request(scope, receive, send, body_consumed, body)

    async def _forward_request(
        self,
        scope: dict[str, Any],
        receive: Callable,
        send: Callable,
        body_consumed: bool,
        body: bytes,
    ):
        """
        Forward request to the app, handling body replay if necessary.

        Args:
            scope: ASGI connection scope
            receive: ASGI receive callable
            send: ASGI send callable
            body_consumed: Whether the request body was already consumed
            body: The consumed request body (used only if body_consumed is True)
        """
        if body_consumed:
            await self._forward_request_with_body(scope, body, send)
        else:
            await self.app(scope, receive, send)

    async def _forward_request_with_body(self, scope: dict[str, Any], body: bytes, send: Callable):
        """
        Forward request to the app when body has already been consumed.

        This implements the "body replay pattern" for ASGI middleware. Since the middleware
        already consumed the request body (by calling the original receive callable), we need
        to provide a replacement receive callable that returns the buffered body to the
        downstream application.

        Args:
            scope: ASGI connection scope
            body: The consumed request body
            send: ASGI send callable
        """
        # Track whether we've already sent the body to avoid duplicate sends
        # This flag is necessary because some ASGI apps might call receive() multiple
        # times even after getting more_body=False
        body_sent = False

        async def receive():
            """
            Replacement receive callable that replays the buffered request body.

            This function replaces the original ASGI receive callable. When the downstream
            application calls await receive(), it will get the buffered body instead of
            trying to read from the already-consumed network stream.

            The body_sent flag prevents duplicate body delivery if the downstream app
            calls receive() multiple times (e.g., in a loop before checking more_body).

            Returns:
                ASGI message dict with type, body, and more_body fields
                - First call: Complete buffered body with more_body=False
                - Subsequent calls: Empty body (defensive fallback)
            """
            nonlocal body_sent
            if not body_sent:
                body_sent = True
                # Return the complete buffered body as a single ASGI message
                return {
                    "type": "http.request",
                    "body": body,
                    "more_body": False,  # Indicates this is the complete body
                }
            # Defensive fallback: return empty body if called again by downstream app
            # This prevents duplicate data processing if the app doesn't respect more_body=False
            return {
                "type": "http.request",
                "body": b"",
                "more_body": False,
            }

        await self.app(scope, receive, send)
