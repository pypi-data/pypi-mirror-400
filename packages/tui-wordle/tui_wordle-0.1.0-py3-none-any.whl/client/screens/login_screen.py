"""Login screen with Google OAuth support."""

import asyncio
import webbrowser
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from threading import Thread
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button
from textual.containers import Container
from textual.binding import Binding
from rich.text import Text

from client.api_client import get_api_client
from client.config import ClientConfig


def find_free_port() -> int:
    """Find a free port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler for OAuth callback."""

    def log_message(self, format, *args):
        pass  # Suppress logging

    def do_GET(self):
        """Handle GET request from OAuth redirect."""
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        self.server.auth_code = params.get("code", [None])[0]
        self.server.auth_state = params.get("state", [None])[0]
        self.server.auth_error = params.get("error", [None])[0]

        # Send response to browser
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        if self.server.auth_code:
            html = """
            <html><body style="font-family: sans-serif; text-align: center; padding: 50px;">
            <h1>Login Successful!</h1>
            <p>You can close this window and return to the terminal.</p>
            </body></html>
            """
        else:
            html = """
            <html><body style="font-family: sans-serif; text-align: center; padding: 50px;">
            <h1>Login Failed</h1>
            <p>Please try again in the terminal.</p>
            </body></html>
            """
        self.wfile.write(html.encode())


