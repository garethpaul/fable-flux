---
title: Modal Redirect Boundary
type: security
status: completed
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

## Verification

- The focused static route-order contract and shell syntax check passed.
- Six isolated hostile mutations were rejected for missing redirect policy,
  redirect following, option ordering, checker contract removal, documentation,
  and completed-plan evidence.
- The pinned `make check` passed 23 tests from the checkout and from `/tmp`
  through the absolute Makefile path.
- `npm ci --ignore-scripts`, `npm run lint`, `npm run build`, and the moderate
  `npm audit` gate passed with zero vulnerabilities. ESLint reported zero
  errors and five pre-existing `<img>` warnings outside this change.
- Exact intended-path, unchanged manifest/workflow/dependency, generated-
  artifact, untracked-file, conflict-marker, whitespace, and changed-line
  credential-pattern audits passed.
- Sequential security, correctness, maintainability, and testing review found
  no actionable issue; redirect failures use the generic request-failure path
  without logging prompts, bodies, credentials, or raw exceptions.
- Generated `front-end/node_modules`, `front-end/.next`, and known Python cache
  directories were removed only after existence checks.
- One bounded exact-head hosted check and code-scanning snapshot is required
  after push; pending jobs will not be polled.
