from __future__ import annotations

import json
import logging
import re
import uuid
from collections.abc import Iterable
from typing import Any

from arp_llm.errors import LlmError
from arp_llm.types import ChatModel, Message
from arp_standard_model import (
    Candidate,
    CandidateSet,
    CandidateSetRequest,
    Candidates,
    ConstraintEnvelope,
    Extensions,
    NodeKind,
    NodeType,
    NodeTypeRef,
)
from arp_standard_server import ArpServerError

from .llm_assets import SELECTION_RESPONSE_SCHEMA, SELECTION_SYSTEM_PROMPT
from .node_registry_client import NodeRegistryGatewayClient
from .utils import now

logger = logging.getLogger(__name__)


class SelectionStrategy:
    def __init__(
        self,
        *,
        node_registry: NodeRegistryGatewayClient | None,
        llm: ChatModel | None,
        strategy: str,
        top_k_default: int | None,
        planner_node_type_id: str | None,
    ) -> None:
        self._node_registry = node_registry
        self._llm = llm
        self._strategy = strategy
        self._top_k_default = top_k_default
        self._planner_node_type_id = planner_node_type_id

    async def generate(self, request: CandidateSetRequest) -> CandidateSet:
        logger.info(
            "Selection requested (subtask_id=%s, goal_len=%s, constraints=%s, strategy=%s)",
            request.subtask_spec.subtask_id,
            len(request.subtask_spec.goal),
            request.constraints is not None,
            self._strategy,
        )
        # Resolve request-level constraints before building candidates.
        top_k = _resolve_top_k(request.constraints, default=self._top_k_default)
        # Fetch inventory from Node Registry and split atomic vs planner-capable composites.
        atomic_types, planner_types = await self._inventory()
        # Apply hard allow/deny filters to the candidate inventory.
        atomic_types = _filter_node_types(atomic_types, request.constraints)
        planner_types = _filter_node_types(planner_types, request.constraints)
        # Only keep the latest version of each NodeType ID to keep selection bounded and predictable.
        atomic_types = _latest_by_node_type_id(atomic_types)
        planner_types = _latest_by_node_type_id(planner_types)
        logger.info(
            "Selection inventory resolved (atomic=%s, planners=%s, top_k=%s)",
            len(atomic_types),
            len(planner_types),
            top_k,
        )

        if self._strategy != "llm":
            logger.warning("Selection strategy unsupported (strategy=%s)", self._strategy)
            raise ArpServerError(
                code="selection_strategy_unsupported",
                message="Only the 'llm' selection strategy is supported",
                status_code=400,
                details={"strategy": self._strategy},
            )
        if self._llm is None:
            logger.warning("Selection LLM missing")
            raise ArpServerError(
                code="selection_llm_missing",
                message="Selection requires an LLM, but no model is configured",
                status_code=503,
            )
        # Delegate to the LLM-based selection path; surface a structured error on failure.
        try:
            return await self._generate_with_llm(
                request=request,
                atomic_types=atomic_types,
                planner_types=planner_types,
                top_k=top_k,
            )
        except ArpServerError:
            raise
        except LlmError as exc:
            logger.warning("Selection LLM error (code=%s, message=%s)", exc.code, exc.message)
            raise ArpServerError(
                code=f"selection_llm_{exc.code}",
                message=exc.message,
                status_code=exc.status_code or 502,
                details=exc.details,
                retryable=exc.retryable,
            ) from exc
        except Exception as exc:
            logger.exception("Selection LLM failed")
            raise ArpServerError(
                code="selection_llm_failed",
                message="Selection LLM request failed",
                status_code=502,
                details={"error": str(exc)},
            ) from exc

    async def _inventory(self) -> tuple[list[NodeType], list[NodeType]]:
        atomic_types: list[NodeType] = []
        planner_types: list[NodeType] = []
        if self._node_registry is None:
            logger.warning("Selection inventory missing Node Registry")
            return atomic_types, planner_types
        atomic_types = await self._node_registry.list_node_types(kind=NodeKind.atomic)
        composite_types = await self._node_registry.list_node_types(kind=NodeKind.composite)
        planner_types = [node_type for node_type in composite_types if _is_planner(node_type, self._planner_node_type_id)]
        return atomic_types, planner_types

    async def _generate_with_llm(
        self,
        *,
        request: CandidateSetRequest,
        atomic_types: list[NodeType],
        planner_types: list[NodeType],
        top_k: int | None,
    ) -> CandidateSet:
        # Validate LLM exist
        if (llm := self._llm) is None:
            raise ArpServerError(
                code="selection_llm_missing",
                message="Selection requires an LLM, but no model is configured",
                status_code=503,
            )

        # Build candidate menu and user payload for the model.
        menu_types = _latest_node_types_by_id(atomic_types)
        menu = [_node_menu_entry(node_type) for node_type in menu_types]
        subtask_extensions = _extensions_payload(request.subtask_spec.extensions)
        request_extensions = _extensions_payload(request.extensions)
        root_goal = subtask_extensions.get("jarvis.root_goal")
        if not isinstance(root_goal, str):
            root_goal = None
        notes = subtask_extensions.get("jarvis.subtask.notes")
        if not isinstance(notes, str):
            notes = None
        prior_steps_raw = request_extensions.get("jarvis.prior_steps")
        previous_steps = _normalize_previous_steps(prior_steps_raw)
        user_payload: dict[str, Any] = {
            "root_goal": root_goal,
            "subtask": {"goal": request.subtask_spec.goal, "notes": notes},
            "previous_steps": previous_steps,
            "available_actions": menu,
            "constraints": _constraints_payload(request.constraints),
            "limits": {"top_k": top_k},
        }
        messages = [
            Message.system(SELECTION_SYSTEM_PROMPT),
            Message.user(json.dumps(user_payload, sort_keys=True)),
        ]

        schema_issues = _find_openai_strict_schema_issues(SELECTION_RESPONSE_SCHEMA, limit=5)
        if schema_issues:
            logger.warning("Selection response schema is not OpenAI-strict (issues=%s)", schema_issues)
        logger.info(
            "Selection LLM request (subtask_id=%s, goal_len=%s, candidates=%s, top_k=%s, has_prior_steps=%s, schema_issues=%s)",
            request.subtask_spec.subtask_id,
            len(request.subtask_spec.goal),
            len(menu),
            top_k,
            bool(previous_steps),
            len(schema_issues),
        )

        # Request a structured response so we can validate candidates deterministically.
        response = await llm.response(
            messages,
            response_schema=SELECTION_RESPONSE_SCHEMA,
            metadata={"subtask_id": request.subtask_spec.subtask_id},
        )
        if response.parsed is None:
            raise LlmError(code="parse_error", message="LLM response missing parsed output")
        parsed = response.parsed

        blocked_reason = parsed.get("blocked_reason")
        blocked_reason_value = blocked_reason.strip() if isinstance(blocked_reason, str) and blocked_reason.strip() else None
        missing_inputs_raw = parsed.get("missing_inputs")
        missing_inputs: list[str] | None = None
        if isinstance(missing_inputs_raw, list):
            missing_inputs = [item for item in missing_inputs_raw if isinstance(item, str) and item.strip()]
        elif missing_inputs_raw is None:
            missing_inputs = None

        if blocked_reason_value is not None:
            logger.info(
                "Selection blocked (subtask_id=%s, missing_inputs=%s, reason=%s)",
                request.subtask_spec.subtask_id,
                missing_inputs,
                blocked_reason_value,
            )
            raise ArpServerError(
                code="selection_blocked",
                message=blocked_reason_value,
                status_code=422,
                details={
                    "subtask_id": request.subtask_spec.subtask_id,
                    "missing_inputs": missing_inputs,
                    "root_goal": root_goal,
                    "llm_provider": response.provider,
                    "llm_model": response.model,
                },
                retryable=False,
            )

        needs_planner = bool(parsed.get("needs_planner"))
        if needs_planner:
            if not planner_types:
                raise ArpServerError(
                    code="selection_planner_missing",
                    message="Selection requires a planner, but no planner node types are available",
                    status_code=422,
                    details={"subtask_id": request.subtask_spec.subtask_id},
                )
            candidates = _planner_only_candidates(planner_types)
        else:
            # Resolve the model's candidates back to known NodeTypes.
            candidates = _parse_llm_candidates(parsed.get("candidates"), atomic_types)
            candidates = _bound_candidates(candidates, top_k)
        logger.info(
            "Selection LLM resolved (subtask_id=%s, candidates=%s, needs_planner=%s)",
            request.subtask_spec.subtask_id,
            len(candidates),
            needs_planner,
        )

        if not candidates:
            raise ArpServerError(
                code="selection_no_candidates",
                message="Selection produced no candidates for the subtask",
                status_code=422,
                details={
                    "subtask_id": request.subtask_spec.subtask_id,
                    "missing_inputs": missing_inputs,
                },
            )

        # Attach non-sensitive strategy metadata for observability.
        extensions = _extensions_payload(request.extensions)
        extensions.pop("jarvis.prior_steps", None)
        extensions.update(
            {
                "jarvis.selection.strategy": "llm",
                "jarvis.selection.needs_planner": needs_planner,
                "jarvis.selection.planner_node_type_ref": candidates[0].node_type_ref.model_dump(exclude_none=True)
                if needs_planner and candidates
                else None,
                "jarvis.llm.provider": response.provider,
                "jarvis.llm.model": response.model,
                "jarvis.llm.latency_ms": response.latency_ms,
            }
        )
        extensions_payload = Extensions.model_validate(extensions)

        return CandidateSet(
            candidate_set_id=str(uuid.uuid4()),
            subtask_id=request.subtask_spec.subtask_id,
            candidates=candidates,
            top_k=top_k,
            generated_at=now(),
            constraints=request.constraints,
            extensions=extensions_payload,
        )


