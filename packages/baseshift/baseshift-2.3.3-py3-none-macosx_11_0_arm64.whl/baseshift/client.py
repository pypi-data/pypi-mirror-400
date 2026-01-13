"""
API client for Baseshift REST API (v2 only).

All functions require JWT authentication via Bearer token.
Run 'baseshift auth login' before using any API functions.

No v1 API support - all endpoints use /api/v2/* paths.
"""

import httpx
import json
import logging
from .version import VERSION
from .auth_token import get_token_manager, AuthenticationError, LOGIN_REQUIRED_MESSAGE

logger = logging.getLogger(__name__)


def get_ci_info():
    """Gathers CI/CD environment variables from the environment."""
    import os

    CI_PIPELINE_ID = os.environ.get("CI_PIPELINE_ID") or os.environ.get("GITHUB_RUN_ID")
    CI_COMMIT_REF_NAME = os.environ.get("CI_COMMIT_REF_NAME") or os.environ.get(
        "GITHUB_HEAD_REF"
    )
    CI_COMMIT_SHA = os.environ.get("CI_COMMIT_SHA") or os.environ.get("GITHUB_SHA")
    CI_MERGE_REQUEST_IID = os.environ.get("CI_MERGE_REQUEST_IID", "github")
    CI_DEFAULT_BRANCH = os.environ.get("CI_DEFAULT_BRANCH") or os.environ.get(
        "GITHUB_BASE_REF"
    )
    CI_USER = os.environ.get("GITHUB_ACTOR") or os.environ.get("GITLAB_USER_LOGIN")

    return {
        "CI_PIPELINE_ID": CI_PIPELINE_ID,
        "CI_COMMIT_REF_NAME": CI_COMMIT_REF_NAME,
        "CI_COMMIT_SHA": CI_COMMIT_SHA,
        "CI_MERGE_REQUEST_IID": CI_MERGE_REQUEST_IID,
        "CI_DEFAULT_BRANCH": CI_DEFAULT_BRANCH,
        "CI_USER": CI_USER,
    }


def get_auth_headers(host: str):
    """
    Get authentication headers for API requests.

    Args:
        host: API host URL

    Returns:
        dict with Authorization header, or None if not authenticated
    """
    token_manager = get_token_manager()
    return token_manager.get_auth_header(host)


async def start_clone_api_async(
    dub_uuid: str,
    host: str,
    grace: int = None,
    timeout: int = None,
    clone_config: dict = None,
):
    """
    Asynchronously call the v2 clone start API with JWT authentication.

    Args:
        dub_uuid: UUID of the dub
        host: API host URL
        grace: Inactivity grace period in seconds
        timeout: Inactivity timeout in seconds
        clone_config: Clone configuration dict

    Returns:
        httpx.Response object
    """
    # Get auth headers
    auth_headers = get_auth_headers(host)

    if not auth_headers:
        raise AuthenticationError(LOGIN_REQUIRED_MESSAGE)

    # Build request body
    json_msg = {
        "dubUuid": dub_uuid,
        "VERSION": VERSION,
        **get_ci_info(),
    }

    if grace:
        json_msg["INACTIVITY_GRACE_SECS"] = grace
    if timeout:
        json_msg["INACTIVITY_TIMEOUT_SECS"] = timeout
    if clone_config:
        json_msg["cloneConfig"] = clone_config

    async with httpx.AsyncClient() as client:
        return await client.post(
            f"{host}/api/v2/dubhub/clone/start",
            json=json_msg,
            headers=auth_headers,
            timeout=300.0,
        )


def start_clone_api_sync(
    dub_uuid: str,
    host: str,
    grace: int = None,
    timeout: int = None,
    clone_config: dict = None,
):
    """
    Synchronously call the v2 clone start API with JWT authentication.

    Args:
        dub_uuid: UUID of the dub
        host: API host URL
        grace: Inactivity grace period in seconds
        timeout: Inactivity timeout in seconds
        clone_config: Clone configuration dict

    Returns:
        httpx.Response object
    """
    # Get auth headers
    auth_headers = get_auth_headers(host)

    if not auth_headers:
        raise AuthenticationError(LOGIN_REQUIRED_MESSAGE)

    # Build request body
    json_msg = {
        "dubUuid": dub_uuid,
        "VERSION": VERSION,
        **get_ci_info(),
    }

    if grace:
        json_msg["INACTIVITY_GRACE_SECS"] = grace
    if timeout:
        json_msg["INACTIVITY_TIMEOUT_SECS"] = timeout
    if clone_config:
        json_msg["cloneConfig"] = clone_config

    with httpx.Client() as client:
        return client.post(
            f"{host}/api/v2/dubhub/clone/start",
            json=json_msg,
            headers=auth_headers,
            timeout=300.0,
        )


