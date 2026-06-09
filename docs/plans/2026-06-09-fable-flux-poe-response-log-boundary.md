---
title: Fable Flux Poe Response Log Boundary
date: 2026-06-09
status: completed
execution: code
---

## Context

The repository already avoids logging raw frontend Modal story content, but the
Python Poe client still logged raw upstream response bodies on JSON parse and
HTTP error paths. Those bodies can contain prompts, generated stories, or
provider diagnostics that should stay out of local logs.

## Goals

- Avoid logging raw Poe response bodies.
- Keep enough diagnostic signal to understand failure size and status.
- Add an offline test for the response-body summary helper.
- Extend the baseline gate so raw response logging does not return.

## Implementation

- Added `_response_body_summary` to report only response body length.
- Replaced raw response/error body logs in `_make_request`.
- Added unit coverage proving summaries omit raw response content.
- Extended `scripts/check-baseline.sh` with source and test guards.

## Verification

- `python3 -m unittest discover -s tests -p "test*.py"`
- `scripts/check-baseline.sh`
- `make check`
- `git diff --check`
