from __future__ import annotations

import logging
import os

from arp_llm.settings import load_chat_model_from_env

from .node_registry_client import NodeRegistryGatewayClient
from .service import SelectionService
from .utils import auth_settings_from_env_or_dev_insecure

logger = logging.getLogger(__name__)


def create_app():
    node_registry_url = (
        os.environ.get("JARVIS_NODE_REGISTRY_URL")
        or os.environ.get("ARP_NODE_REGISTRY_URL")
        or ""
    ).strip()
    selection_strategy = (os.environ.get("JARVIS_SELECTION_STRATEGY") or "llm").strip().lower()
    top_k_raw = (os.environ.get("JARVIS_SELECTION_TOP_K_DEFAULT") or "").strip()
    planner_node_type_id = (os.environ.get("JARVIS_SELECTION_PLANNER_NODE_TYPE_ID") or "").strip() or None
    top_k_default = None
    if top_k_raw:
        try:
            top_k_default = int(top_k_raw)
        except ValueError:
            logger.warning("Invalid JARVIS_SELECTION_TOP_K_DEFAULT: %s", top_k_raw)
    logger.info(
        "Selection config (strategy=%s, top_k_default=%s, planner_node_type_id=%s, node_registry=%s)",
        selection_strategy,
        top_k_default,
        planner_node_type_id,
        bool(node_registry_url),
    )

    node_registry = None
    if node_registry_url:
        node_registry = NodeRegistryGatewayClient(
            base_url=node_registry_url,
        )
    llm = None
    if selection_strategy == "llm":
        try:
            llm = load_chat_model_from_env()
        except Exception as exc:
            logger.warning("Failed to load LLM profile; selection will error until configured. %s", exc)

    auth_settings = auth_settings_from_env_or_dev_insecure()
    logger.info(
        "Selection auth settings (mode=%s, issuer=%s)",
        getattr(auth_settings, "mode", None),
        getattr(auth_settings, "issuer", None),
    )
    return SelectionService(
        node_registry=node_registry,
        llm=llm,
        strategy=selection_strategy,
        top_k_default=top_k_default,
        planner_node_type_id=planner_node_type_id,
    ).create_app(
        title="JARVIS Selection Service",
        auth_settings=auth_settings,
    )


app = create_app()
