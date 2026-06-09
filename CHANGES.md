# Changes

## 2026-06-09

- Rejected scalar or mixed-type uploader `characters`/`tags` metadata before
  Hugging Face dataset record creation, and exposed `make lint`/`make build`
  aliases for the offline baseline.
- Aligned quick story validation with the full mapping-shaped frontmatter
  parser and added regression coverage.
- Rejected non-mapping YAML story frontmatter at parse time and added unit and
  baseline coverage for malformed metadata.
- Stopped logging raw Poe response bodies on Python client parse and HTTP error
  paths.
- Added a response-length summary helper, unit coverage, and baseline guard for
  the Poe logging boundary.
- Rejected non-mapping story frontmatter in the Hugging Face uploader before
  dataset record creation.

## 2026-06-08

- Added an offline maintenance baseline with `make check` and `scripts/check-baseline.sh`.
- Added offline unit tests for story validation, Poe model configuration, prompt shape, and diversity selection of unused characters/settings.
- Hardened the Next.js Modal proxy to require a configured HTTPS endpoint with a hostname, trim server-side env values, avoid raw upstream content logging, and use the Fable Flux served model name by default.
- Split the story page into a dynamic server wrapper and client component so the stable `next build` production path succeeds.
- Updated environment examples, setup script output, frontend docs, and deployment notes for `POE_API_KEY`, `HF_TOKEN`, `MODAL_API_KEY`, `MODAL_API_URL`, and `MODAL_MODEL`.
- Added ignore rules for local secrets, Python caches, virtual environments, logs, and generated runtime output.
