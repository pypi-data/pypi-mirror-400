import asyncio
import json

from typing import cast

import pytest
from arp_llm.types import ChatModel, Message, Response
from arp_standard_model import (
    CandidateSetRequest,
    Candidates,
    ConstraintEnvelope,
    Extensions,
    NodeKind,
    NodeType,
    SelectionGenerateCandidateSetRequest,
    SubtaskSpec,
)
from arp_llm.providers.dev_mock import DevMockChatFixture, DevMockChatModel
from arp_standard_server import ArpServerError
from jarvis_selection_service.node_registry_client import NodeRegistryGatewayClient
from jarvis_selection_service.service import SelectionService


def test_generate_candidate_set_respects_max_k() -> None:
    atomic = [
        _node_type("jarvis.core.echo", version="0.3.7", kind=NodeKind.atomic, description="Echo"),
        _node_type("jarvis.web.fetch", version="0.3.7", kind=NodeKind.atomic, description="Fetch"),
    ]
    registry = _FakeRegistry(atomic=atomic, composite=[])
    fixtures = [
        DevMockChatFixture(
            text="ok",
            parsed={
                "candidates": [
                    {
                        "node_type_id": "jarvis.core.echo",
                        "version": "0.3.7",
                        "score": 0.9,
                        "rationale": "Best match",
                    },
                    {
                        "node_type_id": "jarvis.web.fetch",
                        "version": "0.3.7",
                        "score": 0.8,
                        "rationale": "Secondary match",
                    },
                ],
                "needs_planner": False,
                "blocked_reason": None,
                "missing_inputs": None,
            },
        )
    ]
    llm = DevMockChatModel(fixtures=fixtures)
    service = SelectionService(
        node_registry=cast(NodeRegistryGatewayClient, registry),
        llm=llm,
        strategy="llm",
    )
    request = SelectionGenerateCandidateSetRequest(
        body=CandidateSetRequest(
            subtask_spec=SubtaskSpec(subtask_id="subtask_1", goal="test"),
            constraints=ConstraintEnvelope(
                candidates=Candidates(max_candidates_per_subtask=1),
            ),
        )
    )

    result = asyncio.run(service.generate_candidate_set(request))

    assert result.candidate_set_id
    assert result.top_k == 1
    assert len(result.candidates) == 1


class _FakeRegistry:
    def __init__(self, *, atomic: list[NodeType], composite: list[NodeType]) -> None:
        self._atomic = atomic
        self._composite = composite

    async def list_node_types(self, *, q=None, kind=None):
        _ = q
        if kind == NodeKind.atomic:
            return self._atomic
        if kind == NodeKind.composite:
            return self._composite
        return []


def _node_type(node_type_id: str, *, version: str, kind: NodeKind, description: str) -> NodeType:
    return NodeType(
        node_type_id=node_type_id,
        version=version,
        kind=kind,
        description=description,
        input_schema={"type": "object", "additionalProperties": True},
        output_schema={"type": "object", "additionalProperties": True},
        extensions=Extensions.model_validate({"jarvis.role": "planner"}) if kind == NodeKind.composite else None,
    )


def test_generate_candidate_set_llm_adds_planner() -> None:
    atomic = [_node_type("jarvis.core.echo", version="0.3.7", kind=NodeKind.atomic, description="Echo")]
    planner = [
        _node_type(
            "jarvis.composite.planner.general",
            version="0.3.7",
            kind=NodeKind.composite,
            description="Planner",
        )
    ]
    registry = _FakeRegistry(atomic=atomic, composite=planner)
    fixtures = [
        DevMockChatFixture(
            text="ok",
            parsed={
                "candidates": [
                    {
                        "node_type_id": "jarvis.core.echo",
                        "version": "0.3.7",
                        "score": 0.9,
                        "rationale": "Best match",
                    }
                ],
                "needs_planner": True,
                "blocked_reason": None,
                "missing_inputs": None,
            },
        )
    ]
    llm = DevMockChatModel(fixtures=fixtures)
    service = SelectionService(
        node_registry=cast(NodeRegistryGatewayClient, registry),
        llm=llm,
        strategy="llm",
        top_k_default=2,
    )
    request = SelectionGenerateCandidateSetRequest(
        body=CandidateSetRequest(
            subtask_spec=SubtaskSpec(subtask_id="subtask_1", goal="do something"),
        )
    )
    result = asyncio.run(service.generate_candidate_set(request))

    assert len(result.candidates) == 1
    assert result.candidates[0].node_type_ref.node_type_id == "jarvis.composite.planner.general"


