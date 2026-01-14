"""Local HTTP server for OAuth callback."""

import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional

from janet.utils.console import console


class CallbackHandler(BaseHTTPRequestHandler):
    """HTTP request handler for OAuth callback."""

    authorization_code: Optional[str] = None
    error: Optional[str] = None

    def do_GET(self) -> None:
        """Handle GET request to callback URL."""
        # Parse query parameters
        parsed_url = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed_url.query)

        if "code" in params:
            # Successful authorization
            CallbackHandler.authorization_code = params["code"][0]
            self.send_success_response()
        elif "error" in params:
            # Authorization error
            CallbackHandler.error = params.get("error_description", ["Unknown error"])[0]
            self.send_error_response()
        else:
            # Invalid callback
            self.send_error_response("Invalid callback parameters")

    def send_success_response(self) -> None:
        """Send success HTML response."""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Janet AI - Authentication Successful</title>
            <link rel="icon" href="https://app.tryjanet.ai/logo-favicon.png">
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    background: #ffffff;
                    color: #171717;
                }
                @media (prefers-color-scheme: dark) {
                    body {
                        background: rgb(38, 38, 38);
                        color: #ededed;
                    }
                    .container {
                        background: rgb(50, 50, 50) !important;
                        border: 1px solid #333 !important;
                    }
                    h1 {
                        color: #ededed !important;
                    }
                    p {
                        color: #a3a3a3 !important;
                    }
                    .logo {
                        filter: brightness(0) invert(1);
                    }
                }
                .container {
                    background: white;
                    padding: 3rem 2rem;
                    border-radius: 12px;
                    border: 1px solid #e5e5e5;
                    text-align: center;
                    max-width: 480px;
                    width: 90%;
                    animation: fadeIn 0.3s ease-out;
                }
                .logo {
                    width: 180px;
                    height: auto;
                    margin: 0 auto 2.5rem;
                }
                .success-icon {
                    width: 64px;
                    height: 64px;
                    margin: 0 auto 1.5rem;
                    background: #10b981;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .success-icon svg {
                    width: 36px;
                    height: 36px;
                    color: white;
                }
                h1 {
                    font-size: 1.5rem;
                    font-weight: 600;
                    color: #171717;
                    margin-bottom: 0.75rem;
                }
                p {
                    color: #737373;
                    line-height: 1.6;
                    font-size: 0.95rem;
                }
                @keyframes fadeIn {
                    from {
                        opacity: 0;
                        transform: translateY(10px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <img src="https://app.tryjanet.ai/Full%20Logo.svg" alt="Janet AI" class="logo">
                <div class="success-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                    </svg>
                </div>
                <h1>Authentication Successful</h1>
                <p>Return to your terminal to continue.</p>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html.encode())

    def send_error_response(self, error_message: str = "Authentication failed") -> None:
        """Send error HTML response."""
        self.send_response(400)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Janet AI - Authentication Failed</title>
            <link rel="icon" href="https://app.tryjanet.ai/logo-favicon.png">
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    background: #ffffff;
                    color: #171717;
                }}
                @media (prefers-color-scheme: dark) {{
                    body {{
                        background: rgb(38, 38, 38);
                        color: #ededed;
                    }}
                    .container {{
                        background: rgb(50, 50, 50) !important;
                        border: 1px solid #333 !important;
                    }}
                    h1 {{
                        color: #ededed !important;
                    }}
                    p {{
                        color: #a3a3a3 !important;
                    }}
                    .logo {{
                        filter: brightness(0) invert(1);
                    }}
                }}
                .container {{
                    background: white;
                    padding: 3rem 2rem;
                    border-radius: 12px;
                    border: 1px solid #e5e5e5;
                    text-align: center;
                    max-width: 480px;
                    width: 90%;
                    animation: fadeIn 0.3s ease-out;
                }}
                .logo {{
                    width: 180px;
                    height: auto;
                    margin: 0 auto 2.5rem;
                }}
                .error-icon {{
                    width: 64px;
                    height: 64px;
                    margin: 0 auto 1.5rem;
                    background: #ef4444;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                .error-icon svg {{
                    width: 36px;
                    height: 36px;
                    color: white;
                }}
                h1 {{
                    font-size: 1.5rem;
                    font-weight: 600;
                    color: #171717;
                    margin-bottom: 0.75rem;
                }}
                p {{
                    color: #737373;
                    line-height: 1.6;
                    font-size: 0.95rem;
                }}
                @keyframes fadeIn {{
                    from {{
                        opacity: 0;
                        transform: translateY(10px);
                    }}
                    to {{
                        opacity: 1;
                        transform: translateY(0);
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <img src="https://app.tryjanet.ai/Full%20Logo.svg" alt="Janet AI" class="logo">
                <div class="error-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </div>
                <h1>Authentication Failed</h1>
                <p>Please return to your terminal and try again.</p>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html.encode())

    def log_message(self, format: str, *args) -> None:
        """Suppress default HTTP server logging."""
        pass


class CallbackServer:
    """Lightweight HTTP server for OAuth callback."""

    def __init__(self, port: int = 8765):
        """
        Initialize callback server.

        Args:
            port: Port to listen on (default: 8765)
        """
        self.port = port
        self.server: Optional[HTTPServer] = None
        self.thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """Start server in background thread."""
        # Reset state
        CallbackHandler.authorization_code = None
        CallbackHandler.error = None

        # Try to start server on specified port, fallback to next ports if busy
        # Use 127.0.0.1 instead of localhost for WorkOS compatibility
        for attempt_port in range(self.port, self.port + 10):
            try:
                self.server = HTTPServer(("127.0.0.1", attempt_port), CallbackHandler)
                self.port = attempt_port
                break
            except OSError:
                continue
        else:
            raise RuntimeError("Failed to start callback server: all ports busy")

        # Start server in background thread
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def wait_for_code(self, timeout: int = 300) -> str:
        """
        Wait for authorization code from callback.

        Args:
            timeout: Timeout in seconds (default: 5 minutes)

        Returns:
            Authorization code

        Raises:
            TimeoutError: If timeout reached
            RuntimeError: If authorization error occurred
        """
        if not self.server:
            raise RuntimeError("Server not started")

        import time

        start_time = time.time()
        while time.time() - start_time < timeout:
            if CallbackHandler.authorization_code:
                code = CallbackHandler.authorization_code
                self.stop()
                return code

            if CallbackHandler.error:
                error = CallbackHandler.error
                self.stop()
                raise RuntimeError(f"Authorization error: {error}")

            time.sleep(0.1)

        self.stop()
        raise TimeoutError("Timeout waiting for authorization callback")

    def stop(self) -> None:
        """Stop the server."""
        if self.server:
            self.server.shutdown()
            self.server = None

    def get_redirect_uri(self) -> str:
        """
        Get the redirect URI for this server.

        Returns:
            Redirect URI string
        """
        # WorkOS requires 127.0.0.1 (not localhost) for http in production
        return f"http://127.0.0.1:{self.port}/callback"