def _resolve_top_k(constraints: ConstraintEnvelope | None, *, default: int | None) -> int | None:
    if constraints and isinstance(constraints.candidates, Candidates):
        if constraints.candidates.max_candidates_per_subtask is not None:
            return constraints.candidates.max_candidates_per_subtask
    return default


def _filter_node_types(node_types: Iterable[NodeType], constraints: ConstraintEnvelope | None) -> list[NodeType]:
    allowed: set[str] | None = None
    denied: set[str] | None = None
    max_side_effect_rank: int | None = None
    if constraints and isinstance(constraints.candidates, Candidates):
        if constraints.candidates.allowed_node_type_ids:
            allowed = set(constraints.candidates.allowed_node_type_ids)
        if constraints.candidates.denied_node_type_ids:
            denied = set(constraints.candidates.denied_node_type_ids)
    if constraints and constraints.gates and constraints.gates.side_effect_class is not None:
        max_side_effect_rank = _side_effect_rank(_side_effect_str(constraints.gates.side_effect_class))
    filtered: list[NodeType] = []
    for node_type in node_types:
        if allowed is not None and node_type.node_type_id not in allowed:
            continue
        if denied is not None and node_type.node_type_id in denied:
            continue
        if max_side_effect_rank is not None:
            node_rank = _side_effect_rank(_node_type_side_effect(node_type))
            if node_rank is not None and node_rank > max_side_effect_rank:
                continue
        filtered.append(node_type)
    return filtered


