"""
OAuth2 browser-based authentication for Baseshift CLI.

Implements the OAuth2 authorization code flow:
1. Start local HTTP server to receive callback
2. Open browser to DMS OAuth authorize URL
3. User logs in via browser
4. Receive authorization code via callback
5. Exchange code for JWT tokens
"""

import logging
import secrets
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlencode, urlparse, parse_qs
import threading
import httpx

from .auth_token import get_token_manager

logger = logging.getLogger(__name__)

# Suppress httpx request logging during OAuth
httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)

# Default port for local callback server
CALLBACK_PORT = 8085


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP request handler for OAuth callback."""

    # Class variable to store authorization code
    authorization_code = None
    state = None
    error = None

    def log_message(self, format, *args):
        """Override to suppress default logging."""
        pass

    def do_GET(self):
        """Handle GET request to callback URL."""
        # Parse query parameters
        parsed_path = urlparse(self.path)
        params = parse_qs(parsed_path.query)

        # Extract code and state
        code = params.get("code", [None])[0]
        state = params.get("state", [None])[0]
        error = params.get("error", [None])[0]

        if error:
            OAuthCallbackHandler.error = error
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"""
                <html>
                <head><title>Authentication Error</title></head>
                <body style="font-family: sans-serif; text-align: center; padding: 50px;">
                    <h1>Authentication Error</h1>
                    <p>An error occurred during authentication. Please try again.</p>
                    <p>You can close this window.</p>
                </body>
                </html>
            """
            )
        elif code:
            OAuthCallbackHandler.authorization_code = code
            OAuthCallbackHandler.state = state

            # Send success response
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Authentication Successful - Baseshift</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@600&family=Roboto:wght@400&display=swap" rel="stylesheet">
    <style>
        * {
            box-sizing: border-box;
        }
        body {
            font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            background: #eef3ff;
        }
        .container {
            background: white;
            border-radius: 8px;
            padding: 40px;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 20px;
            box-shadow: 2px 2px 20px 0px rgba(0, 0, 0, 0.16);
        }
        .success-icon {
            width: 50px;
            height: 50px;
        }
        .text-content {
            display: flex;
            flex-direction: column;
            gap: 30px;
            align-items: center;
        }
        .top-section {
            display: flex;
            flex-direction: column;
            gap: 20px;
            align-items: center;
            text-align: center;
        }
        h1 {
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            font-size: 30px;
            color: #0e0e0f;
            margin: 0;
            line-height: 1;
        }
        .description {
            font-family: 'Roboto', sans-serif;
            font-size: 16px;
            color: #4a4a4a;
            margin: 0;
            line-height: 1;
            padding: 0 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="success-icon">
            <svg width="50" height="50" viewBox="0 0 50 50" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="25" cy="25" r="25" fill="#7ED321"/>
                <path fill-rule="evenodd" clip-rule="evenodd" d="M36.5278 16.9097C37.1991 17.5809 37.1991 18.6691 36.5278 19.3403L22.7778 33.0903C22.1066 33.7616 21.0184 33.7616 20.3472 33.0903L13.4722 26.2153C12.8009 25.5441 12.8009 24.4559 13.4722 23.7847C14.1434 23.1134 15.2316 23.1134 15.9028 23.7847L21.5625 29.4443L34.0972 16.9097C34.7684 16.2384 35.8566 16.2384 36.5278 16.9097Z" fill="white"/>
            </svg>
        </div>
        <div class="text-content">
            <div class="top-section">
                <h1>Authentication successful</h1>
                <p class="description">You can close this tab to return to your terminal.</p>
            </div>
        </div>
    </div>
</body>
</html>"""
            )
        else:
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"""
                <html>
                <head><title>Invalid Request</title></head>
                <body style="font-family: sans-serif; text-align: center; padding: 50px;">
                    <h1>Invalid Request</h1>
                    <p>No authorization code received. Please try again.</p>
                </body>
                </html>
            """
            )