async def stop_clone_api_async(clone_uuid: str, host: str):
    """
    Asynchronously call the v2 clone stop API with JWT authentication.

    Args:
        clone_uuid: UUID of the clone to stop
        host: API host URL

    Returns:
        httpx.Response object
    """
    # Get auth headers
    auth_headers = get_auth_headers(host)

    if not auth_headers:
        raise AuthenticationError(LOGIN_REQUIRED_MESSAGE)

    # Build request body
    json_msg = {"cloneUuid": clone_uuid}

    async with httpx.AsyncClient() as client:
        return await client.post(
            f"{host}/api/v2/dubhub/clone/stop",
            json=json_msg,
            headers=auth_headers,
            timeout=60.0,
        )


def stop_clone_api_sync(clone_uuid: str, host: str):
    """
    Synchronously call the v2 clone stop API with JWT authentication.

    Args:
        clone_uuid: UUID of the clone to stop
        host: API host URL

    Returns:
        httpx.Response object
    """
    # Get auth headers
    auth_headers = get_auth_headers(host)

    if not auth_headers:
        raise AuthenticationError(LOGIN_REQUIRED_MESSAGE)

    # Build request body
    json_msg = {"cloneUuid": clone_uuid}

    with httpx.Client() as client:
        return client.post(
            f"{host}/api/v2/dubhub/clone/stop",
            json=json_msg,
            headers=auth_headers,
            timeout=60.0,
        )


async def schema_diff_api_async(clone_uuid: str, host: str):
    """
    Get schema diff for a clone using v2 API with JWT authentication (async).

    Args:
        clone_uuid: UUID of the clone
        host: API host URL

    Returns:
        httpx.Response object
    """
    # Get auth headers
    auth_headers = get_auth_headers(host)

    if not auth_headers:
        raise AuthenticationError(LOGIN_REQUIRED_MESSAGE)

    # Build query params
    params = {"cloneUuid": clone_uuid}

    async with httpx.AsyncClient() as client:
        return await client.get(
            f"{host}/api/v2/dubhub/clone/schema_diff",
            params=params,
            headers=auth_headers,
            timeout=60.0,
        )


def schema_diff_api_sync(clone_uuid: str, host: str):
    """
    Get schema diff for a clone using v2 API with JWT authentication.

    Args:
        clone_uuid: UUID of the clone
        host: API host URL

    Returns:
        httpx.Response object
    """
    # Get auth headers
    auth_headers = get_auth_headers(host)

    if not auth_headers:
        raise AuthenticationError(LOGIN_REQUIRED_MESSAGE)

    # Build query params
    params = {"cloneUuid": clone_uuid}

    with httpx.Client() as client:
        return client.get(
            f"{host}/api/v2/dubhub/clone/schema_diff",
            params=params,
            headers=auth_headers,
            timeout=60.0,
        )


def analyse_clone_api_sync(
    clone_uuid: str,
    host: str,
    method: str = "GET",
):
    """
    Analyse a clone using v2 API with JWT authentication.

    Args:
        clone_uuid: UUID of the clone
        host: API host URL
        method: HTTP method ("GET" or "POST")

    Returns:
        httpx.Response object
    """
    auth_headers = get_auth_headers(host)

    if not auth_headers:
        raise AuthenticationError(LOGIN_REQUIRED_MESSAGE)

    params = {"cloneUuid": clone_uuid}

    with httpx.Client() as client:
        if method.upper() == "POST":
            return client.post(
                f"{host}/api/v2/baseguard/analyse/clone",
                json=params,
                headers=auth_headers,
                timeout=300.0,
            )
        else:
            return client.get(
                f"{host}/api/v2/baseguard/analyse/clone",
                params=params,
                headers=auth_headers,
                timeout=300.0,
            )


