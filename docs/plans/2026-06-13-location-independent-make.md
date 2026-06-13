---
title: Location-Independent Fable Flux Verification
type: reliability
date: 2026-06-13
status: in progress
execution: code
---

# Location-Independent Fable Flux Verification

## Summary

Resolve the maintenance checker from the loaded Makefile so the complete
offline gate works outside the repository directory.

## Requirements

- R1. Derive the repository root from `MAKEFILE_LIST`.
- R2. Invoke the checker through its absolute repository path.
- R3. Preserve all 23 offline tests and optional frontend lint behavior.
- R4. Add mutation-sensitive contracts and actual `/tmp` verification.
- R5. Do not alter story, Modal, Poe, Hugging Face, frontend, dependency, or
  workflow behavior.

## Verification Plan

- Run the full gate at repository root and from `/tmp`.
- Reject hostile root, checker-path, documentation, and plan mutations.
- Run shell syntax, diff, exact-path, secret, and artifact checks.

## Non-Goals

- Installing optional model, dataset, frontend, or hosted-service tooling.
