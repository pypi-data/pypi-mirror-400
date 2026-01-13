from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel

from remotivelabs.cli.settings import settings

router = APIRouter(prefix="/api/studio/v1/environment", tags=["environment"])


class EnvironmentResponse(BaseModel):
    workspace: str
    broker_url: str
    auth_mode: str | None


@router.get("")
def environment(request: Request) -> EnvironmentResponse:
    return EnvironmentResponse(
        workspace=str(request.app.state.topology.workspace), broker_url=str(request.app.state.broker_url), auth_mode=get_auth_mode()
    )


def get_auth_mode() -> str | None:
    if settings.get_active_token():
        return "token"
    return None
