from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class ContainerEngine(str, Enum):
    docker = "docker"
    podman = "podman"


@dataclass
class TopologyContext:
    container_engine: ContainerEngine
    cmd: str | None
    workspace: Path | None
    working_directory: Path
    image: str | None