def oauth_login(host: str, port: int = CALLBACK_PORT, timeout: int = 120):
    """
    Perform OAuth2 browser-based login.

    Args:
        host: API host URL
        port: Local port for callback server (default 8085)
        timeout: Timeout in seconds to wait for user to complete login

    Returns:
        True if login successful, False otherwise
    """
    # Generate state parameter for CSRF protection
    state = secrets.token_urlsafe(32)

    # Callback URL
    redirect_uri = f"http://localhost:{port}/callback"

    # Build authorization URL
    auth_params = {
        "redirect_uri": redirect_uri,
        "state": state,
        "prompt": "consent",  # Force approval screen even if already logged in
    }
    auth_url = f"{host}/api/v2/oauth/authorize?{urlencode(auth_params)}"

    # Reset class variables
    OAuthCallbackHandler.authorization_code = None
    OAuthCallbackHandler.state = None
    OAuthCallbackHandler.error = None

    # Start local HTTP server
    try:
        server = HTTPServer(("localhost", port), OAuthCallbackHandler)
    except OSError as e:
        logger.error(f"Failed to start callback server on port {port}: {e}")
        print(
            f"Error: Could not start local server on port {port}. Is it already in use?"
        )
        return False

    # Start server in background thread
    server_thread = threading.Thread(target=server.handle_request, daemon=True)
    server_thread.start()

    print(f"\n🔐 Opening browser for authentication...")
    print(f"If browser doesn't open automatically, visit: {auth_url}\n")

    # Open browser
    try:
        webbrowser.open(auth_url)
    except Exception as e:
        logger.warning(f"Failed to open browser automatically: {e}")
        print(f"Please open this URL manually: {auth_url}")

    print("⏳ Waiting for authentication...")

    # Wait for callback with timeout
    server_thread.join(timeout=timeout)

    # Check if we received authorization code
    if OAuthCallbackHandler.error:
        print(f"❌ Authentication failed: {OAuthCallbackHandler.error}")
        return False

    if not OAuthCallbackHandler.authorization_code:
        print("❌ Authentication timed out or was cancelled.")
        server.server_close()
        return False

    # Verify state matches
    if OAuthCallbackHandler.state != state:
        logger.error("State mismatch - possible CSRF attack")
        print("❌ Authentication failed: Security verification failed.")
        server.server_close()
        return False

    auth_code = OAuthCallbackHandler.authorization_code

    print("✅ Authorization received, exchanging for access token...")

    # Exchange authorization code for tokens
    try:
        with httpx.Client() as client:
            response = client.post(
                f"{host}/api/v2/oauth/token",
                json={
                    "grant_type": "authorization_code",
                    "code": auth_code,
                    "redirect_uri": redirect_uri,
                },
                timeout=30.0,
            )

            if response.status_code == 200:
                data = response.json()
                access_token = data["access_token"]
                refresh_token = data["refresh_token"]
                expires_in = data.get("expires_in", 3600)
                user_info = data.get("user", {})

                # Save tokens
                token_manager = get_token_manager()
                token_manager.save_tokens(access_token, refresh_token, expires_in)

                print(
                    f"✅ Successfully authenticated as {user_info.get('email', 'unknown')}"
                )
                return True
            else:
                logger.error(
                    f"Token exchange failed: {response.status_code} {response.text}"
                )
                print(f"❌ Failed to obtain access token: {response.text}")
                return False

    except Exception as e:
        logger.error(f"Token exchange failed: {e}")
        print(f"❌ Failed to obtain access token: {e}")
        return False
    finally:
        server.server_close()


def direct_login(host: str, username: str, password: str):
    """
    Perform direct username/password login.

    Args:
        host: API host URL
        username: Username or email
        password: Password

    Returns:
        True if login successful, False otherwise
    """
    try:
        with httpx.Client() as client:
            response = client.post(
                f"{host}/api/v2/token",
                json={
                    "username": username,
                    "password": password,
                },
                timeout=30.0,
            )

            if response.status_code == 200:
                data = response.json()
                access_token = data["access"]
                refresh_token = data["refresh"]

                # Save tokens (default expiration 1 hour)
                token_manager = get_token_manager()
                token_manager.save_tokens(access_token, refresh_token, 3600)

                print(f"✅ Successfully authenticated as {username}")
                return True
            else:
                logger.error(f"Login failed: {response.status_code} {response.text}")
                print(f"❌ Authentication failed: Invalid credentials")
                return False

    except Exception as e:
        logger.error(f"Login failed: {e}")
        print(f"❌ Authentication failed: {e}")
        return False
