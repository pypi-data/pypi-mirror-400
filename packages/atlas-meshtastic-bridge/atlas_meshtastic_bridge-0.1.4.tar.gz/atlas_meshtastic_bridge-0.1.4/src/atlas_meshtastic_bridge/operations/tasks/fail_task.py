from __future__ import annotations

from typing import Any, Dict

from atlas_asset_http_client_python import AtlasCommandHttpClient


async def run(
    client: AtlasCommandHttpClient,
    envelope: Any,
    data: Dict[str, Any],
) -> Any:
    """Mark a task as failed with optional details."""
    task_id = data.get("task_id")
    if not task_id:
        raise ValueError("fail_task requires 'task_id'")
    payload: Dict[str, Any] = {}
    if message := data.get("error_message"):
        payload["error_message"] = message
    if details := data.get("error_details"):
        payload["error_details"] = details
    return await client.fail_task(task_id=str(task_id), **payload)
