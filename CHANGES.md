# Changes

## 2026-06-14

- The Modal proxy rejects HTTP redirects after endpoint validation.

## 2026-06-13

- Made Make verification independent of the caller's working directory.
- Added one runtime shape guard for generated and stored stories so malformed
  string fields or character lists fail before API success or React rendering.
- Require successful Modal responses to declare `application/json` before body
  parsing, with generic failures for missing or non-JSON media types.
- Bounded Modal generation requests to 30 seconds and return a generic 504
  response without logging raw request exceptions.
- Added explicit ownership, approval, provenance, credential, safety/privacy,
  postflight, rollback, and incident boundaries for Hugging Face dataset
  publication and Modal model serving.

## 2026-06-12

- Pinned both hosted jobs to Ubuntu 24.04 and added exact runner, plan, and
  documentation contracts that reject floating image labels.
- Made Poe model preflight fail closed for every status except HTTP 200 instead
  of treating unhandled 2xx, 3xx, and 4xx responses as accessible.
- Added regression coverage for unexpected success, redirect, authentication,
  authorization, rate-limit, and server responses without logging bodies.

## 2026-06-10

- Corrected Poe retry backoff so timeout and rate-limit failures sleep once per
  actual retry and exhausted attempts return without an unnecessary delay.
- Added pinned Python 3.10/3.12/3.14 and Node 20/22/24 GitHub Actions matrices
  for offline tests, frontend linting, production builds, and npm audit.
- Disabled persisted checkout credentials in both hosted jobs and enforced the
  read-only workflow boundary in the offline source contract.
- Pinned minimal CI dependencies, refreshed compatible frontend packages, and
  updated React and React DOM to 19.2.7.

## 2026-06-09

- Hardened the Poe client rate limiter to reject invalid limits and recheck
  token state after sleeping before allowing another upstream request.
- Omitted raw Poe model validation response bodies from logs and recorded a
  length summary instead.
- Rejected non-string story validator `characters`/`tags` metadata in both
  full and quick validation.
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
