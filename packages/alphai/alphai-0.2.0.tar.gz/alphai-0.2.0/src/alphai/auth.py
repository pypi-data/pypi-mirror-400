"""Authentication management for alphai CLI."""

import os
import sys
import socket
import webbrowser
import urllib.parse
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional
import httpx
import questionary
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

from .config import Config
from .utils import get_logger
from . import exceptions

logger = get_logger(__name__)


class CallbackHandler(BaseHTTPRequestHandler):
    """HTTP request handler for OAuth callback."""
    
    def do_GET(self):
        """Handle GET request from OAuth callback."""
        # Parse the query parameters
        parsed_url = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        # Extract token from query parameters
        if 'token' in query_params:
            self.server.token = query_params['token'][0]
            self.send_response(302)  # Redirect
            
            # Get the API URL for redirection
            api_url = getattr(self.server, 'api_url', 'https://runalph.ai')
            
            # Try to use server-hosted success page first, fallback to direct redirect
            try:
                # Check if server has a success page
                success_url = f"{api_url}/auth/cli/success"
                with httpx.Client() as client:
                    response = client.head(success_url, timeout=2.0)
                    if response.status_code == 200:
                        # Server has a success page, use it
                        redirect_url = f"{success_url}?redirect_to={urllib.parse.quote(api_url)}"
                    else:
                        # No success page, redirect directly to dashboard
                        redirect_url = api_url
            except Exception:
                # Network error or timeout, redirect directly to dashboard
                redirect_url = api_url
            
            self.send_header('Location', redirect_url)
            self.end_headers()
            
        elif 'error' in query_params:
            self.server.error = query_params['error'][0]
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Simple error message for errors
            self.wfile.write(f'''
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Authentication Error</title>
                    <style>
                        body {{ font-family: system-ui; text-align: center; padding: 2rem; }}
                        .error {{ color: #ef4444; }}
                    </style>
                </head>
                <body>
                    <h1 class="error">Authentication Error</h1>
                    <p>Please return to your terminal and try again.</p>
                    <script>setTimeout(() => window.close(), 3000);</script>
                </body>
                </html>
            '''.encode('utf-8'))
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<html><body><h2>Invalid callback</h2></body></html>')
    
    def log_message(self, format, *args):
        """Suppress log messages."""
        pass


