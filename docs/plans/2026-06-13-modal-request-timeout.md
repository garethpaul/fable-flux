---
title: Modal Proxy Request Timeout
type: reliability
status: completed
date: 2026-06-13
---

# Modal Proxy Request Timeout

## Summary

Bound the frontend server's outbound Modal generation request so a stalled
provider cannot hold a story request open indefinitely.

## Priority

1. Abort Modal requests after a fixed, documented deadline.
2. Return a stable gateway-timeout response without exposing raw provider or
   runtime exception details.
3. Preserve endpoint validation, prompt bounds, model configuration, and story
   response validation.

## Requirements

- R1. The Modal `fetch` call must use a 30-second abort signal.
- R2. Timeout failures must return HTTP 504 with a generic client-safe message.
- R3. Timeout and other request failures must not log raw exception objects,
  prompts, generated content, API keys, or upstream response bodies.
- R4. Existing HTTPS URL validation, 200-character prompt limit, server-side
  credentials, and story-shape validation must remain unchanged.
- R5. Static contracts and the TypeScript production build must reject removal
  or reordering of the timeout signal.
- R6. The green hosted runner pin from PR #3 must be integrated by replaying its
  exact source patch without closing or modifying that PR.

## Non-Goals

- Retrying Modal requests or changing generation parameters.
- Adding client-side cancellation or changing the browser request timeout.
- Replacing Next.js, the Modal endpoint, or the model.
- Logging provider error bodies or generated stories for diagnostics.

## Implementation Units

### 1. Provider Deadline

Files: `front-end/src/app/api/chat/completions/route.ts`

- Add a named 30-second timeout constant.
- Pass `AbortSignal.timeout` directly to the Modal fetch options.
- Map timeout errors to a generic 504 response and use generic server logs.

### 2. Offline Contracts

Files: `scripts/check-baseline.sh`

- Require the timeout constant, signal, and generic 504 handling.
- Prove the signal occurs inside the Modal fetch before response handling.
- Reject raw exception logging in the route.

### 3. Project Guidance

Files: `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`

- Document the bounded provider request and client-safe timeout behavior.

## Verification Plan

- Run the frontend lint and production build under the installed Node runtime.
- Run `make check`, `make lint`, `make test`, and `make build`.
- Remove the signal, change the deadline, and move the signal outside the fetch
  options; the static/build gate must reject each mutation.
- Run dependency audit, shell syntax, `git diff --check`, and intended-file
  secret scans.
- Take one bounded exact-head hosted matrix snapshot after push; do not poll.

## Verification

- Node 20.19.5 `npm ci`, frontend lint, Next.js 15.5.19 production build, and
  moderate audit passed; lint retained five existing non-failing image warnings.
- Removing the fetch signal produced the expected `missing signal mutation failed` result.
- Changing the deadline from 30 seconds produced the expected `changed deadline mutation failed` result.
- Moving the signal behind response handling produced the expected `reordered signal mutation failed` result.
- The copied offline baseline passed all 23 Python tests and the new frontend
  source contracts.
- The rooted full gate, diff check, shell syntax, and intended-file secret scan
  passed.
- The exact pushed head still requires the bounded hosted Node matrix across
  Node 20, 22, and 24 before aggregate promotion.

## Work Completed

- Added a named 30-second Modal request timeout and applied it directly to
  server-side fetch.
- Added a generic HTTP 504 timeout response and removed raw exception-object
  logging from the outer request failure path.
- Added exact source and ordering contracts for timeout value, signal placement,
  response status, and generic logs.
- Updated project reliability, security, and maintenance guidance.
- Replayed the exact hosted runner pin patch from source commit
  `a3fd99872688acb12dbde74babc7688b05df6491`; PR #3 remains open and unchanged.
