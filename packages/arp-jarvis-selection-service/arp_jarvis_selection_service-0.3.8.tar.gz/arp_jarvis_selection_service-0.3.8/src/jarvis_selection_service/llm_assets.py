from __future__ import annotations

from typing import Any

SELECTION_SYSTEM_PROMPT = (
    "You are selecting the next single action to run for a subtask. "
    "You will be given a JSON input with fields: root_goal, subtask, previous_steps, available_actions, constraints, and limits. "
    "Each available action includes: node_type_id, description, required_inputs, output_keys, side_effect_class, and egress_policy. "
    "Your job: choose actions that can complete the subtask in ONE execution. "
    "Use previous_steps outputs when helpful (prefer reusing existing values instead of regenerating or refetching). "
    "Rules: "
    "- Only choose from available_actions; do not invent new actions. "
    "- If the subtask requires multiple executions (loops over a list, combining multiple results, sequencing, or assembling a final output), "
    "set needs_planner=true AND return an empty candidates array. This will setup the subtask to be further decomposed. "
    "- If no single available action can complete the subtask in one execution under the given constraints and the task cannot be reasonably further decomposed, "
    "set blocked_reason to a short explanation, set missing_inputs when applicable, set needs_planner=false, and return an empty candidates array. "
    "- Otherwise set needs_planner=false and return up to limits.top_k candidates (best first). "
    "- Set candidate.version to null to use the latest version automatically. "
    "Return only JSON that matches the response schema."
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
                    "version": {"type": ["string", "null"]},
                    "score": {"type": ["number", "null"]},
                    "rationale": {"type": ["string", "null"]},
                },
                "required": ["node_type_id", "version", "score", "rationale"],
            },
        },
        "needs_planner": {"type": "boolean"},
        "blocked_reason": {"type": ["string", "null"]},
        "missing_inputs": {
            "type": ["array", "null"],
            "items": {"type": "string"},
        },
    },
    "required": ["candidates", "needs_planner", "blocked_reason", "missing_inputs"],
}
