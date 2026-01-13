# JARVIS Atomic Executor

First-party OSS reference implementation of the ARP `spec/v1` Atomic Executor.

This JARVIS component implements the Atomic Executor API using the SDK packages:
`arp-standard-server`, `arp-standard-model`, and `arp-standard-client`.

Implements: ARP Standard `spec/v1` Atomic Executor API (contract: `ARP_Standard/spec/v1/openapi/atomic-executor.openapi.yaml`).

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

- Atomic Executor listens on `http://127.0.0.1:8082` by default.

```bash
python3 -m pip install -e .
jarvis-atomic-executor
```

> [!TIP]
> Use `bash src/scripts/dev_server.sh --host ... --port ... --reload` for dev convenience.

## Using this repo

This repo is the maintained JARVIS reference for atomic execution. Add or replace handlers while preserving ARP request/response semantics.

This executor auto-loads **installed node packs** via the `jarvis.nodepacks` entry point group (see `arp-jarvis-atomic-nodes`).
If you want to override the default handler registry, pass `handlers=...` when constructing `AtomicExecutor`.

### Default behavior

- Loads handlers from installed node packs (entry points).
- Includes `jarvis.core.echo` from the core pack.
- `execute_atomic_node_run` returns `succeeded` with `outputs={"echo": inputs}` for the echo node.
- Unknown `node_type_id` returns `failed` with an error payload.
- `cancel_atomic_node_run` cancels in-flight handler execution (best-effort).

### Common extensions

- Add more node packs or override the handler registry explicitly.
- Customize cancellation behavior (cooperative cancellation, idempotency, timeouts).
- Configure timeouts/concurrency controls around handler execution.

## Implementation overview

Request flow:
1) Inbound request hits the Atomic Executor (`arp-standard-server`).
2) Auth middleware validates the `Authorization: Bearer <JWT>` header (when enabled).
3) The executor routes by `node_type_ref.node_type_id` and calls the matching handler.
4) The executor returns `AtomicExecuteResult` with outputs and timing metadata.

System-of-record:
- The Atomic Executor does not store run state or emit durable run events.
- The Run Coordinator is responsible for orchestration, durability, and emitting `atomic_executed`.

## Quick health check

```bash
curl http://127.0.0.1:8082/v1/health
```

## Configuration

CLI flags:
- `--host` (default `127.0.0.1`)
- `--port` (default `8082`)
- `--reload` (dev only)

Environment variables:
- Incoming JWT validation is configured via `ARP_AUTH_PROFILE` and `ARP_AUTH_*` overrides (see `.env.example`).
- Optional execution controls:
  - `JARVIS_DEFAULT_TIMEOUT_SECS` (coarse per-request timeout)
  - `JARVIS_MAX_CONCURRENCY` (cap concurrent executions)

## Validate conformance (`arp-conformance`)

```bash
python3 -m pip install arp-conformance
arp-conformance check atomic-executor --url http://127.0.0.1:8082 --tier smoke
arp-conformance check atomic-executor --url http://127.0.0.1:8082 --tier surface
```

## Helper scripts

- `src/scripts/dev_server.sh`: run the server (flags: `--host`, `--port`, `--reload`).
- `src/scripts/send_request.py`: execute an atomic NodeRun from a JSON file.

  ```bash
  python3 src/scripts/send_request.py --request src/scripts/request.json
  ```

  Note: this helper does not include an `Authorization` header. For a quick local run, set `ARP_AUTH_PROFILE=dev-insecure` (dev only), or call the Atomic Executor via the Run Coordinator (recommended).

## Authentication

This service validates incoming JWTs (authn). It does not perform token exchange.

Auth is enabled by default (JWT). To disable for local dev, set `ARP_AUTH_PROFILE=dev-insecure`.
If no `ARP_AUTH_*` env vars are set, the service defaults to required JWT auth with the dev Keycloak issuer.

To enable local Keycloak defaults, set:
- `ARP_AUTH_PROFILE=dev-secure-keycloak`
- `ARP_AUTH_AUDIENCE=arp-atomic-executor`
- `ARP_AUTH_ISSUER=http://localhost:8080/realms/arp-dev`

### Coordinator → Atomic Executor calls

In the JARVIS stack, the Run Coordinator is expected to:
- mint/exchange a service-scoped JWT for the Atomic Executor audience via STS (OIDC/RFC 8693)
- call `POST /v1/atomic-node-runs:execute` with `Authorization: Bearer <token>`

The Atomic Executor validates the JWT (signature + optional `iss`/`aud`) and executes the handler.

## Upgrading

When upgrading to a new ARP Standard SDK release, bump pinned versions in `pyproject.toml` (`arp-standard-*==...`) and re-run conformance.
