"""CLI entry point for Daimyo rules server."""

import asyncio
import logging
import signal
import sys
from enum import Enum

import typer
import uvicorn

from daimyo import __version__
from daimyo.config import settings
from daimyo.infrastructure.logging import get_logger, setup_logging

app = typer.Typer(
    name="daimyo",
    help="Daimyo - Rules Server for Agents",
    add_completion=False,
)


class SuppressShutdownErrors(logging.Filter):
    """Filter to suppress expected errors during server shutdown."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter out CancelledError exceptions during shutdown.

        :param record: Log record to filter
        :type record: logging.LogRecord
        :returns: False if record should be suppressed, True otherwise
        :rtype: bool
        """
        if record.levelno == logging.ERROR:
            if record.exc_info and record.exc_info[0] is asyncio.CancelledError:
                return False
            if "CancelledError" in record.getMessage():
                return False
            if "timeout graceful shutdown exceeded" in record.getMessage():
                return False
        return True


class TransportType(str, Enum):
    """MCP transport types."""

    STDIO = "stdio"
    HTTP = "http"


def version_callback(value: bool) -> None:
    """Print version and exit.

    :param value: Whether version flag was set
    :type value: bool
    :rtype: None
    :raises typer.Exit: Always exits after printing version
    """
    if value:
        typer.echo(f"daimyo version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
) -> None:
    """Daimyo - Rules Server for Agents.

    :param version: Show version flag
    :type version: bool
    :rtype: None
    """
    pass


@app.command()
def serve(
    host: str = typer.Option(
        None,
        "--host",
        help=f"Host to bind to (default: {settings.REST_HOST})",
    ),
    port: int = typer.Option(
        None,
        "--port",
        help=f"Port to bind to (default: {settings.REST_PORT})",
    ),
    reload: bool = typer.Option(
        False,
        "--reload",
        help="Enable auto-reload for development",
    ),
) -> None:
    """Start the REST API server.

    :param host: Host to bind to
    :type host: str
    :param port: Port to bind to
    :type port: int
    :param reload: Enable auto-reload for development
    :type reload: bool
    :rtype: None
    """
    setup_logging()

    resolved_host = host or settings.REST_HOST
    resolved_port = port or settings.REST_PORT

    typer.echo(f"Starting Daimyo REST API server on {resolved_host}:{resolved_port}")
    typer.echo(f"API documentation available at http://{resolved_host}:{resolved_port}/docs")

    try:
        uvicorn.run(
            "daimyo.presentation.rest.app:app",
            host=resolved_host,
            port=resolved_port,
            reload=reload,
            log_config=None,
        )
    except KeyboardInterrupt:
        typer.echo("\nShutting down REST API server gracefully...")
        typer.echo("REST API server stopped.")
    except Exception as e:
        typer.echo(f"\nError running REST API server: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def mcp(
    transport: TransportType = typer.Option(
        None,
        "--transport",
        help=f"MCP transport type (default: {settings.MCP_TRANSPORT})",
    ),
    host: str = typer.Option(
        None,
        "--host",
        help=f"Host to bind to for HTTP transport (default: {settings.MCP_HOST})",
    ),
    port: int = typer.Option(
        None,
        "--port",
        help=f"Port to bind to for HTTP transport (default: {settings.MCP_PORT})",
    ),
) -> None:
    """Start the MCP server.

    :param transport: MCP transport type
    :type transport: TransportType
    :param host: Host to bind to for HTTP transport
    :type host: str
    :param port: Port to bind to for HTTP transport
    :type port: int
    :rtype: None
    """
    setup_logging()
    logger = get_logger(__name__)

    resolved_transport = transport.value if transport else settings.MCP_TRANSPORT
    resolved_host = host or settings.MCP_HOST
    resolved_port = port or settings.MCP_PORT

    typer.echo(f"Starting Daimyo MCP server with {resolved_transport} transport")
    if resolved_transport == "http":
        typer.echo(f"MCP server will listen on {resolved_host}:{resolved_port}")

    from daimyo.infrastructure.di import cleanup_container
    from daimyo.presentation.mcp.server import mcp as mcp_server

    if resolved_transport == "http":
        shutdown_filter = SuppressShutdownErrors()
        for logger_name in ["uvicorn.error", "uvicorn.access", "uvicorn"]:
            logging.getLogger(logger_name).addFilter(shutdown_filter)

    signal.signal(signal.SIGINT, signal.default_int_handler)
    signal.signal(signal.SIGTERM, signal.default_int_handler)

    try:
        if resolved_transport == "stdio":
            mcp_server.run(transport="stdio")
        else:
            mcp_server.run(transport="http", host=resolved_host, port=resolved_port)
    except KeyboardInterrupt:
        logger.info("MCP server shutdown initiated by user")
        typer.echo("\nShutting down MCP server gracefully...")
    except Exception as e:
        logger.exception(f"Error running MCP server: {e}")
        typer.echo(f"\nError running MCP server: {e}", err=True)
        raise typer.Exit(code=1)
    finally:
        logger.info("Cleaning up resources...")
        cleanup_container()
        logger.info("MCP server stopped.")


