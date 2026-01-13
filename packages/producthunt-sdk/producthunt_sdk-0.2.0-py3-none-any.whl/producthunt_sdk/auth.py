"""Authentication for Product Hunt API."""

import hashlib
import json
import secrets
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse

import httpx


class BearerAuth(httpx.Auth):
    """Bearer token authentication for httpx.

    Use this for both developer tokens and OAuth access tokens.

    Example:
        ```python
        from producthunt_sdk import ProductHuntClient, BearerAuth

        # With developer token
        client = ProductHuntClient(auth=BearerAuth("your_developer_token"))

        # With OAuth token
        client = ProductHuntClient(auth=BearerAuth(oauth_access_token))
        ```
    """

    def __init__(self, token: str):
        """Initialize bearer auth.

        Args:
            token: The bearer token (developer token or OAuth access token)

        Raises:
            ValueError: If token is None or empty
        """
        if not token:
            raise ValueError("Token cannot be None or empty")
        self.token = token

    def auth_flow(self, request: httpx.Request):
        """Add Authorization header to request."""
        request.headers["Authorization"] = f"Bearer {self.token}"
        yield request


class TokenCache:
    """In-memory token cache with optional file persistence.

    Example:
        ```python
        # In-memory only
        cache = TokenCache()

        # With file persistence
        cache = TokenCache("~/.producthunt_tokens.json")
        ```
    """

    def __init__(self, file_path: str | Path | None = None):
        """Initialize token cache.

        Args:
            file_path: Optional path to persist tokens. If None, tokens are only
                      stored in memory and lost when the process exits.
        """
        self._tokens: dict[str, str] = {}
        self._lock = threading.Lock()
        self._file_path = Path(file_path).expanduser() if file_path else None

        if self._file_path and self._file_path.exists():
            self._load_from_file()

    def _load_from_file(self) -> None:
        """Load tokens from file."""
        try:
            with open(self._file_path) as f:
                self._tokens = json.load(f)
        except (json.JSONDecodeError, OSError):
            self._tokens = {}

    def _save_to_file(self) -> None:
        """Save tokens to file."""
        if self._file_path:
            self._file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._file_path, "w") as f:
                json.dump(self._tokens, f)

    def get(self, key: str) -> str | None:
        """Get a cached token."""
        with self._lock:
            return self._tokens.get(key)

    def set(self, key: str, token: str) -> None:
        """Cache a token."""
        with self._lock:
            self._tokens[key] = token
            self._save_to_file()

    def clear(self, key: str | None = None) -> None:
        """Clear cached tokens.

        Args:
            key: Specific key to clear, or None to clear all
        """
        with self._lock:
            if key:
                self._tokens.pop(key, None)
            else:
                self._tokens.clear()
            self._save_to_file()


