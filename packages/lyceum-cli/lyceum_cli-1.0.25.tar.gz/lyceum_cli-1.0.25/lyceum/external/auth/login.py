"""Authentication commands: login, logout, status"""

import socket
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

import typer
from rich.console import Console

from ...shared.config import config

console = Console()

auth_app = typer.Typer(name="auth", help="Authentication commands")

# Global variables for callback server
callback_result = {"token": None, "error": None, "received": False}


class CallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler for OAuth callback"""

    def log_message(self, format, *args):
        """Suppress HTTP server logs"""
        pass

    def do_GET(self):
        """Handle GET request for OAuth callback"""
        global callback_result

        try:
            # Parse the callback URL
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)

            if parsed_url.path == "/callback":
                # Extract token from query parameters
                if "token" in query_params:
                    token = query_params["token"][0]
                    user_info = query_params.get("user", [None])[0]
                    refresh_token = query_params.get("refresh_token", [None])[0]

                    callback_result["token"] = token
                    callback_result["user"] = user_info
                    if refresh_token:
                        callback_result["refresh_token"] = refresh_token
                    callback_result["received"] = True

                    # Send success response
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()

                    success_html = """
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Lyceum CLI - Authentication Success</title>
                        <script src="https://cdn.tailwindcss.com"></script>
                    </head>
                    <body class="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
                        <div class="max-w-md w-full space-y-8">
                            <div class="bg-white rounded-lg shadow-md p-8 text-center">
                                <!-- Success Icon -->
                                <div class="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100 mb-6">
                                    <svg class="h-8 w-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                                    </svg>
                                </div>

                                <!-- Header -->
                                <div class="mb-6">
                                    <h1 class="text-2xl font-bold text-gray-900 mb-2">Authentication Successful!</h1>
                                    <p class="text-gray-600 text-lg">Welcome to Lyceum</p>
                                </div>

                                <!-- Instructions -->
                                <div class="space-y-3 mb-8">
                                    <p class="text-gray-700">You can now close this browser tab and return to the CLI.</p>
                                    <p class="text-sm text-gray-500">Your Lyceum CLI has been authenticated successfully and is ready to use.</p>
                                </div>

                                <!-- Close Message -->
                                <div class="w-full py-3 px-4 bg-gray-50 text-gray-700 rounded-md border border-gray-200">
                                    You can close this window now
                                </div>

                                <!-- Lyceum Branding -->
                                <div class="mt-8 pt-6 border-t border-gray-200">
                                    <p class="text-xs text-gray-400">Powered by Lyceum Technology</p>
                                </div>
                            </div>
                        </div>

                        <!-- Auto-close script -->
                        <script>
                            // Auto-close after 10 seconds
                            setTimeout(() => {
                                window.close();
                            }, 10000);
                        </script>
                    </body>
                    </html>
                    """
                    try:
                        self.wfile.write(success_html.encode())
                    except (BrokenPipeError, ConnectionResetError):
                        # Browser closed connection (expected when tab auto-closes)
                        pass

                elif "error" in query_params:
                    error = query_params["error"][0]
                    callback_result["error"] = error
                    callback_result["received"] = True

                    # Send error response
                    self.send_response(400)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()

                    error_html = f"""
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Lyceum CLI - Authentication Error</title>
                        <script src="https://cdn.tailwindcss.com"></script>
                    </head>
                    <body class="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
                        <div class="max-w-md w-full space-y-8">
                            <div class="bg-white rounded-lg shadow-md p-8 text-center">
                                <!-- Error Icon -->
                                <div class="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100 mb-6">
                                    <svg class="h-8 w-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                                    </svg>
                                </div>

                                <!-- Header -->
                                <div class="mb-6">
                                    <h1 class="text-2xl font-bold text-gray-900 mb-2">Authentication Failed</h1>
                                    <p class="text-red-600 text-lg">Something went wrong</p>
                                </div>

                                <!-- Error Details -->
                                <div class="space-y-3 mb-8">
                                    <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
                                        <p class="text-sm">{error}</p>
                                    </div>
                                    <p class="text-gray-600">Please try again or contact support if the issue persists.</p>
                                </div>

                                <!-- Close Message -->
                                <div class="w-full py-3 px-4 bg-gray-50 text-gray-700 rounded-md border border-gray-200">
                                    You can close this window now
                                </div>

                                <!-- Lyceum Branding -->
                                <div class="mt-8 pt-6 border-t border-gray-200">
                                    <p class="text-xs text-gray-400">Powered by Lyceum Technology</p>
                                </div>
                            </div>
                        </div>
                    </body>
                    </html>
                    """
                    try:
                        self.wfile.write(error_html.encode())
                    except (BrokenPipeError, ConnectionResetError):
                        # Browser closed connection
                        pass
                else:
                    # Missing parameters
                    callback_result["error"] = "Missing token or error parameter"
                    callback_result["received"] = True

                    self.send_response(400)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    invalid_html = """
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Lyceum CLI - Invalid Parameters</title>
                        <script src="https://cdn.tailwindcss.com"></script>
                    </head>
                    <body class="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
                        <div class="max-w-md w-full space-y-8">
                            <div class="bg-white rounded-lg shadow-md p-8 text-center">
                                <div class="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-yellow-100 mb-6">
                                    <svg class="h-8 w-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L3.268 16c-.77.833.192 2.5 1.732 2.5z"></path>
                                    </svg>
                                </div>
                                <h1 class="text-2xl font-bold text-gray-900 mb-2">Invalid Parameters</h1>
                                <p class="text-gray-600 mb-8">The authentication callback received invalid parameters.</p>
                                <div class="w-full py-3 px-4 bg-gray-50 text-gray-700 rounded-md border border-gray-200">
                                    You can close this window now
                                </div>
                            </div>
                        </div>
                    </body>
                    </html>
                    """
                    try:
                        self.wfile.write(invalid_html.encode())
                    except (BrokenPipeError, ConnectionResetError):
                        # Browser closed connection
                        pass
            else:
                # Invalid path
                self.send_response(404)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                notfound_html = """
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Lyceum CLI - Page Not Found</title>
                    <script src="https://cdn.tailwindcss.com"></script>
                </head>
                <body class="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
                    <div class="max-w-md w-full space-y-8">
                        <div class="bg-white rounded-lg shadow-md p-8 text-center">
                            <div class="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-gray-100 mb-6">
                                <svg class="h-8 w-8 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0112 15c-2.34 0-4.419-1.007-5.866-2.609C6.107 12.398 6 12.202 6 12s.107-.398.134-.609C7.581 10.007 9.66 9 12 9s4.419 1.007 5.866 2.609c.027.203.134.4.134.609s-.107.406-.134.609A7.962 7.962 0 0117 15z"></path>
                                </svg>
                            </div>
                            <h1 class="text-2xl font-bold text-gray-900 mb-2">Page Not Found</h1>
                            <p class="text-gray-600 mb-8">The requested page could not be found.</p>
                            <div class="w-full py-3 px-4 bg-gray-50 text-gray-700 rounded-md border border-gray-200">
                                You can close this window now
                            </div>
                        </div>
                    </div>
                </body>
                </html>
                """
                try:
                    self.wfile.write(notfound_html.encode())
                except (BrokenPipeError, ConnectionResetError):
                    # Browser closed connection
                    pass

        except Exception as e:
            callback_result["error"] = str(e)
            callback_result["received"] = True

            self.send_response(500)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            server_error_html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Lyceum CLI - Server Error</title>
                <script src="https://cdn.tailwindcss.com"></script>
            </head>
            <body class="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
                <div class="max-w-md w-full space-y-8">
                    <div class="bg-white rounded-lg shadow-md p-8 text-center">
                        <div class="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100 mb-6">
                            <svg class="h-8 w-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                        </div>
                        <h1 class="text-2xl font-bold text-gray-900 mb-2">Server Error</h1>
                        <p class="text-red-600 mb-4">An unexpected error occurred</p>
                        <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md mb-8">
                            <p class="text-sm">{e}</p>
                        </div>
                        <div class="w-full py-3 px-4 bg-gray-50 text-gray-700 rounded-md border border-gray-200">
                            You can close this window now
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            try:
                self.wfile.write(server_error_html.encode())
            except (BrokenPipeError, ConnectionResetError):
                # Browser closed connection
                pass


def get_available_port():
    """Find an available port for the callback server"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


