"""Main CLI application."""

import typer
from metapg.cli.commands import migration, pool

app = typer.Typer(
    name="metapg",
    help="Meta PostgreSQL pools and raw SQL migrations",
    no_args_is_help=True,
)

# Add command groups
app.add_typer(migration.app, name="migration", help="Migration management commands")
app.add_typer(pool.app, name="pool", help="Connection pool management commands")

# For backwards compatibility, also add migration commands directly to root
app.command()(migration.status)
app.command()(migration.apply)
app.command()(migration.rollback)
app.command()(migration.create)
