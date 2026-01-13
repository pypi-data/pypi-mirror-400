import hashlib
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import jwt
import requests

from remotivelabs.cli.settings import settings
from remotivelabs.cli.utils.authorization_keys import public_key
from remotivelabs.cli.utils.rest_helper import RestHelper

logger = logging.getLogger(__name__)


class FeatureNotAuthorizedError(Exception):
    """Raised when not authorized to use a feature"""

    error: str
    details: list[str]

    def __init__(self, error: str, details: list[str]) -> None:
        self.error = error
        self.details = details


@dataclass
class TrackingData:
    feature: str
    action: str
    props: dict[str, str] = field(default_factory=dict)

    def add_prop(self, key: str, value: str, should_add: bool = True) -> "TrackingData":
        """Creates a TrackingData struct with a new key-value pair."""
        if should_add is False:
            return self

        new_props = {**self.props, key: value}
        return TrackingData(feature=self.feature, action=self.action, props=new_props)

    def add_args_info(self, args: list[str]) -> "TrackingData":
        """Adds information about command line arguments."""
        args_hash = hashlib.sha256(" ".join(args).encode()).hexdigest()
        file_suffixes = ",".join(set(Path(arg).suffix for arg in args if Path(arg).suffix))
        new_props = {
            **self.props,
            "args_hash": args_hash,
            "file_suffixes": file_suffixes,
        }
        return TrackingData(feature=self.feature, action=self.action, props=new_props)

    def to_dict(self) -> dict[str, Any]:
        """Converts the TrackingData to a dictionary for JSON serialization."""
        return {"action": self.action, "props": self.props}


def authorize(tracking_data: TrackingData) -> None:
    if settings.get_active_token() is None:
        return _make_auth_request(f"/api/open/features/{tracking_data.feature}/authorize", tracking_data)

    organization = settings.get_organization()
    if organization is None:
        raise FeatureNotAuthorizedError(error="Missing default organization", details=["Try logging in again."])

    url = f"/api/bu/{organization}/features/{tracking_data.feature}/authorize"
    return _make_auth_request(url, tracking_data)


def track(tracking_data: TrackingData) -> None:
    organization = settings.get_organization()
    # TODO: always use open endpoint, include token and organization if available
    if settings.get_active_token() is None or organization is None:
        _make_request(f"/api/open/features/{tracking_data.feature}/authorize", tracking_data)

    else:
        _make_request(f"/api/bu/{organization}/features/{tracking_data.feature}/authorize", tracking_data)


def _make_auth_request(
    url: str,
    params: TrackingData,
) -> None:
    """Make an authorization request to the server."""

    response = _make_request(url, params)

    if response.status_code >= 200 and response.status_code < 300:
        return _process_response_body(response.text)

    if response.status_code in (401, 403):
        raise FeatureNotAuthorizedError(
            error="Verification failed.",
            details=[
                "Please make sure that you are logged in,",
                "have a valid token and that your organization has an active subscription.",
            ],
        )

    raise FeatureNotAuthorizedError(
        error="Server returned an unexpected response.",
        details=[f"(status code {response.status_code}, with body {response.text})", "Please try again or contact RemotiveLabs."],
    )


def _make_request(
    url: str,
    params: TrackingData,
) -> requests.Response:
    body = json.dumps(params.to_dict())
    return RestHelper.handle_simple_post(url=url, body=body)


def _process_response_body(body: str) -> None:
    """Process the response body and verify the JWT token."""
    try:
        data = json.loads(body)
        token = data.get("token")
    except json.JSONDecodeError:
        token = None

    if not token:
        _raise_ensure_latest_version("Received an unexpected response from server.")

    try:
        jwt.decode(token, public_key(RestHelper.get_base_url()), algorithms=["RS256"], leeway=20)
        return
    except jwt.InvalidTokenError:
        _raise_ensure_latest_version("The feature could not be authorized.")


def _raise_ensure_latest_version(error: str) -> None:
    raise FeatureNotAuthorizedError(
        error=error,
        details=["Please ensure you are using the latest version of the software or ", "contact RemotiveLabs if the error persists."],
    )