class AuthManager:
    """Manage authentication for the alphai CLI."""
    
    def __init__(self, config: Config):
        """Initialize the auth manager with configuration."""
        self.config = config
        self.console = Console()
    
    def login_with_token(self, token: str) -> bool:
        """Login with a provided bearer token."""
        logger.info("Attempting login with provided token")
        if not token.strip():
            logger.error("Empty token provided")
            self.console.print("[red]Error: Empty token provided[/red]")
            raise exceptions.ValidationError("Token cannot be empty")
        
        # Validate the token
        if self.validate_token(token):
            self.config.set_bearer_token(token)
            logger.info("Login successful with token")
            return True
        else:
            logger.error("Invalid token provided")
            self.console.print("[red]Error: Invalid token[/red]")
            return False
    
    def interactive_login(self) -> bool:
        """Perform interactive login."""
        self.console.print(Panel(
            "[bold]alphai Authentication[/bold]\n\n"
            "You can get your token from: https://runalph.ai/account/tokens\n"
            "Or set the ALPHAI_BEARER_TOKEN environment variable.",
            title="Authentication Required",
            title_align="left"
        ))
        
        # Check if token is in environment first
        env_token = os.getenv("ALPHAI_BEARER_TOKEN")
        if env_token:
            if self.validate_token(env_token):
                self.config.set_bearer_token(env_token)
                self.console.print("[green]✓ Using token from environment variable[/green]")
                return True
            else:
                self.console.print("[yellow]Warning: Invalid token in environment variable[/yellow]")
        
        # Use questionary for arrow key menu selection
        method = questionary.select(
            "Choose your authentication method:",
            choices=[
                questionary.Choice("Browser login (recommended)", value="browser"),
                questionary.Choice("Token login", value="token")
            ],
            style=questionary.Style([
                ('question', 'bold'),
                ('selected', 'fg:#00aa00 bold'),
                ('pointer', 'fg:#00aa00 bold'),
                ('highlighted', 'fg:#00aa00'),
                ('answer', 'fg:#00aa00 bold')
            ])
        ).ask()
        
        if not method:  # User cancelled (Ctrl+C)
            self.console.print("[yellow]Authentication cancelled[/yellow]")
            return False
        
        if method == "browser":
            self.console.print("[blue]Starting browser authentication...[/blue]")
            return self.browser_login()
        else:
            # Fallback to manual token entry
            self.console.print("[blue]Manual token authentication[/blue]")
            token = Prompt.ask(
                "Enter your bearer token",
                password=True,
                show_default=False
            )
            
            if not token:
                self.console.print("[red]No token provided[/red]")
                return False
            
            return self.login_with_token(token)
    
    def browser_login(self, port: int = 8080) -> bool:
        """Perform browser-based login using OAuth flow."""
        logger.info("Starting browser-based authentication")
        # Try to find an available port
        for attempt_port in range(port, port + 10):
            try:
                # Create HTTP server to handle callback
                httpd = HTTPServer(('localhost', attempt_port), CallbackHandler)
                httpd.timeout = 60  # 1 minute timeout
                httpd.token = None
                httpd.error = None
                httpd.api_url = self.config.base_url  # Pass base_url for redirects (not /api)
                logger.debug(f"Callback server started on port {attempt_port}")
                break
            except OSError:
                logger.debug(f"Port {attempt_port} not available, trying next")
                continue
        else:
            logger.error("Could not find available port for OAuth callback")
            self.console.print("[red]Error: Could not find an available port for callback[/red]")
            return False
        
        redirect_uri = f"http://127.0.0.1:{attempt_port}"
        
        # Construct the authentication URL (auth is at base URL, not /api)
        auth_url = f"{self.config.base_url}/auth/cli"
        auth_params = {
            "redirect_uri": redirect_uri,
            "response_type": "token",
            "hostname": socket.gethostname()  # Get the machine's hostname
        }
        full_auth_url = f"{auth_url}?{urllib.parse.urlencode(auth_params)}"
        
        self.console.print(Panel(
            f"[bold]Browser Authentication[/bold]\n\n"
            f"Opening browser for authentication...\n"
            f"If the browser doesn't open automatically, visit:\n"
            f"{full_auth_url}\n\n"
            f"Waiting for authentication callback on port {attempt_port}...",
            title="Browser Login",
            title_align="left"
        ))
        
        # Open browser
        try:
            webbrowser.open(full_auth_url)
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not open browser automatically: {e}[/yellow]")
            self.console.print(f"[yellow]Please visit: {full_auth_url}[/yellow]")
        
        # Start server in a separate thread
        server_thread = threading.Thread(target=httpd.handle_request)
        server_thread.daemon = True
        server_thread.start()
        
        # Wait for callback with progress indicator
        start_time = time.time()
        while server_thread.is_alive() and time.time() - start_time < 60:
            time.sleep(0.5)
            # Show a simple progress indicator
            elapsed = int(time.time() - start_time)
            if elapsed % 5 == 0 and elapsed > 0:
                self.console.print(f"[dim]Still waiting... ({elapsed}s elapsed)[/dim]")
        
        # Check results
        if hasattr(httpd, 'token') and httpd.token:
            self.console.print("[green]✓ Received authentication token[/green]")
            return self.login_with_token(httpd.token)
        elif hasattr(httpd, 'error') and httpd.error:
            self.console.print(f"[red]Authentication error: {httpd.error}[/red]")
            return False
        else:
            self.console.print("[red]Authentication timed out or failed[/red]")
            return False
    
    def validate_token(self, token: str) -> bool:
        """Validate a bearer token by making a test API call."""
        logger.debug("Validating bearer token")
        try:
            with httpx.Client() as client:
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                
                # Test the token by trying to get organizations
                response = client.get(
                    f"{self.config.api_url}/orgs",
                    headers=headers,
                    timeout=10.0
                )
                
                # Check if the response is successful
                if response.status_code in (200, 201):
                    logger.info("Token validation successful")
                    return True
                elif response.status_code == 401:
                    logger.error("Token validation failed: Invalid or expired token")
                    self.console.print("[red]Error: Invalid or expired token[/red]")
                    return False
                elif response.status_code == 403:
                    logger.error("Token validation failed: Access forbidden")
                    self.console.print("[red]Error: Access forbidden - check your permissions[/red]")
                    return False
                else:
                    logger.error(f"Token validation failed: API returned status {response.status_code}")
                    self.console.print(f"[red]Error: API returned status {response.status_code}[/red]")
                    return False
                    
        except httpx.ConnectError as e:
            logger.error(f"Connection error during token validation: {e}")
            self.console.print(f"[red]Error: Could not connect to API at {self.config.api_url}[/red]")
            return False
        except httpx.TimeoutException as e:
            logger.error(f"Timeout during token validation: {e}")
            self.console.print("[red]Error: Request timed out[/red]")
            return False
        except Exception as e:
            logger.error(f"Unexpected error validating token: {e}", exc_info=True)
            self.console.print(f"[red]Error validating token: {e}[/red]")
            return False
    
    def refresh_token(self) -> bool:
        """Refresh the current token if possible."""
        # This would be implemented if the API supports token refresh
        # For now, we'll just validate the existing token
        if self.config.bearer_token:
            return self.validate_token(self.config.bearer_token)
        return False
    
    def get_user_info(self) -> Optional[dict]:
        """Get information about the currently authenticated user."""
        if not self.config.bearer_token:
            return None
        
        try:
            with httpx.Client() as client:
                headers = {
                    "Authorization": f"Bearer {self.config.bearer_token}",
                    "Content-Type": "application/json"
                }
                
                # Try to get user info (this endpoint may not exist in the actual API)
                response = client.get(
                    f"{self.config.api_url}/user",
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return None
                    
        except Exception:
            return None
    
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated with a valid token."""
        if not self.config.bearer_token:
            return False
        
        # Validate the current token silently (without console output)
        try:
            with httpx.Client() as client:
                headers = {
                    "Authorization": f"Bearer {self.config.bearer_token}",
                    "Content-Type": "application/json"
                }
                
                response = client.get(
                    f"{self.config.api_url}/orgs",
                    headers=headers,
                    timeout=10.0
                )
                
                return response.status_code in (200, 201)
        except Exception:
            return False
    
    def check_existing_authentication(self) -> bool:
        """Check and validate existing authentication, providing user feedback."""
        if not self.config.bearer_token:
            return False
        
        self.console.print("[blue]Checking existing authentication...[/blue]")
        
        if self.validate_token(self.config.bearer_token):
            self.console.print("[green]✓ Already authenticated and token is valid[/green]")
            
            # Try to get user info for additional context
            user_info = self.get_user_info()
            if user_info:
                email = user_info.get('email', 'Unknown')
                self.console.print(f"[green]✓ Logged in as: {email}[/green]")
            
            return True
        else:
            self.console.print("[yellow]⚠ Existing token is invalid or expired[/yellow]")
            # Clear the invalid token
            self.config.clear_bearer_token()
            self.config.save()
            return False 