"""Teyaotlani CLI - Spartan Protocol Client & Server.

A modern Spartan protocol implementation using asyncio.
"""

import asyncio
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .client.session import SpartanClient
from .content.gemtext import extract_input_prompts, has_input_prompt
from .protocol.constants import DEFAULT_PORT
from .protocol.response import SpartanResponse
from .protocol.status import interpret_status
from .server.config import ServerConfig
from .server.server import start_server

console = Console()
error_console = Console(stderr=True, style="bold red")

app = typer.Typer(
    name="teyaotlani",
    help="Teyaotlani - A modern Spartan protocol client & server",
    add_completion=True,
    no_args_is_help=True,
)


def _format_response(response: SpartanResponse, verbose: bool = False) -> None:
    """Format and display a Spartan response.

    Args:
        response: The response to display.
        verbose: Whether to show verbose output.
    """
    if verbose:
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Key", style="bold cyan", no_wrap=True)
        table.add_column("Value", style="white")

        # Status with color
        if response.status == 2:
            status_style = "bold green"
        elif response.status == 3:
            status_style = "bold yellow"
        else:
            status_style = "bold red"

        status_text = interpret_status(response.status)
        table.add_row("Status", f"[{status_style}]{response.status}[/] ({status_text})")
        table.add_row("Meta", response.meta)

        if response.url:
            table.add_row("URL", response.url)

        console.print(table)
        console.print()

    # Display body or error
    if response.body:
        if isinstance(response.body, bytes):
            console.print(response.body.decode("utf-8", errors="replace"))
        else:
            console.print(response.body)

        # Check for input prompts
        if isinstance(response.body, str) and has_input_prompt(response.body):
            prompts = extract_input_prompts(response.body)
            if prompts and not verbose:
                console.print()
                console.print(
                    f"[dim]This page has {len(prompts)} input prompt(s). "
                    "Use --verbose to see details.[/]"
                )
    elif response.status != 2:
        if not verbose:
            if response.status == 2:
                status_style = "bold green"
            elif response.status == 3:
                status_style = "bold yellow"
            else:
                status_style = "bold red"
            console.print(f"[{status_style}][{response.status}][/] {response.meta}")


@app.command()
def get(
    url: str = typer.Argument(..., help="Spartan URL to get"),
    timeout: float = typer.Option(
        30.0, "--timeout", "-t", help="Request timeout in seconds"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show verbose output with headers"
    ),
) -> None:
    """Get a Spartan resource and display it.

    Examples:

        # Get a URL
        $ teyaotlani get spartan://example.com/

        # Get with verbose output
        $ teyaotlani get -v spartan://example.com/page.gmi
    """

    async def _get() -> None:
        try:
            async with SpartanClient(timeout=timeout) as client:
                response = await client.get(url)
                _format_response(response, verbose=verbose)

                if response.status >= 4:
                    raise typer.Exit(code=1)

        except ValueError as e:
            error_console.print(f"Invalid URL: {e}")
            raise typer.Exit(code=1) from e
        except TimeoutError as e:
            error_console.print(f"Timeout: {e}")
            raise typer.Exit(code=1) from e
        except ConnectionError as e:
            error_console.print(f"Connection error: {e}")
            raise typer.Exit(code=1) from e
        except Exception as e:
            error_console.print(f"Error: {e}")
            raise typer.Exit(code=1) from e

    asyncio.run(_get())


