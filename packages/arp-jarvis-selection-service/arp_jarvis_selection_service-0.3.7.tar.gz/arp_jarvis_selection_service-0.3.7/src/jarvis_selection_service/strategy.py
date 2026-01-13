from __future__ import annotations

import json
import logging
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
        menu = [_node_menu_entry(node_type) for node_type in atomic_types]
        user_payload = {
            "subtask": request.subtask_spec.goal,
            "top_k": top_k,
            "candidates": menu,
        }
        messages = [
            Message.system(SELECTION_SYSTEM_PROMPT),
            Message.user(json.dumps(user_payload, sort_keys=True)),
        ]

        # Request a structured response so we can validate candidates deterministically.
        response = await llm.response(
            messages,
            response_schema=SELECTION_RESPONSE_SCHEMA,
            metadata={"subtask_id": request.subtask_spec.subtask_id},
        )
        if response.parsed is None:
            raise LlmError(code="parse_error", message="LLM response missing parsed output")
        parsed = response.parsed
        
        # Resolve the model's candidates back to known NodeTypes.
        candidates = _parse_llm_candidates(parsed.get("candidates"), atomic_types)
        needs_planner = bool(parsed.get("needs_planner"))

        # Apply top-k bounds and add planner fallback if requested.
        candidates = _bound_candidates(candidates, top_k)
        if needs_planner and planner_types:
            candidates = _append_planner_candidate(
                candidates=candidates,
                planner_types=planner_types,
                top_k=top_k,
            )
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
                details={"subtask_id": request.subtask_spec.subtask_id},
            )

        # Attach non-sensitive strategy metadata for observability.
        extensions = dict(request.extensions or {})
        extensions.update(
            {
                "jarvis.selection.strategy": "llm",
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
    if constraints and isinstance(constraints.candidates, Candidates):
        if constraints.candidates.allowed_node_type_ids:
            allowed = set(constraints.candidates.allowed_node_type_ids)
        if constraints.candidates.denied_node_type_ids:
            denied = set(constraints.candidates.denied_node_type_ids)
    filtered: list[NodeType] = []
    for node_type in node_types:
        if allowed is not None and node_type.node_type_id not in allowed:
            continue
        if denied is not None and node_type.node_type_id in denied:
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


def _node_menu_entry(node_type: NodeType) -> dict[str, Any]:
    extensions = _extensions_dict(node_type)
    entry: dict[str, Any] = {
        "node_type_id": node_type.node_type_id,
        "version": node_type.version,
        "description": node_type.description or "",
    }
    if (side_effect := extensions.get("jarvis.side_effect")) is not None:
        entry["side_effect"] = side_effect
    if (egress_policy := extensions.get("jarvis.egress_policy")) is not None:
        entry["egress_policy"] = egress_policy
    if (tags := extensions.get("jarvis.tags")) is not None:
        entry["tags"] = tags
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
    versions = sorted(node_type.version for node_type in node_types)
    return versions[-1]


def _append_planner_candidate(
    *,
    candidates: list[Candidate],
    planner_types: list[NodeType],
    top_k: int | None,
) -> list[Candidate]:
    if not planner_types:
        return candidates
    planner = sorted(planner_types, key=lambda node_type: (node_type.node_type_id, node_type.version))[0]
    planner_ref = NodeTypeRef(node_type_id=planner.node_type_id, version=planner.version)
    if any(candidate.node_type_ref == planner_ref for candidate in candidates):
        return candidates
    if top_k == 1 and candidates:
        return candidates
    if top_k is not None and len(candidates) >= top_k:
        return candidates
    return candidates + [Candidate(node_type_ref=planner_ref, score=0.1, rationale="Planner fallback.")]


def _bound_candidates(candidates: list[Candidate], top_k: int | None) -> list[Candidate]:
    if isinstance(top_k, int) and top_k >= 1:
        return candidates[:top_k]
    return candidates
