# JARVIS Composite Executor

First-party OSS reference implementation of the **ARP Composite Executor** service.

This reference implementation uses the ARP SDK packages plus shared helpers:
`arp-standard-server`, `arp-standard-model`, `arp-standard-client`, `arp-llm`, and `arp-auth`.

Composite execution internals (decomposition/mapping/evaluation) are intentionally implementation-defined. JARVIS keeps the protocol surface small so you can plug in your preferred framework while preserving spec-aligned request/response envelopes.

Implements: ARP Standard `spec/v1` Composite Executor API (contract: `ARP_Standard/spec/v1/openapi/composite-executor.openapi.yaml`).

This repo’s default design is LLM-driven:
- **Planner**: decompose a composite NodeRun into bounded subtasks (LLM).
- **Selector**: call Selection Service to get bounded candidate sets per subtask.
- **Binder**: pick one candidate deterministically (v0: first candidate).
- **Arg-gen**: generate concrete `inputs` for the chosen node type (LLM) using Node Registry canonical schemas.

## Requirements

- Python >= 3.11

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

- Composite Executor listens on `http://127.0.0.1:8083` by default.

```bash
python3 -m pip install -e .
python3 -m jarvis_composite_executor
```

> [!TIP]
> Use `bash src/scripts/dev_server.sh --host ... --port ... --reload` for dev convenience.

## Using this repo

To build your own composite executor, fork this repository and replace the composite engine while preserving request/response semantics.

If all you need is to change composite behavior, edit:
- `src/jarvis_composite_executor/engine/driver.py`

Outgoing client wrapper (composite -> coordinator):
- `src/jarvis_composite_executor/clients/run_coordinator.py`

### Default behavior

- `begin_composite_node_run` returns `accepted=true` and starts a background driver.
- Planner (LLM) decomposes the composite goal into bounded subtasks.
- For each subtask:
  - Selection Service returns a bounded candidate set (top-K).
  - CE binds deterministically to the first candidate (v0).
  - CE fetches canonical `input_schema` from Node Registry and runs arg-gen (LLM) to produce `inputs`.
  - CE creates the child NodeRun via Run Coordinator and waits for completion.
- CE reports evaluation and completes the composite (v0: fail-fast if any child fails).

### Extensions

This service participates in several cross-component `extensions` conventions:

When creating child NodeRuns via Run Coordinator (`create_node_runs`), CE sets:
- `NodeRunCreateSpec.candidate_set_id` and `NodeRunCreateSpec.binding_decision` (Selection linkage + chosen candidate)
- `NodeRunCreateSpec.idempotency_key` (optional; enables idempotent child creation)
- `NodeRunCreateSpec.constraints` (propagates constraints downstream)

Run Coordinator persists these values into `NodeRun.extensions` so they are queryable later.

When calling Selection Service (`generate_candidate_set`), CE may attach optional context in `SubtaskSpec.extensions`:
- `jarvis.subtask.notes`
- `jarvis.root_goal`

Full cross-stack list: `https://github.com/AgentRuntimeProtocol/BusinessDocs/blob/main/Business_Docs/JARVIS/Extensions.md`.

### Notes on API surface

- In `spec/v1`, the Composite Executor API is intentionally minimal (begin + health/version).
- More lifecycle surfaces (patch proposals, sub-NodeRun requests, completion reporting) can be layered on as the standard evolves.

## Quick health check

```bash
curl http://127.0.0.1:8083/v1/health
```

## Configuration

CLI flags:
- `--host` (default `127.0.0.1`)
- `--port` (default `8083`)
- `--reload` (dev only)

Env vars (selected):
- `JARVIS_SELECTION_URL` (required)
- `JARVIS_NODE_REGISTRY_URL` (required; canonical NodeType schemas for arg-gen)
- `ARP_LLM_PROFILE` + provider-specific vars (required; planner + arg-gen)
- `JARVIS_COMPOSITE_MAX_STEPS` + `JARVIS_COMPOSITE_MAX_DEPTH` (required defaults for planning bounds)

## Validate conformance (`arp-conformance`)

```bash
python3 -m pip install arp-conformance
arp-conformance check composite-executor --url http://127.0.0.1:8083 --tier smoke
arp-conformance check composite-executor --url http://127.0.0.1:8083 --tier surface
```

## Helper scripts

- `src/scripts/dev_server.sh`: run the server (flags: `--host`, `--port`, `--reload`).
- `src/scripts/send_request.py`: send a begin request from a JSON file.

  ```bash
  python3 src/scripts/send_request.py --request src/scripts/request.json
  ```

## Authentication

Auth is enabled by default (JWT). To disable for local dev, set `ARP_AUTH_PROFILE=dev-insecure`.

To enable local Keycloak defaults, set:
- `ARP_AUTH_PROFILE=dev-secure-keycloak`
- `ARP_AUTH_AUDIENCE=arp-composite-executor`
- `ARP_AUTH_ISSUER=http://localhost:8080/realms/arp-dev`

Outbound service-to-service calls (Selection / Node Registry) should use STS token exchange (no static bearer tokens).
Configure the STS client credentials with:
- `ARP_AUTH_CLIENT_ID`
- `ARP_AUTH_CLIENT_SECRET`
- `ARP_AUTH_TOKEN_ENDPOINT`

## Upgrading

When upgrading to a new ARP Standard SDK release, bump pinned versions in `pyproject.toml` (`arp-standard-*==...`) and re-run conformance.