async def clone_query_diff_api_async(
    clone_uuid: str,
    host: str,
    base_clone_uuid: str = None,
):
    """
    Get query diff for a clone using v2 API with JWT authentication (async).

    Args:
        clone_uuid: UUID of the clone
        host: API host URL
        base_clone_uuid: Optional base clone UUID for comparison

    Returns:
        httpx.Response object
    """
    auth_headers = get_auth_headers(host)

    if not auth_headers:
        raise AuthenticationError(LOGIN_REQUIRED_MESSAGE)

    params = {"cloneUuid": clone_uuid}

    if base_clone_uuid:
        params["baseCloneUuid"] = base_clone_uuid

    async with httpx.AsyncClient() as client:
        return await client.get(
            f"{host}/api/v2/dubhub/clone/query_diff",
            params=params,
            headers=auth_headers,
            timeout=60.0,
        )


def clone_query_diff_api_sync(clone_uuid: str, host: str):
    """
    Get query diff for a clone using v2 API with JWT authentication.

    Args:
        clone_uuid: UUID of the clone
        host: API host URL

    Returns:
        httpx.Response object
    """
    auth_headers = get_auth_headers(host)

    if not auth_headers:
        raise AuthenticationError(LOGIN_REQUIRED_MESSAGE)

    params = {"cloneUuid": clone_uuid}

    with httpx.Client() as client:
        return client.get(
            f"{host}/api/v2/dubhub/clone/query_diff",
            params=params,
            headers=auth_headers,
            timeout=60.0,
        )


def clone_query_issues_api_sync(clone_uuid: str, host: str):
    """
    Get query issues for a clone using v2 API with JWT authentication.

    Args:
        clone_uuid: UUID of the clone
        host: API host URL

    Returns:
        httpx.Response object
    """
    auth_headers = get_auth_headers(host)

    if not auth_headers:
        raise AuthenticationError(LOGIN_REQUIRED_MESSAGE)

    params = {"cloneUuid": clone_uuid}

    with httpx.Client() as client:
        return client.get(
            f"{host}/api/v2/dubhub/clone/query_issues",
            params=params,
            headers=auth_headers,
            timeout=60.0,
        )


def replication_monitoring_stats_api_sync(dub_uuid: str, host: str):
    """
    Get replication monitoring stats for a dub using v2 API with JWT authentication.

    Args:
        dub_uuid: UUID of the dub
        host: API host URL

    Returns:
        httpx.Response object
    """
    auth_headers = get_auth_headers(host)

    if not auth_headers:
        raise AuthenticationError(LOGIN_REQUIRED_MESSAGE)

    params = {"dubUuid": dub_uuid}

    with httpx.Client() as client:
        return client.get(
            f"{host}/api/v2/dubhub/replication_monitoring_stats",
            params=params,
            headers=auth_headers,
            timeout=60.0,
        )


def repserver_state_api_sync(dub_uuid: str, host: str):
    """
    Get repserver state for a dub using v2 API with JWT authentication.

    Args:
        dub_uuid: UUID of the dub
        host: API host URL

    Returns:
        httpx.Response object
    """
    auth_headers = get_auth_headers(host)

    if not auth_headers:
        raise AuthenticationError(LOGIN_REQUIRED_MESSAGE)

    params = {"dubUuid": dub_uuid}

    with httpx.Client() as client:
        return client.get(
            f"{host}/api/v2/dubhub/repserver_state",
            params=params,
            headers=auth_headers,
            timeout=60.0,
        )


def snapshot_api_sync(dub_uuid: str, host: str):
    """
    Create a snapshot for a dub using v2 API with JWT authentication.

    Args:
        dub_uuid: UUID of the dub
        host: API host URL

    Returns:
        httpx.Response object
    """
    auth_headers = get_auth_headers(host)

    if not auth_headers:
        raise AuthenticationError(LOGIN_REQUIRED_MESSAGE)

    data = {"dubUuid": dub_uuid}

    with httpx.Client() as client:
        return client.post(
            f"{host}/api/v2/dubhub/snapshot/create",
            json=data,
            headers=auth_headers,
            timeout=300.0,
        )