class _CaptureChatModel(ChatModel):
    def __init__(self) -> None:
        self.messages: list[Message] = []

    async def response(
        self,
        messages,
        *,
        response_schema=None,
        temperature=None,
        timeout_seconds=None,
        metadata=None,
    ) -> Response:
        _ = response_schema, temperature, timeout_seconds, metadata
        self.messages = list(messages)
        return Response(
            text="ok",
            parsed={
                "candidates": [
                    {
                        "node_type_id": "jarvis.core.echo",
                        "version": "0.10.0",
                        "score": 0.9,
                        "rationale": "Return an existing value from prior steps.",
                    }
                ],
                "needs_planner": False,
                "blocked_reason": None,
                "missing_inputs": None,
            },
            usage=None,
            provider="test",
            model="test",
            request_id=None,
            latency_ms=0,
        )


def test_generate_candidate_set_includes_prior_steps_and_dedupes_versions() -> None:
    atomic = [
        _node_type("jarvis.core.echo", version="0.3.7", kind=NodeKind.atomic, description="Echo (old)"),
        _node_type("jarvis.core.echo", version="0.10.0", kind=NodeKind.atomic, description="Echo (new)"),
        _node_type("jarvis.core.uuid4", version="0.3.7", kind=NodeKind.atomic, description="UUID4"),
    ]
    registry = _FakeRegistry(atomic=atomic, composite=[])
    llm = _CaptureChatModel()
    service = SelectionService(
        node_registry=cast(NodeRegistryGatewayClient, registry),
        llm=llm,
        strategy="llm",
    )
    request = SelectionGenerateCandidateSetRequest(
        body=CandidateSetRequest(
            subtask_spec=SubtaskSpec(
                subtask_id="S2",
                goal="Return the generated UUID",
                extensions=Extensions.model_validate(
                    {
                        "jarvis.root_goal": "Generate a UUID, then return it.",
                        "jarvis.subtask.notes": "Output the UUID from Subtask S1 as the final result.",
                    }
                ),
            ),
            extensions=Extensions.model_validate(
                {
                    "jarvis.prior_steps": [
                        {
                            "subtask_id": "S1",
                            "node_type_ref": {"node_type_id": "jarvis.core.uuid4", "version": "0.3.7"},
                            "outputs": {"uuid4": "1950631f-c549-4cfd-916c-750d4584783b"},
                        }
                    ]
                }
            ),
        )
    )

    result = asyncio.run(service.generate_candidate_set(request))

    payload = json.loads(llm.messages[1].content)
    echo_entries = [entry for entry in payload["available_actions"] if entry["node_type_id"] == "jarvis.core.echo"]
    assert echo_entries == [
        {
            "node_type_id": "jarvis.core.echo",
            "description": "Echo (new)",
            "required_inputs": [],
            "output_keys": [],
            "side_effect_class": "read",
            "egress_policy": None,
        },
    ]
    assert payload["previous_steps"]
    assert payload["root_goal"] == "Generate a UUID, then return it."

    assert result.candidates[0].node_type_ref.node_type_id == "jarvis.core.echo"
    assert result.candidates[0].node_type_ref.version == "0.10.0"
    extensions = result.extensions.model_dump(exclude_none=True) if result.extensions else {}
    assert "jarvis.prior_steps" not in extensions


def test_generate_candidate_set_blocked_reason_raises() -> None:
    atomic = [_node_type("jarvis.core.echo", version="0.3.7", kind=NodeKind.atomic, description="Echo")]
    registry = _FakeRegistry(atomic=atomic, composite=[])
    fixtures = [
        DevMockChatFixture(
            text="blocked",
            parsed={
                "candidates": [],
                "needs_planner": False,
                "blocked_reason": "Missing required input.",
                "missing_inputs": ["echo"],
            },
        )
    ]
    llm = DevMockChatModel(fixtures=fixtures)
    service = SelectionService(
        node_registry=cast(NodeRegistryGatewayClient, registry),
        llm=llm,
        strategy="llm",
    )
    request = SelectionGenerateCandidateSetRequest(
        body=CandidateSetRequest(
            subtask_spec=SubtaskSpec(subtask_id="subtask_1", goal="Return the provided value"),
        )
    )

    with pytest.raises(ArpServerError) as exc_info:
        asyncio.run(service.generate_candidate_set(request))

    assert exc_info.value.code == "selection_blocked"
    assert exc_info.value.status_code == 422
    assert exc_info.value.retryable is False
