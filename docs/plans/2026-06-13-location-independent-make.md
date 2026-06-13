---
title: Location-Independent Fable Flux Verification
type: reliability
date: 2026-06-13
status: completed
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

## Verification

- `make check` passed all 23 offline tests at repository root and from /tmp
  through the absolute Makefile path.
- Optional readability, sentiment, Hugging Face, and frontend dependencies
  remained explicitly unavailable or skipped without weakening the gate.
- Four hostile root, checker-path, documentation, and completed-plan mutations
  were rejected.
- Shell syntax, diff, exact-path, secret, and generated-artifact checks passed.
