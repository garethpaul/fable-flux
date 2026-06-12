# Poe Model Validation Status Contract

## Status: Completed

## Goal

Prevent failed Poe model preflight requests from being reported as accessible
models merely because their unhandled HTTP status is below 500.

## Prioritized Engineering Work

1. **Require an explicit successful validation response (this change).** Treat
   only HTTP 200 as proof that a configured model is accessible; fail closed for
   authentication, authorization, rate-limit, redirect, unexpected success,
   and server statuses.
2. **Classify validation failures for operators (follow-up).** Return structured
   failure reasons without exposing upstream response bodies or credentials.
3. **Broaden live API contract tests (follow-up).** Add opt-in integration tests
   against a controlled account once a credential-safe CI environment exists.
4. **Add frontend API route tests (follow-up).** Exercise prompt bounds, Modal
   configuration validation, and redacted upstream failures at the route level.

## Requirements

- R1. `_process_validation_response` must return `True` only for HTTP 200.
- R2. HTTP 400 model errors, 401 authentication failures, 403 authorization
  failures, 404 missing models, 429 rate limits, and 5xx failures must return
  `False`.
- R3. Unexpected 2xx/3xx statuses must also return `False`; successful access
  must not be inferred from a broad numeric range.
- R4. Raw validation response bodies, API keys, prompts, and generated content
  must remain absent from logs.
- R5. Existing generation retry behavior for HTTP 429 and 401 must remain
  unchanged.
- R6. Tests, documentation, and the maintenance baseline must reject restoring
  `response.status < 500` or another range-based accessibility decision.

## Verification

- `make check`.
- `python3 -m unittest discover -s tests -p "test*.py"`.
- GitHub Actions on Python 3.10, 3.12, and 3.14 plus the Node 20/22/24 frontend
  matrix.
- `git diff --check`.
- Mutation check: restoring `return response.status < 500` must fail the static
  baseline and focused model-validation test.

## Work Completed

- Changed Poe model preflight so only HTTP 200 returns accessible.
- Kept explicit redacted handling for HTTP 400 and 404 while making all other
  statuses fail closed without reading or logging response bodies.
- Added one table-driven test covering HTTP 200, unexpected 201, redirect 302,
  model error 400, authentication 401, authorization 403, missing model 404,
  rate limit 429, and server failure 500.
- Updated project, security, roadmap, and changelog documentation and extended
  the static baseline to reject range-based accessibility decisions.

## Verification Completed

- `make check` passes locally with 23 tests.
- `git diff --check` passes.
- A context-specific mutation restoring `return response.status < 500` fails
  five focused status cases and the static baseline.
- GitHub Actions push run `27391848731` passed on Python 3.10, 3.12, and 3.14
  and Node 20, 22, and 24.
- GitHub Actions pull-request run `27391849643` passed the same six-job matrix.