class OAuth2(httpx.Auth):
    """OAuth2 authentication for Product Hunt that handles the entire flow.

    This class implements httpx.Auth and automatically:
    - Opens browser for user authorization (on first request)
    - Runs a local callback server to receive the authorization code
    - Exchanges the code for an access token
    - Caches the token for future requests
    - Adds the Bearer token to all requests

    Note: Product Hunt requires HTTPS redirect URIs. Use ngrok to tunnel
    to localhost during development.

    Example:
        ```python
        from producthunt_sdk import ProductHuntClient, OAuth2

        # Basic usage - opens browser on first API call
        client = ProductHuntClient(auth=OAuth2(
            client_id="your_client_id",
            client_secret="your_client_secret",
        ))
        viewer = client.get_viewer()  # Browser opens, user authorizes

        # With custom redirect URI (for ngrok)
        client = ProductHuntClient(auth=OAuth2(
            client_id="your_client_id",
            client_secret="your_client_secret",
            redirect_uri="https://abc123.ngrok.io/callback",
        ))

        # With file-based token cache (persists across restarts)
        from producthunt_sdk.auth import TokenCache
        OAuth2.token_cache = TokenCache("~/.producthunt_tokens.json")
        ```
    """

    AUTHORIZE_URL = "https://api.producthunt.com/v2/oauth/authorize"
    TOKEN_URL = "https://api.producthunt.com/v2/oauth/token"

    # Class-level cache and lock (shared across all instances)
    token_cache = TokenCache()
    _lock = threading.Lock()

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        *,
        redirect_uri: str | None = None,
        redirect_uri_port: int = 8000,
        scope: str = "public private",
        timeout: float = 120,
        open_browser: bool = True,
    ):
        """Initialize OAuth2 authentication.

        Args:
            client_id: Your OAuth application client ID
            client_secret: Your OAuth application client secret
            redirect_uri: Full redirect URI (must be HTTPS for Product Hunt).
                         If None, uses http://localhost:{redirect_uri_port}/callback
                         which requires ngrok tunneling.
            redirect_uri_port: Port for local callback server (default: 8000)
            scope: Space-separated scopes (default: "public private")
                   Options: "public", "public private", "public private write"
            timeout: Seconds to wait for authorization (default: 120)
            open_browser: Whether to open browser automatically (default: True)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri_port = redirect_uri_port
        self.redirect_uri = redirect_uri or f"http://localhost:{redirect_uri_port}/callback"
        self.scope = scope
        self.timeout = timeout
        self.open_browser = open_browser

        # Generate cache key from credentials
        self._cache_key = hashlib.sha256(
            f"{client_id}:{client_secret}:{scope}".encode()
        ).hexdigest()[:16]

    def _get_cached_token(self) -> str | None:
        """Get token from cache."""
        return self.token_cache.get(self._cache_key)

    def _cache_token(self, token: str) -> None:
        """Store token in cache."""
        self.token_cache.set(self._cache_key, token)

    def _run_oauth_flow(self) -> str:
        """Run the full OAuth flow: browser auth + token exchange.

        Returns:
            The access token

        Raises:
            TimeoutError: If authorization times out
            RuntimeError: If authorization fails
        """
        # Create callback handler class with result storage
        result = {"code": None, "error": None, "state": None}
        expected_state = secrets.token_urlsafe(16)

        class CallbackHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                parsed = urlparse(self.path)
                if parsed.path == "/callback":
                    params = parse_qs(parsed.query)

                    if "error" in params:
                        result["error"] = params["error"][0]
                        self._send_response("Authorization failed. You can close this window.")
                    elif "code" in params:
                        result["code"] = params["code"][0]
                        result["state"] = params.get("state", [None])[0]
                        self._send_response("Authorization successful! You can close this window.")
                    else:
                        self._send_response("Invalid callback. Missing code parameter.", 400)
                else:
                    self.send_response(404)
                    self.end_headers()

            def _send_response(self, message: str, status: int = 200):
                self.send_response(status)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                html = f"<html><body><h1>{message}</h1></body></html>"
                self.wfile.write(html.encode())

            def log_message(self, format, *args):
                pass  # Suppress logging

        # Build authorization URL
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": self.scope,
            "state": expected_state,
        }
        auth_url = f"{self.AUTHORIZE_URL}?{urlencode(params)}"

        # Start callback server
        server = HTTPServer(("localhost", self.redirect_uri_port), CallbackHandler)
        server.timeout = self.timeout

        # Open browser
        if self.open_browser:
            webbrowser.open(auth_url)

        # Wait for callback
        server.handle_request()
        server.server_close()

        # Check result
        if result["error"]:
            raise RuntimeError(f"Authorization failed: {result['error']}")

        if not result["code"]:
            raise TimeoutError("Authorization timed out waiting for callback")

        if result["state"] != expected_state:
            raise RuntimeError("State mismatch - possible CSRF attack")

        # Exchange code for token
        response = httpx.post(
            self.TOKEN_URL,
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": result["code"],
                "redirect_uri": self.redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        response.raise_for_status()

        access_token = response.json()["access_token"]
        self._cache_token(access_token)

        return access_token

    def _ensure_token(self) -> str:
        """Ensure we have a valid token, running OAuth flow if needed."""
        # Fast path: check cache without lock
        cached = self._get_cached_token()
        if cached:
            return cached

        # Slow path: acquire lock and run OAuth flow
        with self._lock:
            # Double-check after acquiring lock
            cached = self._get_cached_token()
            if cached:
                return cached

            return self._run_oauth_flow()

    def auth_flow(self, request: httpx.Request):
        """Add Authorization header to request.

        This is called by httpx for each request. On the first request,
        it will trigger the OAuth flow (opening browser, etc).
        """
        token = self._ensure_token()
        request.headers["Authorization"] = f"Bearer {token}"
        yield request

    def clear_token(self) -> None:
        """Clear the cached token, forcing re-authentication on next request."""
        self.token_cache.clear(self._cache_key)


class ClientCredentials(httpx.Auth):
    """Client credentials authentication for Product Hunt API.

    This provides read-only access to public endpoints without requiring
    user authorization. Use this for server-side applications that don't
    need user context.

    Note: Client-level tokens cannot access user-specific data. Fields like
    `isVoted`, `viewer`, etc. will return default values (false, null).

    Example:
        ```python
        from producthunt_sdk import ProductHuntClient, ClientCredentials

        # Simple setup - no browser required
        client = ProductHuntClient(auth=ClientCredentials(
            client_id="your_client_id",
            client_secret="your_client_secret",
        ))

        # Access public data
        posts = client.get_posts(featured=True)
        for post in posts.nodes:
            print(f"{post.name}: {post.votes_count} votes")

        # Note: user-specific fields return defaults
        print(post.is_voted)  # Always False with client credentials
        ```
    """

    TOKEN_URL = "https://api.producthunt.com/v2/oauth/token"

    # Class-level cache and lock (shared across all instances)
    token_cache = TokenCache()
    _lock = threading.Lock()

    def __init__(self, client_id: str, client_secret: str):
        """Initialize client credentials authentication.

        Args:
            client_id: Your OAuth application client ID
            client_secret: Your OAuth application client secret
        """
        self.client_id = client_id
        self.client_secret = client_secret

        # Generate cache key from credentials
        self._cache_key = hashlib.sha256(
            f"client_credentials:{client_id}:{client_secret}".encode()
        ).hexdigest()[:16]

    def _get_cached_token(self) -> str | None:
        """Get token from cache."""
        return self.token_cache.get(self._cache_key)

    def _cache_token(self, token: str) -> None:
        """Store token in cache."""
        self.token_cache.set(self._cache_key, token)

    def _fetch_token(self) -> str:
        """Fetch a new client credentials token.

        Returns:
            The access token

        Raises:
            httpx.HTTPStatusError: If token request fails
        """
        response = httpx.post(
            self.TOKEN_URL,
            json={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials",
            },
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )
        response.raise_for_status()

        access_token = response.json()["access_token"]
        self._cache_token(access_token)

        return access_token

    def _ensure_token(self) -> str:
        """Ensure we have a valid token, fetching one if needed."""
        # Fast path: check cache without lock
        cached = self._get_cached_token()
        if cached:
            return cached

        # Slow path: acquire lock and fetch token
        with self._lock:
            # Double-check after acquiring lock
            cached = self._get_cached_token()
            if cached:
                return cached

            return self._fetch_token()

    def auth_flow(self, request: httpx.Request):
        """Add Authorization header to request."""
        token = self._ensure_token()
        request.headers["Authorization"] = f"Bearer {token}"
        yield request

    def clear_token(self) -> None:
        """Clear the cached token, forcing a new token fetch on next request."""
        self.token_cache.clear(self._cache_key)
