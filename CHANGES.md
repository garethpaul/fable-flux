# Changes

## 2026-06-08

- Added an offline maintenance baseline with `make check` and `scripts/check-baseline.sh`.
- Added offline unit tests for story validation, Poe model configuration, prompt shape, and diversity selection of unused characters/settings.
- Hardened the Next.js Modal proxy to require a configured HTTPS endpoint, trim server-side env values, avoid raw upstream content logging, and use the Fable Flux served model name by default.
- Updated environment examples, setup script output, frontend docs, and deployment notes for `POE_API_KEY`, `HF_TOKEN`, `MODAL_API_KEY`, `MODAL_API_URL`, and `MODAL_MODEL`.
- Added ignore rules for local secrets, Python caches, virtual environments, logs, and generated runtime output.
