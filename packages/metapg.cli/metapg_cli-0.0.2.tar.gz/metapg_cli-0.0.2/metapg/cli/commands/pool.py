"""Connection pool management commands."""

import os

import typer
from metapg.cli.utils import console, run_async
from metapg.pool import close_all_pools, close_pool, get_pool, init_pool
from rich.table import Table

app = typer.Typer()


@app.command()
def init(
    db_name: str = typer.Argument("default", help="Database pool name"),
    dsn: str | None = typer.Option(
        None,
        "--dsn",
        help="Database connection string",
    ),
    min_size: int = typer.Option(1, "--min-size", help="Minimum pool size"),
    max_size: int = typer.Option(20, "--max-size", help="Maximum pool size"),
):
    """Initialize a database connection pool."""

    if dsn is None:
        if db_name == "default":
            dsn = os.getenv("DATABASE_URL")
        else:
            env_key = f"DATABASE_URL_{db_name.upper()}"
            dsn = os.getenv(env_key)

        if dsn is None:
            console.print(
                f"[red]Error: No DSN provided and {env_key if db_name != 'default' else 'DATABASE_URL'} not set[/red]",
            )
            raise typer.Exit(1)

    try:
        pool = init_pool(dsn=dsn, db_name=db_name, min_size=min_size, max_size=max_size)
        console.print(
            f"[green]✓[/green] Initialized pool '{db_name}' (min: {min_size}, max: {max_size})",
        )
    except Exception as e:
        console.print(f"[red]✗ Failed to initialize pool: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def status(
    db_name: str | None = typer.Argument(None, help="Database pool name (optional)"),
):
    """Show connection pool status."""

    async def _status():
        try:
            if db_name:
                # Show status for specific pool
                pool = get_pool(db_name)
                table = Table(title=f"Pool Status: {db_name}")
                table.add_column("Property", style="cyan")
                table.add_column("Value", style="yellow")

                table.add_row("Pool Name", db_name)
                table.add_row("Min Size", str(pool.min_size))
                table.add_row("Max Size", str(pool.max_size))
                table.add_row(
                    "Current Size",
                    str(len(pool._pool)) if hasattr(pool, "_pool") else "N/A",
                )
                table.add_row(
                    "Available",
                    (
                        str(pool._available.qsize())
                        if hasattr(pool, "_available")
                        else "N/A"
                    ),
                )

                console.print(table)
            else:
                # Show all pools (this would require tracking in the pool module)
                console.print(
                    "[yellow]Pool listing not implemented. Specify a pool name.[/yellow]",
                )

        except Exception as e:
            console.print(f"[red]✗ Error: {e}[/red]")
            raise typer.Exit(1)

    run_async(_status())


@app.command()
def close(
    db_name: str | None = typer.Argument(
        None,
        help="Database pool name (all if not specified)",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force close without confirmation",
    ),
):
    """Close database connection pool(s)."""

    async def _close():
        try:
            if db_name:
                if not force:
                    if not typer.confirm(f"Close pool '{db_name}'?"):
                        console.print("Cancelled")
                        return

                await close_pool(db_name)
                console.print(f"[green]✓[/green] Closed pool '{db_name}'")
            else:
                if not force:
                    if not typer.confirm("Close all pools?"):
                        console.print("Cancelled")
                        return

                await close_all_pools()
                console.print("[green]✓[/green] Closed all pools")

        except Exception as e:
            console.print(f"[red]✗ Error: {e}[/red]")
            raise typer.Exit(1)

    run_async(_close())