def snapshot_status_api_sync(snapshot_uuid: str, host: str):
    """
    Get snapshot status using v2 API with JWT authentication.

    Args:
        snapshot_uuid: UUID of the snapshot
        host: API host URL

    Returns:
        httpx.Response object
    """
    auth_headers = get_auth_headers(host)

    if not auth_headers:
        raise AuthenticationError(LOGIN_REQUIRED_MESSAGE)

    params = {"snapshot_uuid": snapshot_uuid}

    with httpx.Client() as client:
        return client.get(
            f"{host}/api/v2/dubhub/snapshot/status",
            params=params,
            headers=auth_headers,
            timeout=60.0,
        )


def subset_edit_api_sync(
    dub_uuid: str,
    host: str,
    subset_config: str,
):
    """
    Edit subset configuration using v2 API with JWT authentication.

    Args:
        dub_uuid: UUID of the dub
        host: API host URL
        subset_config: Subset configuration string (JSON)

    Returns:
        httpx.Response object
    """
    auth_headers = get_auth_headers(host)

    if not auth_headers:
        raise AuthenticationError(LOGIN_REQUIRED_MESSAGE)

    data = {
        "dubUuid": dub_uuid,
        "config": (
            json.loads(subset_config)
            if isinstance(subset_config, str)
            else subset_config
        ),
    }

    with httpx.Client() as client:
        return client.post(
            f"{host}/api/v2/dubhub/subset",
            json=data,
            headers=auth_headers,
            timeout=60.0,
        )


def change_masking_rules_api_sync(dub_uuid: str, host: str, config: dict):
    """
    Change masking rules using v2 API with JWT authentication.

    Args:
        dub_uuid: UUID of the dub
        host: API host URL
        config: Configuration dictionary with:
            - restart_dub: bool (required) - Restart dub after applying changes
            - override_policy: bool (required) - Delete existing rules before applying
            - ignore_errors: bool (optional, default: false) - Continue on errors
            - dry_run: bool (optional, default: false) - Validate without applying
            - manual_rules: list (optional) - List of masking rules
              Each rule: {"table": "db.schema.table", "column": "col", "masking_function": "func", ...}

    Returns:
        httpx.Response object
    """
    auth_headers = get_auth_headers(host)

    if not auth_headers:
        raise AuthenticationError(LOGIN_REQUIRED_MESSAGE)

    data = {"dubUuid": dub_uuid, "config": config}

    with httpx.Client() as client:
        return client.post(
            f"{host}/api/v2/dubhub/masking",
            json=data,
            headers=auth_headers,
            timeout=60.0,
        )


def list_masking_rules_api_sync(
    dub_uuid: str,
    host: str,
    return_unmasked: bool = False,
):
    """
    List masking rules using v2 API with JWT authentication.

    Args:
        dub_uuid: UUID of the dub
        host: API host URL
        return_unmasked: Include rules with 'unmasked' category (optional, default: false)

    Returns:
        httpx.Response object
    """
    auth_headers = get_auth_headers(host)

    if not auth_headers:
        raise AuthenticationError(LOGIN_REQUIRED_MESSAGE)

    params = {"dubUuid": dub_uuid}

    if return_unmasked:
        params["return_unmasked_categories"] = "true"

    with httpx.Client() as client:
        return client.get(
            f"{host}/api/v2/dubhub/masking/list",
            params=params,
            headers=auth_headers,
            timeout=60.0,
        )


def create_hub_api_sync(
    hub_name: str,
    dub_uuid_list: list,
    host: str,
    org_token: str = None,
    org_uuid: str = None,
    schedule: str = "never",
):
    """
    Create a new hub/environment using v2 API with JWT authentication.

    Args:
        hub_name: Name of the hub/environment
        dub_uuid_list: List of Dub UUIDs to add to the hub
        host: API host URL
        org_token: Organization token (optional, for legacy compatibility)
        org_uuid: Organization UUID (preferred)
        schedule: Snapshot schedule ("never", "daily", "weekly", "monthly")

    Returns:
        httpx.Response object
    """
    auth_headers = get_auth_headers(host)

    if not auth_headers:
        raise AuthenticationError(LOGIN_REQUIRED_MESSAGE)

    data = {"name": hub_name, "dubUuidList": dub_uuid_list, "schedule": schedule}

    if org_uuid:
        data["orgUuid"] = org_uuid
    elif org_token:
        data["orgToken"] = org_token
    else:
        raise ValueError("Either org_uuid or org_token must be provided")

    with httpx.Client() as client:
        return client.post(
            f"{host}/api/v2/dubhub/environment/create",
            json=data,
            headers=auth_headers,
            timeout=60.0,
        )


