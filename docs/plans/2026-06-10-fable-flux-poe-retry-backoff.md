# Fable Flux Poe Retry Backoff

status: completed

## Context

The Poe story client retried transient upstream failures, but timeout handling
slept in the exception branch and then slept again in the shared retry branch.
Rate-limit and timeout failures also slept after the final allowed attempt even
though no subsequent request would be made.

## Objectives

- Apply exactly one failure-specific delay before each actual retry.
- Preserve exponential provider backoff for HTTP 429 responses.
- Return immediately when the configured retry budget is exhausted.
- Add deterministic offline coverage without real network calls or time delays.

## Work Completed

- Centralized each attempt's retry delay before the shared retry boundary.
- Kept 429 delays at 60 seconds with exponential growth capped at 300 seconds.
- Kept timeout delays at five seconds per attempt without the duplicate generic
  sleep.
- Added async unit coverage for timeout exhaustion and successful rate-limit
  retry paths.
- Extended the repository baseline and operational documentation.

## Verification

- `python3 -m unittest discover -s tests -p "test_poe_client.py"`
- `python3 -m unittest discover -s tests -p "test*.py"`
- `make check`
- `make lint`
- `make test`
- `make build`
- `git diff --check`
