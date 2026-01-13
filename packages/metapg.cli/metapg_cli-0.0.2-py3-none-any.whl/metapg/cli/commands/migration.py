"""Migration management commands."""

from pathlib import Path

import typer
from metapg.cli.utils import console, run_async
from metapg.migrations import MigrationRunner
from rich.table import Table
from rich.text import Text

app = typer.Typer()


@app.command()
def status(
    db: str = typer.Option("default", "--db", "-d", help="Database name"),
    migrations_dir: str | None = typer.Option(
        None,
        "--migrations-dir",
        help="Migrations directory",
    ),
):
    """Show migration status for a database."""

    async def _status():
        migrations_path = Path(migrations_dir) if migrations_dir else None
        runner = MigrationRunner(db, migrations_path)
        status = await runner.get_status()

        # Create status table
        table = Table(title=f"Migration Status: {db}")
        table.add_column("Migration", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Applied", style="green")
        table.add_column("Duration", justify="right")

        # Add applied migrations
        for record in status.applied:
            duration_text = f"{record.duration_ms:.1f}ms" if record.duration_ms else ""
            status_text = (
                Text("✓ Applied", style="green")
                if not record.error
                else Text("✗ Failed", style="red")
            )
            table.add_row(
                record.name,
                status_text,
                str(record.applied_at.strftime("%Y-%m-%d %H:%M")),
                duration_text,
            )

        # Add pending migrations
        for migration in status.pending:
            table.add_row(
                migration.name,
                Text("○ Pending", style="yellow"),
                "",
                "",
            )

        console.print(table)

        # Summary
        if status.is_up_to_date:
            console.print("\n[green]✓ Database is up to date[/green]")
        else:
            console.print(
                f"\n[yellow]○ {len(status.pending)} migrations pending[/yellow]",
            )

    run_async(_status())


@app.command()
def apply(
    db: str = typer.Option("default", "--db", "-d", help="Database name"),
    target: str | None = typer.Option(
        None,
        "--target",
        "-t",
        help="Target migration",
    ),
    migrations_dir: str | None = typer.Option(
        None,
        "--migrations-dir",
        help="Migrations directory",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Apply without confirmation",
    ),
):
    """Apply pending migrations."""

    async def _apply():
        migrations_path = Path(migrations_dir) if migrations_dir else None
        runner = MigrationRunner(db, migrations_path)

        # Check status first
        status = await runner.get_status()

        if not status.pending:
            console.print("[green]✓ Database is up to date[/green]")
            return

        to_apply = status.pending
        if target:
            # Find target
            target_idx = None
            for i, migration in enumerate(to_apply):
                if (
                    migration.name == target
                    or str(migration.version).zfill(3) in target
                ):
                    target_idx = i
                    break

            if target_idx is None:
                console.print(
                    f"[red]Error: Target migration '{target}' not found[/red]",
                )
                raise typer.Exit(1)

            to_apply = to_apply[: target_idx + 1]

        # Show what will be applied
        console.print(f"\n[cyan]Migrations to apply ({db}):[/cyan]")
        for migration in to_apply:
            desc = f" - {migration.description}" if migration.description else ""
            console.print(f"  [yellow]→[/yellow] {migration.name}{desc}")

        # Confirm unless forced
        if not force:
            if not typer.confirm(f"\nApply {len(to_apply)} migrations to '{db}'?"):
                console.print("Cancelled")
                return

        console.print()

        # Apply migrations
        try:
            for migration in to_apply:
                console.print(f"[blue]→[/blue] Applying {migration.name}...")
                await runner.apply_migration(migration)
                console.print(f"[green]✓[/green] Applied {migration.name}")

            console.print(
                f"\n[green]✓ Successfully applied {len(to_apply)} migrations[/green]",
            )

        except Exception as e:
            console.print(f"\n[red]✗ Migration failed: {e}[/red]")
            raise typer.Exit(1)

    run_async(_apply())


@app.command()
def rollback(
    db: str = typer.Option("default", "--db", "-d", help="Database name"),
    steps: int = typer.Option(
        1,
        "--steps",
        "-n",
        help="Number of migrations to rollback",
    ),
    migrations_dir: str | None = typer.Option(
        None,
        "--migrations-dir",
        help="Migrations directory",
    ),
):
    """Rollback applied migrations."""

    async def _rollback():
        migrations_path = Path(migrations_dir) if migrations_dir else None
        runner = MigrationRunner(db, migrations_path)

        # Get applied migrations
        applied = await runner.get_applied_migrations()

        if not applied:
            console.print("[yellow]No migrations to rollback[/yellow]")
            return

        # Get migrations to rollback (most recent first)
        to_rollback = applied[-steps:] if steps <= len(applied) else applied
        to_rollback.reverse()

        console.print(f"\n[cyan]Migrations to rollback ({db}):[/cyan]")
        for record in to_rollback:
            console.print(f"  [yellow]←[/yellow] {record.name}")

        if not typer.confirm(f"\nRollback {len(to_rollback)} migrations from '{db}'?"):
            console.print("Cancelled")
            return

        console.print()

        # Rollback migrations
        try:
            for record in to_rollback:
                console.print(f"[blue]←[/blue] Rolling back {record.name}...")
                await runner.rollback_migration(record.name)
                console.print(f"[green]✓[/green] Rolled back {record.name}")

            console.print(
                f"\n[green]✓ Successfully rolled back {len(to_rollback)} migrations[/green]",
            )

        except Exception as e:
            console.print(f"\n[red]✗ Rollback failed: {e}[/red]")
            raise typer.Exit(1)

    run_async(_rollback())


@app.command()
def create(
    name: str = typer.Argument(..., help="Migration name (e.g., 'add_user_index')"),
    db: str = typer.Option("default", "--db", "-d", help="Database name"),
    migrations_dir: str | None = typer.Option(
        None,
        "--migrations-dir",
        help="Migrations directory",
    ),
):
    """Create a new migration file."""
    migrations_path = (
        Path(migrations_dir) if migrations_dir else Path("migrations") / db
    )
    migrations_path.mkdir(parents=True, exist_ok=True)

    # Find next version number
    existing = list(migrations_path.glob("*.sql"))
    if existing:
        versions = []
        for f in existing:
            try:
                version = int(f.stem.split("_")[0])
                versions.append(version)
            except (ValueError, IndexError):
                continue
        next_version = max(versions) + 1 if versions else 1
    else:
        next_version = 1

    # Create filename
    clean_name = name.replace(" ", "_").replace("-", "_").lower()
    filename = f"{next_version:03d}_{clean_name}.sql"
    file_path = migrations_path / filename

    # Get current date
    from datetime import datetime

    current_date = datetime.now().strftime("%Y-%m-%d")

    # Create template content
    template = f"""-- {name.replace("_", " ").title()}
-- Created: {current_date}

-- Your migration SQL here
-- CREATE TABLE ...

-- ROLLBACK (optional)
-- DROP TABLE ...
"""

    file_path.write_text(template)
    console.print(f"[green]✓[/green] Created migration: {file_path}")
