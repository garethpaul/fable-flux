---
title: Modal Response Content-Type Boundary
type: security
date: 2026-06-13
status: completed
execution: code
---

# Modal Response Content-Type Boundary

## Summary

Require a successful Modal response to declare JSON before parsing its body, so
HTML, text, or missing media types fail closed at the proxy boundary.

## Requirements

- R1. Validate `Content-Type` only after the existing successful HTTP status
  check and before `modalResponse.json()`.
- R2. Accept `application/json` case-insensitively with optional parameters.
- R3. Reject missing, malformed, or non-JSON media types with the existing
  generic upstream-failure posture.
- R4. Do not log response bodies, prompts, generated stories, API keys, or raw
  upstream headers.
- R5. Preserve timeout, endpoint, prompt, model, status, and story-shape
  validation contracts.

## Verification Plan

- Add a section-scoped static contract for status, media-type, and parse order.
- Run the Python maintenance baseline and frontend lint/build/audit on the
  maintained Node versions available locally.
- Reject hostile mutations that remove or broaden the media-type check, move it
  after parsing, or weaken docs/plan evidence.
- Use no Modal credentials, live requests, billable generation, or story data.

## Non-Goals

- Changing Modal request payloads, model choice, or response story schema.
- Accepting vendor-specific or text JSON media types.
- Deploying the proxy or calling external AI services.

## Work Completed

- Added a strict media-type helper that accepts `application/json`
  case-insensitively with optional parameters.
- Kept the successful-status check before the media-type boundary and moved no
  existing timeout, prompt, endpoint, model, or story-shape behavior.
- Returned the existing generic upstream failure when the Content-Type is
  missing or non-JSON, without logging raw headers or bodies.
- Added ordering, exact-media-type, documentation, and plan-evidence contracts
  to the offline baseline.

## Verification Completed

- `make check` ran all 23 Python tests and reached the intentional plan-status
  gate before this completed evidence was recorded. Afterward, `make lint`,
  `make test`, `make build`, and `make check` all passed the completed baseline.
- Clean frontend installs, lint, production builds, and moderate npm audits
  passed locally on Node 20, 22, and 24. Lint retained five existing
  `@next/next/no-img-element` warnings and reported no errors.
- Eight isolated hostile mutations were rejected, covering helper removal,
  broadened media acceptance, missing-value acceptance, parse-before-check
  ordering, header-contract removal, documentation removal, stale plan status,
  and missing verification evidence.
- `git diff --check`, intended-file artifact checks, and added-line secret scans
  passed.
- No Modal credentials, live requests, billable generation, deployments, or
  generated story data were used.
