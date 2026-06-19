---
title: Poe Response Body Boundary
type: security
date: 2026-06-14
status: completed
execution: code
---

# Poe Response Body Boundary

## Summary

Bound Poe validation and story-generation response bodies before decoding or
parsing them. Upstream content must not consume unbounded memory or appear in
diagnostic logs when a successful response has an unexpected shape.

## Requirements

- R1. Reject declared or streamed Poe response bodies larger than a documented
  byte limit before JSON parsing.
- R2. Decode accepted response bodies as strict UTF-8 and fail closed for
  malformed bytes.
- R3. Apply the same bounded reader to model validation and story generation.
- R4. Preserve successful story extraction, status handling, retry behavior,
  and content-free length diagnostics.
- R5. Replace unexpected-shape diagnostics with metadata that cannot expose the
  parsed upstream body.
- R6. Add mutation-sensitive unit and static coverage, then run the full gate on
  maintained Python versions and from an external working directory.

## Non-Goals

- Changing Poe request prompts, model selection, rate limits, or retry counts.
- Changing Modal proxy response handling.
- Persisting or truncating oversized upstream content.

## Implementation Units

1. Add a single bounded byte reader and explicit oversized-response exception
   in `src/poe_client.py`; route both response paths through it.
2. Extend `tests/test_poe_client.py` with declared-length, streamed-overflow,
   strict UTF-8, success extraction, validation, and log-redaction regressions.
3. Add a focused source contract under `scripts/`, wire it into
   `scripts/check-baseline.sh`, and synchronize project guidance.

## Verification

- Python 3.12.8 and Python 3.14.0: all 32 offline tests passed, including 18
  focused Poe client regressions.
- Eight hostile source mutations were rejected: removed declared-length guard,
  removed streamed-length guard, replacement UTF-8 decoding, restored
  unbounded reads, weakened shape-log redaction, exposed validation or
  generation decode failures, and removed overflow coverage.
- Python compilation passed for the implementation, tests, and focused checker
  on both maintained interpreters.
- `make check` passed the full 32-test maintenance baseline on Python 3.12.8
  and in an isolated pinned Python 3.14.0 environment.
- The Python 3.12.8 full gate also passed through the repository's absolute
  Makefile path from an external working directory.
- No live Poe, Modal, Hugging Face, or generated-story calls were made.
- Exact intended-path, generated-artifact, whitespace, conflict-marker, and
  changed-line credential-pattern audits passed before commit.
