"""
Authentication commands for Baseshift CLI.

Provides login, logout, and status commands for JWT authentication.
"""

import argparse
import getpass
import logging
from .base import BaseCommand
from ..auth_oauth import oauth_login, direct_login
from ..auth_token import get_token_manager


class AuthCommand(BaseCommand):
    """Authentication management commands."""

    def add_arguments(self, parser):
        """Add authentication subcommands."""
        auth_subparsers = parser.add_subparsers(dest="action", required=True)

        # Login command
        login_parser = auth_subparsers.add_parser("login", help="Login to Baseshift")
        login_parser.add_argument(
            "--method",
            choices=["browser", "direct"],
            default="browser",
            help="Authentication method: browser (OAuth) or direct (username/password)",
        )
        login_parser.add_argument(
            "--username", help="Username or email for direct login"
        )
        login_parser.add_argument(
            "--password", help="Password for direct login (will prompt if not provided)"
        )
        login_parser.add_argument(
            "--port",
            type=int,
            default=8085,
            help="Local port for OAuth callback (default: 8085)",
        )

        # Logout command
        auth_subparsers.add_parser("logout", help="Logout and clear stored tokens")

        # Status command
        auth_subparsers.add_parser("status", help="Check authentication status")

    def run(self, args, host):
        """Execute authentication command."""
        if args.action == "login":
            self.handle_login(args, host)
        elif args.action == "logout":
            self.handle_logout(args, host)
        elif args.action == "status":
            self.handle_status(args, host)

    def handle_login(self, args, host):
        """Handle login command."""
        # Suppress httpx logging during auth check
        httpx_logger = logging.getLogger("httpx")
        original_level = httpx_logger.level
        httpx_logger.setLevel(logging.WARNING)

        token_manager = get_token_manager()

        # Check if already logged in with valid tokens
        if token_manager.is_authenticated():
            # Try to get a valid token (this will attempt refresh if needed)
            valid_token = token_manager.get_valid_access_token(host)
            if valid_token:
                httpx_logger.setLevel(original_level)
                print("ℹ️  You are already logged in.")
                print(
                    "Use 'baseshift auth logout' to logout first if you want to login as a different user."
                )
                return
            else:
                # Tokens exist but are invalid/expired - clear silently and proceed with login
                token_manager.clear_tokens(silent=True)

        # Restore httpx logging
        httpx_logger.setLevel(original_level)

        if args.method == "browser":
            # Browser-based OAuth login
            print("🔐 Starting browser-based authentication...")
            success = oauth_login(host, port=args.port)
            if not success:
                print("\n💡 Tip: You can also use direct login with --method=direct")
        else:
            # Direct username/password login
            username = args.username
            if not username:
                username = input("Username or email: ")

            password = args.password
            if not password:
                password = getpass.getpass("Password: ")

            success = direct_login(host, username, password)

    def handle_logout(self, args, host):
        """Handle logout command."""
        token_manager = get_token_manager()

        if not token_manager.is_authenticated():
            print("ℹ️  You are not logged in.")
            return

        token_manager.clear_tokens()
        print("✅ Successfully logged out.")

    def handle_status(self, args, host):
        """Handle status command."""
        import httpx

        token_manager = get_token_manager()

        if not token_manager.is_authenticated():
            print("❌ Not authenticated")
            print("\nUse 'baseshift auth login' to authenticate.")
            return

        # Get auth header
        auth_header = token_manager.get_auth_header(host)

        if not auth_header:
            print("❌ Authentication expired or invalid")
            print("\nUse 'baseshift auth login' to re-authenticate.")
            return

        # Check with server
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{host}/api/v2/auth/status",
                    headers=auth_header,
                    timeout=10.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("authenticated"):
                        user = data.get("user", {})
                        print("✅ Authenticated")
                        print(f"\nUser: {user.get('email', 'unknown')}")
                        print(f"Username: {user.get('username', 'unknown')}")
                    else:
                        print("❌ Not authenticated")
                else:
                    print("❌ Authentication check failed")
                    print("\nUse 'baseshift auth login' to re-authenticate.")
        except Exception as e:
            print(f"❌ Failed to check authentication status: {e}")
