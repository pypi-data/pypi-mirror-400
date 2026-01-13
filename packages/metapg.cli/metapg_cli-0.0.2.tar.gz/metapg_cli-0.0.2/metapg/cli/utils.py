"""CLI utility functions."""

import asyncio

from rich.console import Console

console = Console()


def run_async(coro):
    """Run an async function in the CLI."""
    return asyncio.run(coro)
