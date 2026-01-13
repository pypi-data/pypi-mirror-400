# JARVIS Selection Service

First-party OSS reference implementation of the **ARP Selection Service**.

The Selection Service produces bounded candidate sets for mapping subtasks to NodeTypes.
The selection strategy is intentionally implementation-defined; JARVIS uses LLM-assisted ranking by default
(via `arp-llm`) and returns an error if selection cannot be produced.

Implements: ARP Standard `spec/v1` Selection API (contract: `ARP_Standard/spec/v1/openapi/selection.openapi.yaml`).

## Requirements

- Python >= 3.10

## Install

```bash
python3 -m pip install -e .
```

## Local configuration (optional)

For local dev convenience, copy the example env file:

```bash
cp .env.example .env.local
```

`src/scripts/dev_server.sh` auto-loads `.env.local` (or `.env`).

## Run

- Selection Service listens on `http://127.0.0.1:8085` by default.

```bash
python3 -m pip install -e .
python3 -m jarvis_selection_service
```

> [!TIP]
> Use `bash src/scripts/dev_server.sh --host ... --port ... --reload` for dev convenience.

## Using this repo

To build your own selection service, fork this repository and replace the selection strategy while preserving request/response semantics.

If all you need is to change selection strategy, edit:
- `src/jarvis_selection_service/strategy.py`

Outgoing client wrapper (selection -> node registry):
- `src/jarvis_selection_service/node_registry_client.py`

### Default behavior

- Builds inventory from Node Registry (atomic-first).
- Uses `arp-llm` to rank atomic candidates for a subtask.
- Adds the composite planner node type when the LLM indicates the task does not fit a single atomic node.
- Planner NodeTypes are seeded by Node Registry (e.g. `jarvis.composite.planner.general`).
- Applies `constraints.candidates.allowed_node_type_ids` / `denied_node_type_ids` if provided.
- Applies `constraints.candidates.max_candidates_per_subtask` as the top-K bound when provided.
- Returns an error if the LLM is unavailable or no candidates can be produced.

### Extensions

The Selection API surfaces `extensions` in both inputs and outputs. This implementation uses them as follows:

Consumes `NodeType.extensions` from Node Registry inventory:
- `jarvis.role` (planner detection)
- `jarvis.side_effect`, `jarvis.egress_policy`, `jarvis.tags` (enrich the LLM menu)

Writes `CandidateSet.extensions` for observability:
- `jarvis.selection.strategy` (currently `llm`)
- `jarvis.llm.provider`, `jarvis.llm.model`, `jarvis.llm.latency_ms`

Passthrough:
- Any keys provided in `CandidateSetRequest.extensions` are copied into `CandidateSet.extensions` (non-sensitive metadata only).

Reserved (accepted but not required in v0.3.x):
- `SubtaskSpec.extensions.jarvis.subtask.notes`
- `SubtaskSpec.extensions.jarvis.root_goal`

Full cross-stack list: `https://github.com/AgentRuntimeProtocol/BusinessDocs/blob/main/Business_Docs/JARVIS/Extensions.md`.

## Quick health check

```bash
curl http://127.0.0.1:8085/v1/health
```

## Configuration

CLI flags:
- `--host` (default `127.0.0.1`)
- `--port` (default `8085`)
- `--reload` (dev only)

Env vars (selected):

- `JARVIS_NODE_REGISTRY_URL` (required)
- `JARVIS_NODE_REGISTRY_AUDIENCE` (optional; outbound token exchange audience)
- `JARVIS_SELECTION_STRATEGY` (default `llm`; other strategies are not supported yet)
- `JARVIS_SELECTION_TOP_K_DEFAULT` (optional)
- `JARVIS_SELECTION_PLANNER_NODE_TYPE_ID` (optional; planner fallback is auto-detected)

LLM (required when `JARVIS_SELECTION_STRATEGY=llm`):

- `ARP_LLM_PROFILE`, `ARP_LLM_CHAT_MODEL`, `ARP_LLM_API_KEY`, ...
  - See `https://github.com/AgentRuntimeProtocol/BusinessDocs/blob/main/Business_Docs/JARVIS/LLMProvider/HLD.md` and `https://github.com/AgentRuntimeProtocol/BusinessDocs/blob/main/Business_Docs/JARVIS/LLMProvider/LLD.md`.

## Validate conformance (`arp-conformance`)

```bash
python3 -m pip install arp-conformance
arp-conformance check selection --url http://127.0.0.1:8085 --tier smoke
arp-conformance check selection --url http://127.0.0.1:8085 --tier surface
```

## Helper scripts

- `src/scripts/dev_server.sh`: run the server (flags: `--host`, `--port`, `--reload`).
- `src/scripts/send_request.py`: generate a candidate set from a JSON file.

  ```bash
  python3 src/scripts/send_request.py --request src/scripts/request.json
  ```

## Authentication

Auth is enabled by default (JWT). To disable for local dev, set `ARP_AUTH_PROFILE=dev-insecure`.

To enable local Keycloak defaults, set:
- `ARP_AUTH_PROFILE=dev-secure-keycloak`
- `ARP_AUTH_AUDIENCE=arp-selection`
- `ARP_AUTH_ISSUER=http://localhost:8080/realms/arp-dev`

Outbound service-to-service calls (Node Registry / PDP) should use STS token exchange (no static bearer tokens).
Configure the STS client credentials with:

- `ARP_AUTH_CLIENT_ID`
- `ARP_AUTH_CLIENT_SECRET`
- `ARP_AUTH_TOKEN_ENDPOINT`

## Upgrading

When upgrading to a new ARP Standard SDK release, bump pinned versions in `pyproject.toml` (`arp-standard-*==...`) and re-run conformance.
