"""CLI authentication and credential management.

Handles storing/loading credentials from ~/.wafer/credentials.json
and verifying tokens against the wafer-api.
"""

import json
import socket
import webbrowser
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import httpx

from .api_client import get_api_url

# Default Supabase project URL (can be overridden)
DEFAULT_SUPABASE_URL = "https://auth.wafer.ai"

CREDENTIALS_DIR = Path.home() / ".wafer"
CREDENTIALS_FILE = CREDENTIALS_DIR / "credentials.json"


@dataclass
class Credentials:
    """Stored credentials."""

    access_token: str
    email: str | None = None


@dataclass
class UserInfo:
    """User info from token verification."""

    user_id: str
    email: str | None


def save_credentials(token: str, email: str | None = None) -> None:
    """Save credentials to ~/.wafer/credentials.json."""
    CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
    data = {"access_token": token}
    if email:
        data["email"] = email
    CREDENTIALS_FILE.write_text(json.dumps(data, indent=2))
    # Set restrictive permissions (owner read/write only)
    CREDENTIALS_FILE.chmod(0o600)


def load_credentials() -> Credentials | None:
    """Load credentials from ~/.wafer/credentials.json.

    Returns None if file doesn't exist or is invalid.
    """
    if not CREDENTIALS_FILE.exists():
        return None
    try:
        data = json.loads(CREDENTIALS_FILE.read_text())
        return Credentials(
            access_token=data["access_token"],
            email=data.get("email"),
        )
    except (json.JSONDecodeError, KeyError):
        return None


def clear_credentials() -> bool:
    """Remove credentials file.

    Returns True if file was removed, False if it didn't exist.
    """
    if CREDENTIALS_FILE.exists():
        CREDENTIALS_FILE.unlink()
        return True
    return False


def get_auth_headers() -> dict[str, str]:
    """Get Authorization headers if credentials exist.

    Returns empty dict if not logged in.
    """
    creds = load_credentials()
    if creds:
        return {"Authorization": f"Bearer {creds.access_token}"}
    return {}


def verify_token(token: str) -> UserInfo:
    """Verify token with wafer-api and return user info.

    Raises:
        httpx.HTTPStatusError: If token is invalid (401) or other HTTP error
        httpx.RequestError: If API is unreachable
    """
    api_url = get_api_url()
    with httpx.Client(timeout=10.0) as client:
        response = client.post(
            f"{api_url}/v1/auth/verify",
            json={"token": token},
        )
        response.raise_for_status()
        data = response.json()
        return UserInfo(
            user_id=data["user_id"],
            email=data.get("email"),
        )


def _find_free_port() -> int:
    """Find a free port for the callback server."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def get_supabase_url() -> str:
    """Get Supabase URL from environment or default."""
    import os

    return os.environ.get("SUPABASE_URL", DEFAULT_SUPABASE_URL)


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler that catches the OAuth callback with access token."""

    access_token: str | None = None
    error: str | None = None

    def log_message(self, format: str, *args: object) -> None:
        """Suppress default logging."""
        pass

    def do_GET(self) -> None:
        """Handle GET request - catch the callback or serve the HTML page."""
        parsed = urlparse(self.path)

        if parsed.path == "/callback":
            # This is the redirect from Supabase with hash fragment
            # But hash fragments aren't sent to server, so serve a page that extracts it
            html = """<!DOCTYPE html>
<html>
<head><title>Wafer CLI Login</title></head>
<body>
<h2>Completing login...</h2>
<script>
// Extract token from hash fragment
const hash = window.location.hash.substring(1);
const params = new URLSearchParams(hash);
const accessToken = params.get('access_token');
const error = params.get('error_description') || params.get('error');

if (accessToken) {
    // Send token to our local server
    fetch('/token?access_token=' + encodeURIComponent(accessToken))
        .then(() => {
            document.body.innerHTML = '<h2>✓ Login successful!</h2><p>You can close this window.</p>';
        });
} else if (error) {
    fetch('/token?error=' + encodeURIComponent(error));
    document.body.innerHTML = '<h2>✗ Login failed</h2><p>' + error + '</p>';
} else {
    document.body.innerHTML = '<h2>✗ No token received</h2>';
}
</script>
</body>
</html>"""
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode())

        elif parsed.path == "/token":
            # JavaScript sends us the token
            params = parse_qs(parsed.query)
            if "access_token" in params:
                OAuthCallbackHandler.access_token = params["access_token"][0]
            elif "error" in params:
                OAuthCallbackHandler.error = params["error"][0]

            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")

        else:
            self.send_response(404)
            self.end_headers()


def browser_login(timeout: int = 120) -> str:
    """Open browser for GitHub OAuth and return access token.

    Starts a local HTTP server, opens browser to Supabase OAuth,
    and waits for the callback with the access token.

    Args:
        timeout: Seconds to wait for callback (default 120)

    Returns:
        Access token string

    Raises:
        TimeoutError: If no callback received within timeout
        RuntimeError: If OAuth flow failed
    """
    import time

    port = _find_free_port()
    redirect_uri = f"http://localhost:{port}/callback"
    supabase_url = get_supabase_url()

    # Build OAuth URL
    auth_url = (
        f"{supabase_url}/auth/v1/authorize"
        f"?provider=github"
        f"&redirect_to={redirect_uri}"
    )

    # Reset state
    OAuthCallbackHandler.access_token = None
    OAuthCallbackHandler.error = None

    # Start local server
    server = HTTPServer(("localhost", port), OAuthCallbackHandler)
    server.timeout = 1  # Check for token every second

    # Open browser
    print("Opening browser for GitHub authentication...")
    print(f"If browser doesn't open, visit: {auth_url}")
    webbrowser.open(auth_url)

    # Wait for callback
    start = time.time()
    print("Waiting for authentication...", end="", flush=True)

    while time.time() - start < timeout:
        server.handle_request()

        if OAuthCallbackHandler.access_token:
            print(" ✓")
            server.server_close()
            return OAuthCallbackHandler.access_token

        if OAuthCallbackHandler.error:
            print(" ✗")
            server.server_close()
            raise RuntimeError(f"OAuth failed: {OAuthCallbackHandler.error}")

    server.server_close()
    raise TimeoutError(f"No response within {timeout} seconds")
