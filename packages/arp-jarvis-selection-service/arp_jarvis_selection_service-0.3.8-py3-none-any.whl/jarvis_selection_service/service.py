from __future__ import annotations

from arp_llm.types import ChatModel
from arp_standard_model import (
    CandidateSet,
    Health,
    SelectionGenerateCandidateSetRequest,
    SelectionHealthRequest,
    SelectionVersionRequest,
    Status,
    VersionInfo,
)
from arp_standard_server.selection import BaseSelectionServer

from . import __version__
from .node_registry_client import NodeRegistryGatewayClient
from .strategy import SelectionStrategy
from .utils import now


class SelectionService(BaseSelectionServer):
    """Selection surface; implement your candidate generation here."""

    # Core method - API surface and main extension points
    def __init__(
        self,
        *,
        service_name: str = "arp-jarvis-selection-service",
        service_version: str = __version__,
        node_registry: NodeRegistryGatewayClient | None = None,
        llm: ChatModel | None = None,
        strategy: str = "llm",
        top_k_default: int | None = None,
        planner_node_type_id: str | None = None,
    ) -> None:
        """
        Not part of ARP spec; required to construct the selection service.

        Args:
          - service_name: Name exposed by /v1/version.
          - service_version: Version exposed by /v1/version.
          - node_registry: Optional wrapper for Node Registry calls.

        Potential modifications:
          - Inject your selection engine or model.
          - Add caching or persistence for candidate sets.
        """
        self._service_name = service_name
        self._service_version = service_version
        self._selection = SelectionStrategy(
            node_registry=node_registry,
            llm=llm,
            strategy=strategy,
            top_k_default=top_k_default,
            planner_node_type_id=planner_node_type_id,
        )

    # Core methods - Selection API implementations
    async def health(self, request: SelectionHealthRequest) -> Health:
        """
        Mandatory: Required by the ARP Selection API.

        Args:
          - request: SelectionHealthRequest (unused).
        """
        _ = request
        return Health(status=Status.ok, time=now())

    async def version(self, request: SelectionVersionRequest) -> VersionInfo:
        """
        Mandatory: Required by the ARP Selection API.

        Args:
          - request: SelectionVersionRequest (unused).
        """
        _ = request
        return VersionInfo(
            service_name=self._service_name,
            service_version=self._service_version,
            supported_api_versions=["v1"],
        )

    async def generate_candidate_set(self, request: SelectionGenerateCandidateSetRequest) -> CandidateSet:
        """
        Mandatory: Required by the ARP Selection API.

        Args:
          - request: SelectionGenerateCandidateSetRequest with subtask + constraints.

        Potential modifications:
          - Replace the default candidate list with your own selection logic.
          - Respect constraints and budgets when generating candidates.
        """
        return await self._selection.generate(request.body)
