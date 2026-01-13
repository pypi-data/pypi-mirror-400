from __future__ import annotations

from typing import Any

SELECTION_SYSTEM_PROMPT = (
    "You are a selector that chooses the best atomic node types for a subtask. "
    "Only choose from the provided candidates. "
    "If no single atomic node is a clear fit or the task is multi-step, set needs_planner=true."
)

SELECTION_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "candidates": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "node_type_id": {"type": "string"},
                    "version": {"type": "string"},
                    "score": {"type": ["number", "null"]},
                    "rationale": {"type": ["string", "null"]},
                },
                "required": ["node_type_id", "version", "score", "rationale"],
            },
        },
        "needs_planner": {"type": "boolean"},
    },
    "required": ["candidates", "needs_planner"],
}
