# Agent Trace SDK

This repository scaffolds the tracing SDK described in `SDK_Architecture_Detail.md` and is organized to match the phased delivery plan in `phases.txt`.

## Layout
- `traccia_sdk/` — Python client implementation.
  - `tracer/` — span, span context, tracer, and provider logic.
  - `instrumentation/` — decorator and monkey-patching helpers.
  - `exporter/` — HTTP exporter and related delivery utilities.
  - `context/` — context variable management and propagators.
  - `processors/` — span processors, sampling, and batching utilities.
  - `examples/` — usage examples and quickstarts.
- `backend/` — ingest API and storage components.
- `proto/` — protobuf definitions for wire formats.
- `docs/` — product and developer documentation.

## Status
Phases completed: 0–6 (foundation, core tracing engine, processors/queue, exporter stubs, instrumentation, propagation, cost intelligence). Phase 7 adds DX helpers (env/CLI/console). Remaining: Phases 8–10 per `phases.txt`.
