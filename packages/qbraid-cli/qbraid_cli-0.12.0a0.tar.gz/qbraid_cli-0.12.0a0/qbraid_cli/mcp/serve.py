# Copyright (c) 2025, qBraid Development Team
# All rights reserved.

"""
MCP aggregator server implementation.

Provides stdio-based MCP server that aggregates multiple qBraid MCP backends.
"""
import asyncio
import json
import logging
import signal
import sys
from typing import Optional

import typer
from qbraid_core.services.mcp import MCPRouter, MCPWebSocketClient, discover_mcp_servers
from qbraid_core.sessions import QbraidSession


def setup_logging(debug: bool = False) -> None:
    """
    Configure logging for MCP server.

    Args:
        debug: Enable debug logging
    """
    level = logging.DEBUG if debug else logging.INFO

    # Log to stderr so stdout remains clean for MCP protocol
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stderr,
    )


class MCPAggregatorServer:
    """
    MCP aggregator server that bridges stdio to multiple WebSocket backends.

    Architecture:
        Claude Desktop (stdio) <-> THIS SERVER <-> Multiple MCP WebSocket Servers
    """

    def __init__(
        self,
        session: QbraidSession,
        workspace: str = "lab",
        include_staging: bool = False,
        debug: bool = False,
    ):
        """
        Initialize MCP aggregator server.

        Args:
            session: Authenticated qBraid session
            workspace: Workspace to connect to
            include_staging: Include staging endpoints
            debug: Enable debug logging
        """
        self.session = session
        self.workspace = workspace
        self.include_staging = include_staging
        self.debug = debug
        self.router: Optional[MCPRouter] = None
        self.logger = logging.getLogger(__name__)
        self._shutdown_event = asyncio.Event()

    async def initialize_backends(self) -> None:
        """
        Discover and connect to MCP backend servers.
        """
        # Get user info for building WebSocket URLs
        try:
            user_info = self.session.get_user()
            username = user_info.get("email")
            if not username:
                raise ValueError("User email not found in session")
        except Exception as err:
            self.logger.error("Failed to get user info: %s", err)
            typer.secho(
                "Error: Could not authenticate. Please run 'qbraid configure' first.",
                fg=typer.colors.RED,
                err=True,
            )
            raise typer.Exit(1)

        # Discover available MCP endpoints
        endpoints = discover_mcp_servers(
            workspace=self.workspace,
            include_staging=self.include_staging,
        )

        if not endpoints:
            typer.secho(
                f"Warning: No MCP endpoints found for workspace '{self.workspace}'",
                fg=typer.colors.YELLOW,
                err=True,
            )
            raise typer.Exit(1)

        self.logger.info("Discovered %d MCP endpoint(s)", len(endpoints))

        # Create router
        self.router = MCPRouter(on_message=self._handle_backend_message)

        # Create WebSocket clients for each endpoint
        for endpoint in endpoints:
            # Use JupyterHub token for lab endpoints, API key for other endpoints
            try:
                if endpoint.name.startswith("lab"):
                    try:
                        token_data = self.session.get_jupyter_token_data()
                        token = token_data.get("token")
                        if not token:
                            raise ValueError("Token not found in response data")
                    except Exception as err:
                        self.logger.error(
                            "Failed to get Jupyter token for endpoint '%s': %s",
                            endpoint.name,
                            err,
                        )
                        typer.secho(
                            f"Error: Could not retrieve Jupyter token for '{endpoint.name}'. "
                            "Please ensure you are authenticated with qBraid Lab.",
                            fg=typer.colors.RED,
                            err=True,
                        )
                        raise typer.Exit(1)
                else:
                    token = self.session.api_key
                    if not token:
                        self.logger.error("No API key available for endpoint '%s'", endpoint.name)
                        typer.secho(
                            f"Error: No API key available for '{endpoint.name}'. "
                            "Please run 'qbraid configure' to set up your credentials.",
                            fg=typer.colors.RED,
                            err=True,
                        )
                        raise typer.Exit(1)

                ws_url = endpoint.build_url(username, token)
                self.logger.info("Configuring backend: %s", endpoint.name)

                client = MCPWebSocketClient(
                    websocket_url=ws_url,
                    on_message=self._handle_backend_message,
                    name=endpoint.name,
                )
                self.router.add_backend(endpoint.name, client)
            except typer.Exit:
                raise  # Re-raise typer.Exit to propagate clean exits
            except Exception as err:  # pylint: disable=broad-exception-caught
                self.logger.error("Failed to configure backend '%s': %s", endpoint.name, err)
                typer.secho(
                    f"Error: Failed to configure backend '{endpoint.name}': {err}",
                    fg=typer.colors.RED,
                    err=True,
                )
                raise typer.Exit(1)

        # Connect to all backends
        self.logger.info("Connecting to backends...")
        await self.router.connect_all()

        # Check connection status
        connected = self.router.get_connected_backends()
        if not connected:
            typer.secho(
                "Error: Failed to connect to any MCP backends",
                fg=typer.colors.RED,
                err=True,
            )
            raise typer.Exit(1)

        self.logger.info("Connected to %d backend(s): %s", len(connected), ", ".join(connected))
        typer.secho(
            f"MCP aggregator ready ({len(connected)} backend(s) connected)",
            fg=typer.colors.GREEN,
            err=True,
        )

    def _handle_backend_message(self, message: dict) -> None:
        """
        Handle messages from backend MCP servers.

        Forwards messages to stdout for Claude Desktop.

        Args:
            message: Message dictionary from backend
        """
        try:
            self.logger.info(
                "📥 _handle_backend_message called with message: %s", str(message)[:100]
            )
            # Write message to stdout as JSON
            json_str = json.dumps(message)
            self.logger.info("📤 Writing to stdout: %s", json_str[:100])
            sys.stdout.write(json_str + "\n")
            sys.stdout.flush()
            self.logger.info("✅ Successfully sent to client")
        except Exception as err:  # pylint: disable=broad-exception-caught
            self.logger.error("❌ Error forwarding message: %s", err, exc_info=True)

    async def _stdin_loop(self) -> None:
        """
        Read messages from stdin (Claude Desktop) and route to backends.
        """
        loop = asyncio.get_event_loop()

        self.logger.info("Starting stdin loop...")

        try:
            while not self._shutdown_event.is_set():
                # Read line from stdin (non-blocking)
                try:
                    line = await loop.run_in_executor(None, sys.stdin.readline)
                    if not line:
                        # EOF reached (stdin closed)
                        self.logger.info("stdin closed, shutting down...")
                        break

                    line = line.strip()
                    if not line:
                        continue

                    self.logger.debug("Received from client: %s...", line[:100])

                    # Parse JSON message
                    message = json.loads(line)

                    # Route to appropriate backend
                    if self.router:
                        await self.router.handle_message(message)

                except json.JSONDecodeError as err:
                    self.logger.error("Invalid JSON from client: %s", err)
                except Exception as err:  # pylint: disable=broad-exception-caught
                    self.logger.error("Error processing message: %s", err)

        except asyncio.CancelledError:
            self.logger.info("stdin loop cancelled")
        except Exception as err:  # pylint: disable=broad-exception-caught
            self.logger.error("Fatal error in stdin loop: %s", err)
        finally:
            self._shutdown_event.set()

    async def run(self) -> None:
        """
        Run the MCP aggregator server.
        """

        # Setup signal handlers for graceful shutdown
        def signal_handler(signum, _frame):  # pylint: disable=unused-argument
            self.logger.info("Received signal %d, shutting down...", signum)
            self._shutdown_event.set()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Start backend initialization and stdin loop concurrently
        # This allows the server to respond to Claude's initialize request
        # while backends are still connecting in the background
        try:
            await asyncio.gather(
                self.initialize_backends(),
                self._stdin_loop(),
            )
        finally:
            # Cleanup
            self.logger.info("Shutting down backends...")
            if self.router:
                await self.router.shutdown_all()
            self.logger.info("Shutdown complete")


def serve_mcp(workspace: str, include_staging: bool, debug: bool) -> None:
    """
    Start the qBraid MCP aggregator server.

    Args:
        workspace: Workspace name (lab, qbook, etc.)
        include_staging: Include staging endpoints
        debug: Enable debug logging
    """
    # Setup logging
    setup_logging(debug=debug)
    logger = logging.getLogger(__name__)

    logger.info("Starting qBraid MCP aggregator...")
    logger.info("Workspace: %s, Staging: %s, Debug: %s", workspace, include_staging, debug)

    # Create qBraid session
    try:
        session = QbraidSession()
    except Exception as err:
        typer.secho(
            f"Error creating qBraid session: {err}\n"
            "Please run 'qbraid configure' to set up your credentials.",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(1)

    # Create and run server
    server = MCPAggregatorServer(
        session=session,
        workspace=workspace,
        include_staging=include_staging,
        debug=debug,
    )

    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as err:
        logger.error("Fatal error: %s", err, exc_info=debug)
        typer.secho(f"Error: {err}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)
