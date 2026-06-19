---
title: Story Response Shape Validation
type: reliability
date: 2026-06-13
status: completed
execution: code
---

# Story Response Shape Validation

## Status: Completed

## Summary

Reject malformed generated or stored story objects before they reach React
rendering code.

## Problem

The Modal proxy currently checks only whether required values are truthy. A
model response can therefore supply numbers or objects for string fields, or an
invalid character list, and still be returned to the browser. The story page
then calls string methods and renders those values, causing a client-side
runtime failure. Manually corrupted or stale `localStorage` data reaches the
same consumer without validation.

## Requirements

- R1. Add one shared runtime type guard for `StoryResponse`.
- R2. Require non-empty strings for title, setting, story, and moral.
- R3. Accept characters only as a non-empty string or a non-empty array of
  non-empty strings or named character objects with an optional string
  description.
- R4. Reject malformed Modal story JSON before returning a success response.
- R5. Reject malformed stored stories before setting page state and redirect to
  the home route without rendering them.
- R6. Preserve prompt validation, Modal timeout/media-type checks, error-body
  redaction, model configuration, and valid story rendering.
- R7. Protect both consumers and the malformed fixture cases with static and
  mutation-sensitive contracts.

## Verification Plan

- Run focused static fixture validation for valid and malformed story shapes.
- Run the full repository Make targets on Python 3.12 and 3.14.
- Run frontend lint and production build with bounded commands.
- Reject mutations that weaken string, character, API, storage, plan, or
  evidence contracts.
- Audit exact paths, generated artifacts, secrets, and dependency/workflow
  preservation before commit.

## Non-Goals

- Changing story generation prompts, Modal request parameters, UI layout,
  publishing flows, or dataset schemas.
- Adding a new runtime validation dependency.

## Work Completed

- Added a dependency-free `isStoryResponse` runtime type guard beside the
  shared TypeScript contract.
- Required non-empty string story fields and a valid non-empty characters value.
- Applied the same guard after Modal JSON parsing and after local storage JSON
  parsing before either consumer accepts the object.
- Synchronized reliability, security, vision, change, and contributor guidance.

## Verification Completed

- Compiled the production guard and passed 2 valid plus 9 malformed runtime
  fixtures covering scalar fields, empty/invalid characters, objects, arrays,
  and absent values.
- Frontend lint passed with the existing five `no-img-element` warnings and no
  errors; the Next.js 15.5.19 production build compiled, type-checked, and
  generated all routes successfully under Node 20.19.5.
- `make check`, `make lint`, `make test`, and `make build` passed all 23 offline
  tests under Python 3.12.8 and under an isolated Python 3.14.0 environment with
  the pinned `requirements-ci.txt` dependencies.
- `sh -n scripts/check-baseline.sh` and `git diff --check` passed.
- Six isolated hostile mutations were rejected across non-empty strings,
  character arrays, API validation, stored-story validation, plan status, and
  mutation evidence.
- No Poe, Hugging Face, Modal, dataset publication, or generated-story network
  call was made.
