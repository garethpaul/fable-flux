# Poe Model Validation Status Contract

## Status: In Progress

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
