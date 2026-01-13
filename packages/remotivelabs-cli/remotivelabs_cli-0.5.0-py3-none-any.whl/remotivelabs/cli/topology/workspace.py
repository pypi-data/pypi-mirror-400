from dataclasses import replace
from pathlib import Path

import typer

from remotivelabs.cli.typer import typer_utils
from remotivelabs.cli.utils.analytics import TrackingData, authorize, track
from remotivelabs.cli.utils.console import print_generic_error, print_generic_message, print_success

HELP = """
Manage RemotiveTopology workspaces
"""

app = typer_utils.create_typer_sorted(rich_markup_mode="rich", help=HELP)


@app.command("init", help="Initialize a RemotiveTopology workspace in the current directory")
def init(
    ctx: typer.Context,
    force: bool = typer.Option(default=False, help="Override existing RemotiveTopology workspace if it exists"),
) -> None:
    if ctx.obj["topology"].workspace is not None and not force:
        print_generic_message(f"RemotiveTopology workspace is already initialized: {ctx.obj['topology'].workspace}")
        raise typer.Exit(1)
    authorize(TrackingData(feature="topology", action="init"))
    ctx.obj["topology"] = replace(ctx.obj["topology"], workspace=Path(ctx.obj["topology"].working_directory))
    init_workspace(ctx.obj["topology"].workspace)
    print_success("RemotiveTopology workspace initialized")


@app.command("current", help="Show the current RemotiveTopology workspace")
def current(
    ctx: typer.Context,
) -> None:
    track(TrackingData(feature="topology", action="current"))
    workspace = ctx.obj["topology"].workspace
    if workspace is None:
        print_generic_error("RemotiveTopology workspace not initialized")
        raise typer.Exit(1)
    print_generic_message(f"Current RemotiveTopology workspace: {workspace}")


def init_workspace(workspace_path: Path) -> None:
    Path.mkdir(workspace_path / ".remotive", exist_ok=True)
    gitignore_path = workspace_path / ".remotive" / ".gitignore"
    if not gitignore_path.is_file():
        gitignore_path.write_text("# Automatically created by RemotiveTopology\n*\n!.gitignore\n")


def find_topology_workspace(start_path: Path) -> Path | None:
    """
    Find the RemotiveTopology workspace by looking for a .remotive folder
    in the current directory or any of its parent directories.

    Args:
        start_path (Path): The starting directory to search from.

    Returns:
        Path: The path to the RemotiveTopology workspace."""

    for dir in [start_path] + list(start_path.parents):
        remotive_dir = dir / ".remotive"
        if remotive_dir.is_dir():
            return dir
    return None