@auth_app.command("login")
def login(
    base_url: str | None = typer.Option(None, "--url", help="API base URL (for development)"),
    dashboard_url: str | None = typer.Option(
        "https://dashboard.lyceum.technology", "--dashboard", help="Dashboard URL"
    ),
    manual: bool = typer.Option(
        False, "--manual", help="Use manual API key login instead of browser"
    ),
    api_key: str | None = typer.Option(
        None, "--api-key", "-k", help="API key for manual login"
    ),
):
    """Login to Lyceum via browser authentication"""
    global callback_result

    if manual:
        # Legacy manual login
        if not api_key:
            api_key = typer.prompt("Enter your Lyceum API key", hide_input=True)

        config.api_key = api_key
        if base_url:
            config.base_url = base_url
        config.save()

        # Test the connection
        try:
            import httpx
            headers = {"Authorization": f"Bearer {config.api_key}"}
            response = httpx.get(f"{config.base_url}/api/v2/external/machine-types", headers=headers, timeout=10.0)
            if response.status_code == 200:
                console.print("[green]✅ Successfully authenticated![/green]")
            else:
                console.print(f"[red]❌ Authentication failed: HTTP {response.status_code}[/red]")
                raise typer.Exit(1)
        except Exception as e:
            console.print(f"[red]❌ Authentication failed: {e}[/red]")
            raise typer.Exit(1)
        return

    # OAuth-style browser login
    try:
        if base_url:
            config.base_url = base_url
        else:
            # Reset to production URL if no custom URL specified
            config.base_url = "https://api.lyceum.technology"

        # Reset callback result
        callback_result = {"token": None, "error": None, "received": False}

        # Start callback server
        callback_port = get_available_port()
        callback_server = HTTPServer(('localhost', callback_port), CallbackHandler)

        console.print(f"[dim]Starting callback server on port {callback_port}...[/dim]")

        # Start server in background thread
        server_thread = threading.Thread(target=callback_server.serve_forever, daemon=True)
        server_thread.start()

        # Construct login URL
        callback_url = f"http://localhost:{callback_port}/callback"
        login_url = f"{dashboard_url}/cli-login?callback={callback_url}"

        console.print("[cyan]🌐 Opening browser for authentication...[/cyan]")
        console.print(f"[dim]If browser doesn't open, visit: {login_url}[/dim]")

        # Open browser
        if not webbrowser.open(login_url):
            console.print("[yellow]⚠️  Could not open browser automatically[/yellow]")
            console.print(f"[yellow]Please manually open: {login_url}[/yellow]")

        console.print("[dim]Waiting for authentication... (timeout: 120 seconds)[/dim]")

        # Wait for callback with timeout
        timeout = 120  # 2 minutes
        start_time = time.time()

        while not callback_result["received"] and (time.time() - start_time) < timeout:
            time.sleep(0.5)

        # Stop server
        callback_server.shutdown()
        callback_server.server_close()

        if callback_result["received"]:
            if callback_result["token"]:
                # Save token and test connection
                config.api_key = callback_result["token"]
                # Also save refresh_token if provided
                if callback_result.get("refresh_token"):
                    config.refresh_token = callback_result["refresh_token"]
                config.save()

                console.print("[green]✅ Authentication token received![/green]")

                # Test the connection using health endpoint
                try:
                    import httpx
                    headers = {"Authorization": f"Bearer {config.api_key}"}

                    # Create client with explicit timeout and SSL verification
                    client = httpx.Client(timeout=30.0, verify=True)
                    try:
                        response = client.get(
                            f"{config.base_url}/api/v2/external/machine-types",
                            headers=headers
                        )
                        if response.status_code == 200:
                            console.print("[green]✅ Successfully authenticated![/green]")
                            if callback_result.get("user"):
                                console.print(f"[dim]Logged in as: {callback_result['user']}[/dim]")
                        else:
                            console.print(f"[red]❌ Token validation failed: HTTP {response.status_code}[/red]")
                            console.print(f"[dim]Response: {response.text}[/dim]")
                            raise typer.Exit(1)
                    finally:
                        client.close()
                except httpx.TimeoutException as e:
                    console.print(f"[yellow]⚠️  Token validation timed out: {e}[/yellow]")
                    console.print(f"[yellow]Token saved but couldn't verify connectivity to {config.base_url}[/yellow]")
                    console.print("[dim]You can test the connection later with 'lyceum auth status'[/dim]")
                    # Don't exit with error - token was received successfully
                except Exception as e:
                    console.print(f"[red]❌ Token validation failed: {e}[/red]")
                    console.print(f"[dim]Token saved but couldn't verify. Error type: {type(e).__name__}[/dim]")
                    raise typer.Exit(1)

            elif callback_result["error"]:
                console.print(f"[red]❌ Authentication failed: {callback_result['error']}[/red]")
                raise typer.Exit(1)
        else:
            console.print("[red]❌ Authentication timed out. Please try again.[/red]")
            raise typer.Exit(1)

    except KeyboardInterrupt:
        console.print("\n[yellow]Authentication cancelled by user.[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]❌ Authentication error: {e}[/red]")
        raise typer.Exit(1)


@auth_app.command("logout")
def logout():
    """Logout and remove stored credentials"""
    from ...shared.config import CONFIG_FILE
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()
    console.print("[green]✅ Logged out successfully![/green]")


@auth_app.command("status")
def status():
    """Show current configuration and authentication status"""
    from ...shared.config import CONFIG_FILE
    console.print(f"[dim]Config file: {CONFIG_FILE}[/dim]")
    console.print(f"[dim]Base URL: {config.base_url}[/dim]")

    if config.api_key:
        console.print("[green]✅ Authenticated[/green]")
        console.print(f"[dim]API Key: {config.api_key[:8]}...[/dim]")

        # Test connection
        try:
            import httpx
            headers = {"Authorization": f"Bearer {config.api_key}"}
            response = httpx.get(f"{config.base_url}/api/v2/external/machine-types", headers=headers, timeout=10.0)
            if response.status_code == 200:
                console.print("[green]✅ API connection working[/green]")
            else:
                console.print(f"[yellow]⚠️  API connection issues: HTTP {response.status_code}[/yellow]")
        except Exception as e:
            console.print(f"[red]❌ API connection failed: {e}[/red]")
    else:
        console.print("[red]❌ Not authenticated. Run 'lyceum login' first.[/red]")
