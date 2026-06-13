---
title: Modal Response Content-Type Boundary
type: security
date: 2026-06-13
status: planned
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
