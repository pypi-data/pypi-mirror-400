"""CLI entrypoint for bcrypt speed tests."""

from __future__ import annotations

# ruff: noqa: T201
from typing import Annotated

import typer

from .benchmark import COSTS, ITERATIONS, benchmark_cost

app = typer.Typer(add_completion=False)


def _resolve_costs(costs: list[int] | None) -> list[int]:
    if costs:
        return list(costs)
    return list(COSTS)


@app.callback(invoke_without_command=True)
def run(
    ctx: typer.Context,
    iterations: Annotated[
        int,
        typer.Option(
            "--iterations",
            "-i",
            help="Hashes to run per cost factor.",
            min=1,
        ),
    ] = ITERATIONS,
    costs: Annotated[
        list[int] | None,
        typer.Option(
            "--cost",
            "-c",
            help="Cost factor(s). Repeat to pass multiple values.",
            min=4,
            max=31,
        ),
    ] = None,
) -> None:
    """Run the benchmark and print a timing table."""
    if ctx.invoked_subcommand is not None:
        return
    selected_costs = _resolve_costs(costs)
    print(f"Iterations per cost: {iterations}\n")
    print(f"{'Cost':>4} | {'Avg time (ms)':>12}")
    print("-" * 22)

    for cost in selected_costs:
        avg = benchmark_cost(cost, iterations)
        print(f"{cost:>4} | {avg * 1000:>12.1f}")


def main() -> None:
    """Run the CLI application."""
    app()