@app.command()
def upload(
    url: str = typer.Argument(..., help="Spartan URL to upload to"),
    content: str = typer.Option(
        None, "--content", "-c", help="Content to upload (string)"
    ),
    file: Path = typer.Option(
        None,
        "--file",
        "-f",
        help="File to upload",
        exists=True,
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
    ),
    timeout: float = typer.Option(
        30.0, "--timeout", "-t", help="Request timeout in seconds"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show verbose output"),
) -> None:
    """Upload content to a Spartan server.

    Examples:

        # Upload string content
        $ teyaotlani upload spartan://example.com/file.txt -c "Hello, world!"

        # Upload a file
        $ teyaotlani upload spartan://example.com/doc.gmi -f document.gmi
    """
    if content is None and file is None:
        error_console.print("Either --content or --file is required")
        raise typer.Exit(code=1)

    if content is not None and file is not None:
        error_console.print("Cannot specify both --content and --file")
        raise typer.Exit(code=1)

    async def _upload() -> None:
        try:
            # Get content
            if file is not None:
                upload_content = file.read_bytes()
            else:
                upload_content = content.encode("utf-8")  # type: ignore[union-attr]

            async with SpartanClient(timeout=timeout) as client:
                response = await client.upload(url, upload_content)
                _format_response(response, verbose=verbose)

                if response.status >= 4:
                    raise typer.Exit(code=1)

        except ValueError as e:
            error_console.print(f"Invalid URL: {e}")
            raise typer.Exit(code=1) from e
        except TimeoutError as e:
            error_console.print(f"Timeout: {e}")
            raise typer.Exit(code=1) from e
        except ConnectionError as e:
            error_console.print(f"Connection error: {e}")
            raise typer.Exit(code=1) from e
        except Exception as e:
            error_console.print(f"Error: {e}")
            raise typer.Exit(code=1) from e

    asyncio.run(_upload())


@app.command()
def serve(
    root: Path = typer.Argument(
        None,
        help="Document root directory",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    config_file: Path = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to TOML configuration file",
        exists=True,
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
    ),
    host: str = typer.Option(None, "--host", "-H", help="Server host address"),
    port: int = typer.Option(None, "--port", "-p", help="Server port"),
    enable_directory_listing: bool = typer.Option(
        False, "--directory-listing", "-d", help="Enable directory listings"
    ),
    log_level: str = typer.Option(
        "INFO", "--log-level", "-l", help="Logging level (DEBUG, INFO, WARNING, ERROR)"
    ),
    json_logs: bool = typer.Option(
        False, "--json-logs", help="Output logs in JSON format"
    ),
) -> None:
    """Start a Spartan server to serve files.

    Examples:

        # Serve current directory
        $ teyaotlani serve .

        # Serve with config file
        $ teyaotlani serve --config config.toml

        # Serve with directory listings enabled
        $ teyaotlani serve ./capsule --directory-listing

        # Serve on custom port
        $ teyaotlani serve ./capsule --port 3000
    """

    async def _serve() -> None:
        try:
            if config_file:
                # Load from config file
                config = ServerConfig.from_toml(config_file)

                # CLI overrides
                if host is not None:
                    config.host = host
                if port is not None:
                    config.port = port
                if root is not None:
                    config.document_root = root
                if enable_directory_listing:
                    config.enable_directory_listing = True
                config.log_level = log_level
                config.json_logs = json_logs
            else:
                # Create config from CLI arguments
                if root is None:
                    error_console.print("Document root is required (or use --config)")
                    raise typer.Exit(code=1)

                config = ServerConfig(
                    host=host or "localhost",
                    port=port or DEFAULT_PORT,
                    document_root=root,
                    enable_directory_listing=enable_directory_listing,
                    log_level=log_level,
                    json_logs=json_logs,
                )

            await start_server(config)

        except FileNotFoundError as e:
            error_console.print(f"Config file not found: {e}")
            raise typer.Exit(code=1) from e
        except ValueError as e:
            error_console.print(f"Configuration error: {e}")
            raise typer.Exit(code=1) from e
        except OSError as e:
            error_console.print(f"Server error: {e}")
            raise typer.Exit(code=1) from e
        except KeyboardInterrupt:
            pass  # Normal shutdown

    asyncio.run(_serve())


@app.command()
def version() -> None:
    """Show version information."""
    console.print("[bold cyan]Teyaotlani[/] - Spartan Protocol Client & Server")
    console.print("[bold]Version:[/] 0.1.0")
    console.print("[bold]Protocol:[/] Spartan (spartan://)")
    console.print("[bold]Default Port:[/] 300")
    console.print()
    console.print("[dim]Named after the Nahuatl word for 'warrior'[/]")


def main() -> None:
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