class LoginScreen(Screen):
    """Login screen with Google OAuth and offline mode."""

    BINDINGS = [
        Binding("escape", "quit", "Quit"),
        Binding("enter", "submit", "Login", show=False),
    ]

    CSS = """
    LoginScreen {
        background: #121213;
        align: center middle;
    }

    #login-container {
        width: 56;
        height: auto;
        background: #1a1a1b;
        border: solid #3a3a3c;
        padding: 2;
    }

    #login-title {
        width: 100%;
        height: 5;
        content-align: center middle;
    }

    #login-subtitle {
        width: 100%;
        height: 2;
        content-align: center middle;
        color: #818384;
    }

    #google-section {
        width: 100%;
        height: auto;
        padding: 1 0;
    }

    #google-button {
        width: 100%;
    }

    #google-status {
        width: 100%;
        height: auto;
        min-height: 3;
        content-align: center middle;
        padding: 1;
        margin-top: 1;
    }

    #divider {
        width: 100%;
        height: 1;
        content-align: center middle;
        color: #3a3a3c;
        margin: 1 0;
    }

    #offline-section {
        width: 100%;
        height: auto;
    }

    #offline-hint {
        width: 100%;
        height: 1;
        color: #565758;
    }

    #offline-button {
        width: 100%;
        margin-top: 1;
    }

    #server-status {
        width: 100%;
        height: 1;
        content-align: center middle;
        color: #565758;
        margin-top: 2;
    }
    """

    def __init__(self, api_url: str = "http://localhost:8000", **kwargs) -> None:
        super().__init__(**kwargs)
        self.api_url = api_url
        self.server_online = False
        self.google_available = False
        self._config = ClientConfig()
        self._oauth_state = None

    def compose(self) -> ComposeResult:
        with Container(id="login-container"):
            yield Static(id="login-title")
            yield Static("[#818384]Play Wordle every day![/]", id="login-subtitle")

            with Container(id="google-section"):
                yield Button("Login with Google", id="google-button", variant="primary")
                yield Static(id="google-status")

            yield Static("[#3a3a3c]─────────── or ───────────[/]", id="divider")

            with Container(id="offline-section"):
                yield Static("[#565758]Play without an account[/]", id="offline-hint")
                yield Button("Play Offline", id="offline-button", variant="default")

            yield Static(id="server-status")

    def on_mount(self) -> None:
        self._render_title()
        asyncio.create_task(self._check_server())

    def _render_title(self) -> None:
        title = self.query_one("#login-title", Static)
        logo = """[bold white]╦ ╦╔═╗╦═╗╔╦╗╦  ╔═╗
║║║║ ║╠╦╝ ║║║  ║╣
╚╩╝╚═╝╩╚══╩╝╩═╝╚═╝[/]"""
        title.update(Text.from_markup(logo))

    async def _check_server(self) -> None:
        """Check if server is available and Google OAuth is configured."""
        status = self.query_one("#server-status", Static)
        status.update(Text.from_markup("[#c9b458]Checking server...[/]"))

        client = get_api_client(self.api_url)
        self.server_online = await client.health_check()

        if self.server_online:
            status.update(Text.from_markup("[#6aaa64]● Server online[/]"))
            # Check if Google OAuth is available
            try:
                response = await client._client.get(
                    f"{self.api_url}/auth/google/status",
                    timeout=5.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    self.google_available = data.get("configured", False)
            except Exception:
                self.google_available = False

            if not self.google_available:
                google_btn = self.query_one("#google-button", Button)
                google_btn.disabled = True
                google_btn.label = "Google Login (Not configured)"
        else:
            status.update(Text.from_markup("[#787c7e]○ Server offline[/]"))
            google_btn = self.query_one("#google-button", Button)
            google_btn.disabled = True
            google_btn.label = "Google Login (Server offline)"

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "google-button":
            await self._start_google_login()
        elif event.button.id == "offline-button":
            self._play_offline()

    async def _start_google_login(self) -> None:
        """Start Google OAuth flow with localhost redirect."""
        if not self.server_online or not self.google_available:
            return

        google_status = self.query_one("#google-status", Static)
        google_status.update(Text.from_markup("[#c9b458]Opening browser...[/]"))

        client = get_api_client(self.api_url)

        try:
            # Use fixed port for OAuth callback (must be registered in Google Console)
            port = 9876
            redirect_uri = f"http://localhost:{port}/callback"

            # Get auth URL from server
            response = await client._client.get(
                f"{self.api_url}/auth/google/auth-url",
                params={"redirect_uri": redirect_uri},
            )

            if response.status_code != 200:
                google_status.update(Text.from_markup("[#787c7e]Failed to start login[/]"))
                return

            data = response.json()
            auth_url = data["auth_url"]
            self._oauth_state = data["state"]

            # Start local HTTP server to receive callback
            server = HTTPServer(("localhost", port), OAuthCallbackHandler)
            server.auth_code = None
            server.auth_state = None
            server.auth_error = None
            server.timeout = 120  # 2 minutes timeout

            google_status.update(Text.from_markup(
                "[#c9b458]Waiting for Google login...[/]\n"
                "[#565758]A browser window should open.[/]"
            ))

            # Open browser
            webbrowser.open(auth_url)

            # Wait for callback in a thread
            def wait_for_callback():
                server.handle_request()

            thread = Thread(target=wait_for_callback, daemon=True)
            thread.start()

            # Poll for result
            for _ in range(120):  # 2 minutes max
                await asyncio.sleep(1)
                if server.auth_code or server.auth_error:
                    break

            if server.auth_error:
                google_status.update(Text.from_markup(
                    f"[#787c7e]Login cancelled or failed[/]"
                ))
                return

            if not server.auth_code:
                google_status.update(Text.from_markup("[#787c7e]Login timed out[/]"))
                return

            # Exchange code for token
            google_status.update(Text.from_markup("[#c9b458]Completing login...[/]"))

            callback_response = await client._client.post(
                f"{self.api_url}/auth/google/callback",
                json={
                    "code": server.auth_code,
                    "state": server.auth_state,
                    "redirect_uri": redirect_uri,
                },
            )

            if callback_response.status_code != 200:
                google_status.update(Text.from_markup("[#787c7e]Failed to complete login[/]"))
                return

            result = callback_response.json()

            if result.get("success"):
                # Save token locally
                self._config.save(result["username"], result["token"])

                google_status.update(Text.from_markup(
                    f"[bold #6aaa64]✓ Welcome, {result['username']}![/]"
                ))
                await asyncio.sleep(1)
                self.dismiss({
                    "username": result["username"],
                    "token": result["token"],
                    "streak": 0,
                })
            else:
                google_status.update(Text.from_markup(
                    f"[#787c7e]{result.get('error', 'Login failed')}[/]"
                ))

        except Exception as e:
            google_status.update(Text.from_markup(f"[#787c7e]Error: {str(e)}[/]"))

    def _play_offline(self) -> None:
        """Start offline game."""
        self.dismiss({"username": "Player", "token": None, "streak": 0})

    def action_submit(self) -> None:
        self._play_offline()

    def action_quit(self) -> None:
        self.app.exit()
