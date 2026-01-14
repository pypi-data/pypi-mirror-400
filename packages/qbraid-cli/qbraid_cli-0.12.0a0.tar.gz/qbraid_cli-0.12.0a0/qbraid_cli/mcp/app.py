# Copyright (c) 2025, qBraid Development Team
# All rights reserved.

"""
CLI commands for qBraid MCP aggregator.

"""
import typer

from .serve import serve_mcp

mcp_app = typer.Typer(help="MCP (Model Context Protocol) aggregator commands")


@mcp_app.command("serve", help="Start MCP aggregator server for Claude Desktop")
def serve(
    workspace: str = typer.Option(
        "lab",
        "--workspace",
        "-w",
        help="Workspace to connect to (lab, qbook, etc.)",
    ),
    include_staging: bool = typer.Option(
        False,
        "--staging",
        "-s",
        help="Include staging endpoints",
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        "-d",
        help="Enable debug logging",
    ),
):
    """
    Start the qBraid MCP aggregator server.

    This command starts a unified MCP server that connects to multiple qBraid MCP backends
    (Lab pod_mcp, devices, jobs, etc.) and exposes them through a single stdio interface
    for Claude Desktop and other AI agents.

    Usage:
        # Start MCP server for Lab workspace
        qbraid mcp serve

        # Include staging endpoints for testing
        qbraid mcp serve --staging

        # Enable debug logging
        qbraid mcp serve --debug

    Claude Desktop Configuration:
        {
          "mcpServers": {
            "qbraid": {
              "command": "qbraid",
              "args": ["mcp", "serve"]
            }
          }
        }
    """
    serve_mcp(workspace=workspace, include_staging=include_staging, debug=debug)


@mcp_app.command("status", help="Show status of MCP connections")
def status():
    """
    Show the status of MCP backend connections.

    Displays which backends are configured and their connection status.
    """
    typer.echo("MCP Status:")
    typer.echo("  Implementation in progress...")
    typer.echo("  This will show connection status for all configured MCP backends")


@mcp_app.command("list", help="List available MCP servers")
def list_servers(
    workspace: str = typer.Option(
        None,
        "--workspace",
        "-w",
        help="Filter by workspace (lab, qbook, etc.)",
    ),
    include_staging: bool = typer.Option(
        False,
        "--staging",
        "-s",
        help="Include staging endpoints",
    ),
):
    """
    List available qBraid MCP servers.

    Shows all discovered MCP endpoints that can be connected to.
    """
    try:
        from qbraid_core.services.mcp import discover_mcp_servers

        endpoints = discover_mcp_servers(
            workspace=workspace or "lab", include_staging=include_staging
        )

        if not endpoints:
            typer.echo("No MCP servers found")
            return

        typer.echo(f"Found {len(endpoints)} MCP server(s):\n")
        for endpoint in endpoints:
            typer.echo(f"  • {endpoint.name}")
            typer.echo(f"    {endpoint.base_url}")
            if endpoint.description:
                typer.echo(f"    {endpoint.description}")
            typer.echo()

    except ImportError as exc:
        typer.secho(
            "Error: qbraid-core MCP module not found. "
            "Please install qbraid-core with MCP support: pip install qbraid-core[mcp]",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1) from exc
    except Exception as err:
        typer.secho(f"Error listing MCP servers: {err}", fg=typer.colors.RED)
        raise typer.Exit(1)
