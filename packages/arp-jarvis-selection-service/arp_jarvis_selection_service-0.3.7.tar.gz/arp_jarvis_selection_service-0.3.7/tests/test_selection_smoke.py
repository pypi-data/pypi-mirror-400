import asyncio

from typing import cast

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

    assert len(result.candidates) == 2
    assert result.candidates[0].node_type_ref.node_type_id == "jarvis.core.echo"
    assert result.candidates[1].node_type_ref.node_type_id == "jarvis.composite.planner.general"
