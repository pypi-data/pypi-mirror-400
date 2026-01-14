from __future__ import annotations

from typing import Any, Dict

from atlas_asset_http_client_python import AtlasCommandHttpClient


async def run(
    client: AtlasCommandHttpClient,
    envelope: Any,
    data: Dict[str, Any],
) -> Any:
    """Update an existing task."""
    task_id = data.get("task_id")
    if not task_id:
        raise ValueError("update_task requires 'task_id'")
    payload: Dict[str, Any] = {}
    for key in ("status", "entity_id", "components", "extra"):
        if key in data:
            payload[key] = data.get(key)
    if not payload:
        raise ValueError("update_task requires at least one of: status, entity_id, components, extra")
    return await client.update_task(task_id=str(task_id), **payload)
