import os
from pathlib import Path

import typer as t

from remotivelabs.cli.topology.context import ContainerEngine, TopologyContext
from remotivelabs.cli.topology.typer import (
    ContainerEngineOption,
    TopologyCommandOption,
    TopologyImageOption,
)
from remotivelabs.cli.topology.workspace import find_topology_workspace
from remotivelabs.cli.topology.wrapper import app
from remotivelabs.cli.utils.consent import require_consent
from remotivelabs.cli.utils.console import print_generic_error


@app.callback()
def service_callback(
    ctx: t.Context,
    topology_cmd: str = TopologyCommandOption,
    topology_image: str = TopologyImageOption,
    topology_workspace: str = t.Option(
        None,
        envvar="REMOTIVE_TOPOLOGY_WORKSPACE",
        help="Optional override for workspace path",
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=True,
        readable=True,
    ),
    container_engine: ContainerEngine = ContainerEngineOption,
) -> None:
    require_consent()
    ctx.obj = ctx.obj or {}
    working_directory = Path(os.curdir).absolute().resolve()
    if topology_workspace is None:
        workspace_path = find_topology_workspace(working_directory)
    else:
        workspace_path = Path(topology_workspace).absolute().resolve()
        if not (workspace_path / ".remotive").is_dir():
            print_generic_error(f"Workspace path is not initialized: {workspace_path}")
            raise t.Exit(1)
        if not working_directory.is_relative_to(workspace_path):
            print_generic_error(f"Working directory {working_directory} is not inside the workspace {workspace_path}")
            raise t.Exit(1)
    ctx.obj["topology"] = TopologyContext(
        container_engine=container_engine,
        cmd=topology_cmd,
        workspace=workspace_path,
        working_directory=working_directory,
        image=topology_image,
    )


__all__ = ["app"]
