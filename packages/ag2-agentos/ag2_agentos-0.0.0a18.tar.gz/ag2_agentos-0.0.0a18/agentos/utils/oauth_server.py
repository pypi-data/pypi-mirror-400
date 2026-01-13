"""OAuth callback HTTP server for AG2 CLI authentication."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Event
from typing import Optional


class OAuthCallbackServer:
    """
    Simple HTTP server to receive OAuth callback with access token.

    Listens on specified port for POST requests containing access_token.
    Validates the security code and stores the token.
    """

    def __init__(self, port: int, expected_code: str, timeout: int = 300):
        """
        Initialize OAuth callback server.

        Args:
            port: Port to listen on (default: 8617)
            expected_code: Expected security code for validation
            timeout: Server timeout in seconds (default: 300 = 5 minutes)
        """
        self.port = port
        self.expected_code = expected_code
        self.timeout = timeout
        self.access_token: Optional[str] = None
        self.error: Optional[str] = None
        self.server: Optional[HTTPServer] = None
        self.shutdown_event = Event()

    def start(self) -> None:
        """
        Start the server in blocking mode.

        Server will run until:
        - Valid access token is received
        - Timeout is reached (default 5 minutes)
        - Server is manually shutdown
        """
        import time

        handler_class = self._create_handler_class()

        try:
            self.server = HTTPServer(('127.0.0.1', self.port), handler_class)
            # Set a short timeout for handle_request to allow checking shutdown_event
            self.server.timeout = 1.0  # 1 second poll interval
            self.server.oauth_callback = self  # Reference to this instance

            # Track overall timeout
            start_time = time.time()

            # Run server until shutdown event is set or timeout
            while not self.shutdown_event.is_set():
                # Check if we've exceeded the overall timeout
                elapsed = time.time() - start_time
                if elapsed >= self.timeout:
                    self.error = "timeout"
                    break

                # Handle one request (or timeout after 1 second)
                self.server.handle_request()

        except OSError as e:
            if e.errno == 48:  # Address already in use
                raise OSError(f"Port {self.port} is already in use") from e
            raise
        finally:
            if self.server:
                self.server.server_close()

    def shutdown(self) -> None:
        """Gracefully shutdown the server."""
        self.shutdown_event.set()
        if self.server:
            self.server.shutdown()

    def _create_handler_class(self):
        """Create handler class with reference to this server instance."""
        server_instance = self

        class OAuthCallbackHandler(BaseHTTPRequestHandler):
            """Handle POST requests with access_token."""

            # Allowed origins for CORS
            ALLOWED_ORIGINS = [
                'http://localhost:3000',
                'https://localhost:3000',
                'https://dev.app.ag2.ai',
                'https://app.ag2.ai',
            ]

            def _get_cors_origin(self) -> str:
                """Get appropriate CORS origin header value based on request origin."""
                origin = self.headers.get('Origin', '')
                if origin in self.ALLOWED_ORIGINS:
                    return origin
                # Default to first allowed origin if origin not in allowed list
                return self.ALLOWED_ORIGINS[0]

            def do_OPTIONS(self) -> None:
                """Handle CORS preflight requests."""
                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', self._get_cors_origin())
                self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.send_header('Access-Control-Allow-Credentials', 'true')
                self.end_headers()

            def do_POST(self) -> None:
                """
                Handle POST request with access token.

                Expected request body (JSON):
                {
                    "access_token": "token_value",
                    "code": "ABC123"
                }
                """
                try:
                    # Check content length
                    content_length = int(self.headers.get('Content-Length', 0))

                    # Limit request size to 1KB to prevent DoS
                    if content_length > 1024:
                        self.send_response(413)  # Payload Too Large
                        self.send_header('Access-Control-Allow-Origin', self._get_cors_origin())
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(b'{"error": "Request too large"}')
                        return

                    # Read and parse JSON body
                    body = self.rfile.read(content_length)
                    data = json.loads(body)
                    # Validate required fields
                    if 'access_token' not in data or 'code' not in data:
                        self.send_response(400)  # Bad Request
                        self.send_header('Access-Control-Allow-Origin', self._get_cors_origin())
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(b'{"error": "Missing required fields: access_token and code"}')
                        return

                    # Validate security code
                    if data['code'] != server_instance.expected_code:
                        self.send_response(403)  # Forbidden
                        self.send_header('Access-Control-Allow-Origin', self._get_cors_origin())
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(b'{"error": "Invalid security code"}')
                        return

                    # Validate token format (non-empty, minimum length)
                    access_token = data.get('access_token', '').strip()
                    if not access_token or len(access_token) < 10:
                        self.send_response(400)  # Bad Request
                        self.send_header('Access-Control-Allow-Origin', self._get_cors_origin())
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(b'{"error": "Invalid access token format"}')
                        return

                    # Success - store token
                    server_instance.access_token = access_token

                    # Send success response
                    self.send_response(200)
                    self.send_header('Access-Control-Allow-Origin', self._get_cors_origin())
                    self.send_header('Content-Type', 'text/html')
                    self.end_headers()

                    # Send success HTML page
                    success_html = """
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>Authentication Successful</title>
                        <style>
                            body {
                                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                                display: flex;
                                justify-content: center;
                                align-items: center;
                                height: 100vh;
                                margin: 0;
                                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            }
                            .container {
                                background: white;
                                padding: 3rem;
                                border-radius: 10px;
                                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                                text-align: center;
                                max-width: 400px;
                            }
                            .success-icon {
                                font-size: 4rem;
                                margin-bottom: 1rem;
                            }
                            h1 {
                                color: #2d3748;
                                margin-bottom: 0.5rem;
                            }
                            p {
                                color: #718096;
                                margin-bottom: 1.5rem;
                            }
                            .close-message {
                                color: #4a5568;
                                font-size: 0.9rem;
                            }
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <div class="success-icon">✓</div>
                            <h1>Authentication Successful!</h1>
                            <p>You have been successfully authenticated with AG2.</p>
                            <p class="close-message">You can close this window and return to your terminal.</p>
                        </div>
                    </body>
                    </html>
                    """
                    self.wfile.write(success_html.encode('utf-8'))

                    # Trigger server shutdown
                    server_instance.shutdown_event.set()

                except json.JSONDecodeError:
                    self.send_response(400)  # Bad Request
                    self.send_header('Access-Control-Allow-Origin', self._get_cors_origin())
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(b'{"error": "Invalid JSON in request body"}')

                except Exception as e:
                    self.send_response(500)  # Internal Server Error
                    self.send_header('Access-Control-Allow-Origin', self._get_cors_origin())
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    error_message = f'{{"error": "Internal server error: {str(e)}"}}'
                    self.wfile.write(error_message.encode('utf-8'))

            def log_message(self, format: str, *args) -> None:
                """Suppress default logging (we use Rich console instead)."""
                pass

        return OAuthCallbackHandler