def _is_planner(node_type: NodeType, planner_node_type_id: str | None) -> bool:
    if node_type.kind != NodeKind.composite:
        return False
    if planner_node_type_id and node_type.node_type_id == planner_node_type_id:
        return True
    if node_type.node_type_id.startswith("jarvis.composite.planner"):
        return True
    extensions = _extensions_dict(node_type)
    return extensions.get("jarvis.role") == "planner"


def _extensions_dict(node_type: NodeType) -> dict[str, Any]:
    if node_type.extensions is None:
        return {}
    if hasattr(node_type.extensions, "model_dump"):
        return node_type.extensions.model_dump(exclude_none=True)
    return dict(node_type.extensions)


def _extensions_payload(extensions: Extensions | None) -> dict[str, Any]:
    if extensions is None:
        return {}
    if hasattr(extensions, "model_dump"):
        return extensions.model_dump(exclude_none=True)
    return dict(extensions)


def _normalize_previous_steps(raw: Any) -> list[dict[str, Any]]:
    if not isinstance(raw, list):
        return []
    steps: list[dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue

        action = item.get("action")
        if not isinstance(action, str):
            node_type_ref = item.get("node_type_ref")
            if isinstance(node_type_ref, dict) and isinstance(node_type_ref.get("node_type_id"), str):
                action = node_type_ref["node_type_id"]
            else:
                action = None

        outputs = item.get("outputs") if isinstance(item.get("outputs"), dict) else {}

        normalized = {
            "action": action,
            "outputs": outputs,
        }
        steps.append(normalized)
    return steps


def _node_menu_entry(node_type: NodeType) -> dict[str, Any]:
    required_inputs = _schema_required_inputs(node_type.input_schema)
    output_keys = _schema_output_keys(node_type.output_schema)
    entry: dict[str, Any] = {
        "node_type_id": node_type.node_type_id,
        "description": node_type.description or "",
        "required_inputs": required_inputs,
        "output_keys": output_keys,
        "side_effect_class": _node_type_side_effect(node_type),
        "egress_policy": _node_type_egress_policy(node_type),
    }
    return entry


def _parse_llm_candidates(raw: Any, atomic_types: list[NodeType]) -> list[Candidate]:
    if not isinstance(raw, list):
        return []
    by_key = {(node_type.node_type_id, node_type.version): node_type for node_type in atomic_types}
    by_id = _group_by_id(atomic_types)
    seen: set[tuple[str, str]] = set()
    candidates: list[Candidate] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        node_type_id = item.get("node_type_id")
        version = item.get("version")
        if not isinstance(node_type_id, str):
            continue
        if not isinstance(version, str):
            version = _latest_version(by_id.get(node_type_id, []))
        if not isinstance(version, str):
            continue
        key = (node_type_id, version)
        if key not in by_key or key in seen:
            continue
        seen.add(key)
        score = item.get("score")
        if not isinstance(score, (int, float)):
            score = None
        rationale = item.get("rationale")
        if not isinstance(rationale, str):
            rationale = None
        candidates.append(
            Candidate(
                node_type_ref=NodeTypeRef(node_type_id=node_type_id, version=version),
                score=score,
                rationale=rationale,
            )
        )
    return candidates


def _group_by_id(node_types: Iterable[NodeType]) -> dict[str, list[NodeType]]:
    grouped: dict[str, list[NodeType]] = {}
    for node_type in node_types:
        grouped.setdefault(node_type.node_type_id, []).append(node_type)
    return grouped


def _latest_version(node_types: list[NodeType]) -> str | None:
    if not node_types:
        return None
    return max((node_type.version for node_type in node_types), key=_version_sort_key)


def _latest_node_types_by_id(node_types: list[NodeType]) -> list[NodeType]:
    by_id = _group_by_id(node_types)
    latest: list[NodeType] = []
    for node_type_id, versions in by_id.items():
        version = _latest_version(versions)
        if version is None:
            continue
        for node_type in versions:
            if node_type.version == version:
                latest.append(node_type)
                break
    return sorted(latest, key=lambda node_type: node_type.node_type_id)


def _prefer_planner_candidate(
    *,
    candidates: list[Candidate],
    planner_types: list[NodeType],
    top_k: int | None,
) -> list[Candidate]:
    if not planner_types:
        return candidates
    planner = sorted(planner_types, key=lambda node_type: node_type.node_type_id)[0]
    planner_ref = NodeTypeRef(node_type_id=planner.node_type_id, version=planner.version)
    planner_candidate = next((candidate for candidate in candidates if candidate.node_type_ref == planner_ref), None)
    if planner_candidate is None:
        planner_candidate = Candidate(node_type_ref=planner_ref, score=0.1, rationale="Planner required.")

    ordered = [planner_candidate] + [candidate for candidate in candidates if candidate.node_type_ref != planner_ref]
    return _bound_candidates(ordered, top_k)


def _planner_only_candidates(planner_types: list[NodeType]) -> list[Candidate]:
    planner = sorted(planner_types, key=lambda node_type: node_type.node_type_id)[0]
    planner_ref = NodeTypeRef(node_type_id=planner.node_type_id, version=planner.version)
    return [Candidate(node_type_ref=planner_ref, score=0.1, rationale="Planner required.")]


def _constraints_payload(constraints: ConstraintEnvelope | None) -> dict[str, Any]:
    allowed = None
    denied = None
    if constraints and isinstance(constraints.candidates, Candidates):
        allowed = constraints.candidates.allowed_node_type_ids or None
        denied = constraints.candidates.denied_node_type_ids or None

    max_side_effect_class = None
    require_approval = None
    if constraints and constraints.gates:
        if constraints.gates.side_effect_class is not None:
            max_side_effect_class = _side_effect_str(constraints.gates.side_effect_class)
        require_approval = constraints.gates.require_approval

    return {
        "allowed_node_type_ids": allowed,
        "denied_node_type_ids": denied,
        "max_side_effect_class": max_side_effect_class,
        "require_approval": require_approval,
    }


def _node_type_side_effect(node_type: NodeType) -> str:
    extensions = _extensions_dict(node_type)
    side_effect = extensions.get("jarvis.side_effect")
    if isinstance(side_effect, str) and side_effect in ("read", "write", "irreversible"):
        return side_effect
    return "read"


def _node_type_egress_policy(node_type: NodeType) -> str | None:
    extensions = _extensions_dict(node_type)
    egress_policy = extensions.get("jarvis.egress_policy")
    return egress_policy if isinstance(egress_policy, str) else None


def _schema_required_inputs(schema: Any) -> list[str]:
    if not isinstance(schema, dict):
        return []
    props = schema.get("properties")
    if not isinstance(props, dict):
        return []
    required = schema.get("required")
    required_set = {key for key in required if isinstance(key, str)} if isinstance(required, list) else set(props.keys())

    required_inputs: list[str] = []
    for key in required_set:
        prop_schema = props.get(key)
        if not _schema_allows_null(prop_schema):
            required_inputs.append(key)
    return sorted(required_inputs)


def _schema_output_keys(schema: Any) -> list[str]:
    if not isinstance(schema, dict):
        return []
    props = schema.get("properties")
    if not isinstance(props, dict):
        return []
    return sorted([key for key in props.keys() if isinstance(key, str)])


def _schema_allows_null(schema: Any) -> bool:
    if not isinstance(schema, dict):
        return False
    schema_type = schema.get("type")
    if schema_type == "null":
        return True
    if isinstance(schema_type, list) and "null" in schema_type:
        return True
    for key in ("anyOf", "oneOf"):
        branches = schema.get(key)
        if isinstance(branches, list) and any(_schema_allows_null(branch) for branch in branches):
            return True
    return False


def _side_effect_str(value: Any) -> str | None:
    if hasattr(value, "value") and isinstance(value.value, str):
        return value.value
    if isinstance(value, str):
        return value
    return None


def _side_effect_rank(value: str | None) -> int | None:
    if value is None:
        return None
    return {"read": 0, "write": 1, "irreversible": 2}.get(value)


def _bound_candidates(candidates: list[Candidate], top_k: int | None) -> list[Candidate]:
    if isinstance(top_k, int) and top_k >= 1:
        return candidates[:top_k]
    return candidates


def _find_openai_strict_schema_issues(schema: dict[str, Any], *, limit: int) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []

    def visit(value: Any, path: list[Any]) -> None:
        if len(issues) >= limit:
            return
        if isinstance(value, dict):
            schema_type = value.get("type")
            is_object = schema_type == "object" or (isinstance(schema_type, list) and "object" in schema_type)
            if is_object:
                ap = value.get("additionalProperties", None)
                if ap is not False:
                    issues.append(
                        {
                            "path": _format_schema_path(path),
                            "issue": "additionalProperties_must_be_false",
                            "value": ap,
                        }
                    )
                    if len(issues) >= limit:
                        return

                props = value.get("properties")
                if props is None or not isinstance(props, dict):
                    issues.append(
                        {
                            "path": _format_schema_path(path + ["properties"]),
                            "issue": "properties_must_be_object",
                            "value": None if props is None else type(props).__name__,
                        }
                    )
                    if len(issues) >= limit:
                        return
                    props = {}

                req = value.get("required")
                if req is None or not isinstance(req, list):
                    issues.append(
                        {
                            "path": _format_schema_path(path + ["required"]),
                            "issue": "required_must_be_array",
                            "value": None if req is None else type(req).__name__,
                        }
                    )
                    if len(issues) >= limit:
                        return
                    req = []

                missing = [key for key in props.keys() if key not in req]
                if missing:
                    issues.append(
                        {
                            "path": _format_schema_path(path + ["required"]),
                            "issue": "required_must_include_all_properties",
                            "value": missing,
                        }
                    )
                    if len(issues) >= limit:
                        return

            for key, item in value.items():
                if key in ("$defs", "definitions") and isinstance(item, dict):
                    for def_name, def_schema in item.items():
                        visit(def_schema, path + [key, def_name])
                    continue
                if key in ("anyOf", "oneOf", "allOf") and isinstance(item, list):
                    for idx, branch in enumerate(item):
                        visit(branch, path + [key, idx])
                    continue
                if key == "properties" and isinstance(item, dict):
                    for prop_name, prop_schema in item.items():
                        visit(prop_schema, path + [key, prop_name])
                    continue
                if key == "items":
                    visit(item, path + [key])
                    continue
        elif isinstance(value, list):
            for idx, item in enumerate(value):
                visit(item, path + [idx])

    visit(schema, [])
    return issues


def _format_schema_path(path: list[Any]) -> str:
    if not path:
        return "$"
    parts: list[str] = ["$"]
    for item in path:
        if isinstance(item, int):
            parts.append(f"[{item}]")
        else:
            parts.append(f".{item}")
    return "".join(parts)


def _latest_by_node_type_id(node_types: Iterable[NodeType]) -> list[NodeType]:
    latest: dict[str, NodeType] = {}
    for node_type in node_types:
        current = latest.get(node_type.node_type_id)
        if current is None or _version_sort_key(node_type.version) > _version_sort_key(current.version):
            latest[node_type.node_type_id] = node_type
    return [latest[node_type_id] for node_type_id in sorted(latest)]


_SEMVER_RE = re.compile(
    r"^v?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-([0-9A-Za-z.-]+))?"
    r"(?:\+[0-9A-Za-z.-]+)?$"
)


def _semver_key(version: str) -> tuple[int, int, int, int, tuple[tuple[int, Any], ...]] | None:
    match = _SEMVER_RE.match(version)
    if not match:
        return None
    major, minor, patch = (int(match.group(i)) for i in range(1, 4))
    if (prerelease := match.group(4)) is None:
        return (major, minor, patch, 1, ())
    parts: list[tuple[int, Any]] = []
    for part in prerelease.split("."):
        if part.isdigit():
            parts.append((0, int(part)))
        else:
            parts.append((1, part))
    return (major, minor, patch, 0, tuple(parts))


def _version_sort_key(version: str) -> tuple[int, Any]:
    if (key := _semver_key(version)) is not None:
        return (1, key)
    return (0, version)
