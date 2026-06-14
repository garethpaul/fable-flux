---
title: Modal Redirect Boundary
type: security
status: planned
date: 2026-06-14
---

# Modal Redirect Boundary

## Summary

Reject HTTP redirects for server-side Modal story requests so endpoint
validation cannot be bypassed after dispatch and prompt bodies are never
forwarded to a redirect destination.

## Requirements

- R1. The Modal `fetch` call must set `redirect: "error"` before request
  headers and body construction.
- R2. Preserve the HTTPS hostname validation, 30-second timeout, prompt bound,
  server-side bearer token, JSON response media-type check, and story-shape
  validation.
- R3. Extend the existing static fetch-order contract and synchronized security
  guidance so removal, acceptance, or post-dispatch drift fails the gate.
- R4. Keep hosted checks offline and do not call Modal or expose prompts,
  generated stories, or credentials during validation.

## Non-Goals

- Following same-origin redirects or introducing a redirect allowlist.
- Changing the Modal endpoint, model, payload schema, timeout, or error body.
- Adding dependencies or making live provider requests.

## Planned Verification

- Run the focused static route contract and the full pinned `make check` gate.
- Run the full gate from `/tmp` through the absolute Makefile path.
- Reject isolated hostile mutations for missing redirect policy, redirect
  following, option ordering, documentation, and completed-plan evidence.
- Audit exact intended paths, generated artifacts, conflict markers,
  whitespace, and changed-line credential patterns before commit.
- Take one bounded exact-head hosted check and code-scanning snapshot after push;
  do not poll pending jobs.
