---
title: Fable Flux Frontmatter Mapping Guard
date: 2026-06-09
status: completed
execution: code
---

## Context

Story files rely on YAML frontmatter for IDs, story type, characters, settings,
word counts, and tags. The validator parsed YAML safely, but it accepted any
valid YAML value before running metadata checks. Sequence or scalar frontmatter
could then flow into downstream validation and produce confusing field errors or
exceptions instead of a clear structure failure.

## Goals

- Require story frontmatter to be a mapping before validation continues.
- Keep malformed metadata failures on the same "invalid story structure" path as
  missing or unparsable frontmatter.
- Add an offline regression test for non-mapping frontmatter.
- Extend the baseline gate so the parser boundary remains covered.

## Implementation

- Added an `isinstance(frontmatter, dict)` guard in `_parse_story_structure`.
- Added `test_non_mapping_frontmatter_is_invalid` for YAML sequence metadata.
- Extended `scripts/check-baseline.sh` with source, test, and plan-status
  checks.
- Updated README, VISION, and CHANGES to document the guarded metadata shape.

## Verification

- `python3 -m unittest discover -s tests -p "test_story_validator.py"`
- `python3 -m unittest discover -s tests -p "test*.py"`
- `scripts/check-baseline.sh`
- `make check`
- `git diff --check`