def hub_snapshot_api_sync(
    env_uuid: str,
    host: str,
    method: str = "POST",
    prepare_only: bool = False,
    tag: str = None,
    snapshot_uuid: str = None,
):
    """
    Manage hub/environment snapshots using v2 API with JWT authentication.

    Args:
        env_uuid: UUID of the hub/environment
        host: API host URL
        method: HTTP method ("GET" or "POST")
        prepare_only: If True, only prepare the snapshot without creating it
        tag: Optional tag for the snapshot
        snapshot_uuid: UUID of snapshot to check status (for GET)

    Returns:
        httpx.Response object
    """
    auth_headers = get_auth_headers(host)

    if not auth_headers:
        raise AuthenticationError(LOGIN_REQUIRED_MESSAGE)

    data = {"envUuid": env_uuid}

    with httpx.Client() as client:
        if method.upper() == "POST":
            data["prepareOnly"] = prepare_only
            if tag:
                data["tag"] = tag
            return client.post(
                f"{host}/api/v2/dubhub/environment/snapshot",
                json=data,
                headers=auth_headers,
                timeout=300.0,
            )
        else:
            if snapshot_uuid:
                data["snapshotUuid"] = snapshot_uuid
            return client.get(
                f"{host}/api/v2/dubhub/environment/snapshot",
                params=data,
                headers=auth_headers,
                timeout=60.0,
            )


def hub_status_api_sync(env_uuid: str, host: str):
    """
    Get hub/environment status using v2 API with JWT authentication.

    Args:
        env_uuid: UUID of the hub/environment
        host: API host URL

    Returns:
        httpx.Response object
    """
    auth_headers = get_auth_headers(host)

    if not auth_headers:
        raise AuthenticationError(LOGIN_REQUIRED_MESSAGE)

    params = {"envUuid": env_uuid}

    with httpx.Client() as client:
        return client.get(
            f"{host}/api/v2/dubhub/environment/status",
            params=params,
            headers=auth_headers,
            timeout=60.0,
        )


def hub_dubs_api_sync(
    env_uuid: str,
    host: str,
    method: str = "GET",
    dub_uuid: str = None,
):
    """
    Manage hub/environment dubs using v2 API with JWT authentication.

    Args:
        env_uuid: UUID of the hub/environment
        host: API host URL
        method: HTTP method ("GET", "POST", or "DELETE")
        dub_uuid: UUID of the dub (for POST/DELETE operations)

    Returns:
        httpx.Response object
    """
    auth_headers = get_auth_headers(host)

    if not auth_headers:
        raise AuthenticationError(LOGIN_REQUIRED_MESSAGE)

    data = {"envUuid": env_uuid}

    if dub_uuid and method.upper() in ["POST", "DELETE"]:
        data["dubUuid"] = dub_uuid

    with httpx.Client() as client:
        if method.upper() == "POST":
            return client.post(
                f"{host}/api/v2/dubhub/environment/dubs",
                json=data,
                headers=auth_headers,
                timeout=60.0,
            )
        elif method.upper() == "DELETE":
            return client.delete(
                f"{host}/api/v2/dubhub/environment/dubs",
                json=data,
                headers=auth_headers,
                timeout=60.0,
            )
        else:
            return client.get(
                f"{host}/api/v2/dubhub/environment/dubs",
                params=data,
                headers=auth_headers,
                timeout=60.0,
            )


def analyze_pr_api_sync(host: str, org_token: str, webhook_payload: dict):
    """
    Call the baseguard PR comment API (no authentication required).

    This endpoint is designed to be called from GitHub webhooks and
    does not require JWT authentication.

    Args:
        host: API host URL
        org_token: Organization token
        webhook_payload: The GitHub webhook payload (full PR event data)

    Returns:
        httpx.Response object
    """
    payload = {
        "orgToken": org_token,
        "webhookPayload": webhook_payload,
    }
    with httpx.Client() as client:
        return client.post(
            f"{host}/api/baseguard/pr_comment",
            json=payload,
            timeout=60.0,
        )