@app.command()
def list_scopes() -> None:
    """List all available scopes.

    :rtype: None
    """
    setup_logging()

    from daimyo.infrastructure.di import get_container

    container = get_container()
    repo = container.scope_repository()
    scopes = repo.list_scopes()

    if not scopes:
        typer.echo("No scopes found.")
        return

    typer.echo("Available scopes:")
    for scope_name in scopes:
        typer.echo(f"  - {scope_name}")


@app.command()
def show(
    scope_name: str = typer.Argument(
        ...,
        help="Name of the scope to show",
    ),
) -> None:
    """Show details of a specific scope.

    :param scope_name: Name of the scope to show
    :type scope_name: str
    :rtype: None
    """
    setup_logging()

    from daimyo.infrastructure.di import get_container

    try:
        container = get_container()
        repo = container.scope_repository()
        scope = repo.get_scope(scope_name)

        if scope is None:
            typer.echo(f"Error: Scope '{scope_name}' not found", err=True)
            raise typer.Exit(code=1)

        typer.echo(f"# Scope: {scope.metadata.name}")
        typer.echo(f"\nDescription: {scope.metadata.description}")
        if scope.metadata.parent:
            typer.echo(f"Parent: {scope.metadata.parent}")
        if scope.metadata.tags:
            typer.echo(f"Tags: {scope.metadata.tags}")

        typer.echo(f"\nCommandments: {len(scope.commandments.categories)} categories")
        typer.echo(f"Suggestions: {len(scope.suggestions.categories)} categories")

    except Exception as e:
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(code=1)


@app.command()
def context(
    scope_name: str = typer.Argument(
        ...,
        help="Name of the scope to show context for",
    ),
    category: str = typer.Option(
        None,
        "--category",
        "-c",
        help="Specific category to include in context",
    ),
    format: str = typer.Option(
        "yaml",
        "--format",
        "-f",
        help="Output format: yaml, json, or table",
    ),
    show_sources: bool = typer.Option(
        False,
        "--sources",
        "-s",
        help="Show the source of each context variable",
    ),
) -> None:
    """Show template context for a scope.

    :param scope_name: Name of the scope
    :type scope_name: str
    :param category: Optional category name
    :type category: str | None
    :param format: Output format
    :type format: str
    :param show_sources: Whether to show variable sources
    :type show_sources: bool
    :rtype: None
    """
    setup_logging()

    from daimyo.application.formatters.context_formatter import get_context_formatter
    from daimyo.domain import CategoryKey
    from daimyo.infrastructure.di import get_container

    try:
        container = get_container()
        scope_service = container.scope_service()
        template_renderer = container.template_renderer()
        plugin_registry = container.plugin_registry()

        scope = scope_service.resolve_scope(scope_name)
        if scope is None:
            typer.echo(f"Error: Scope '{scope_name}' not found", err=True)
            raise typer.Exit(code=1)

        category_obj = None
        if category:
            category_key = CategoryKey.from_string(category)
            category_obj = scope.commandments.categories.get(
                category_key
            ) or scope.suggestions.categories.get(category_key)
            if category_obj is None:
                typer.echo(f"Warning: Category '{category}' not found in scope", err=True)

        context_data = template_renderer.get_context_with_sources(scope, category_obj)

        enabled_patterns = getattr(settings, "ENABLED_PLUGINS", [])
        filters, tests = plugin_registry.aggregate_filters_and_tests(enabled_patterns)

        formatter = get_context_formatter(format, show_sources)
        output = formatter.format(
            context_data=context_data,
            scope_name=scope_name,
            category_name=category,
            filters=filters,
            tests=tests,
        )
        typer.echo(output)

    except Exception as e:
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(code=1)


def cli() -> None:
    """Entry point for the CLI.

    :rtype: None
    """
    app()


if __name__ == "__main__":
    cli()
