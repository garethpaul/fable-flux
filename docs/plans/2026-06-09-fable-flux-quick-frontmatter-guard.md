---
title: Fable Flux Quick Frontmatter Guard
date: 2026-06-09
status: completed
execution: code
---

## Context

The full story validator rejected non-mapping YAML frontmatter before content
quality checks, but `quick_validate` only checked that YAML could be parsed.
Sequence or scalar metadata could pass the quick path even though complete
validation would reject it.

## Goals

- Keep quick validation aligned with full story frontmatter parsing.
- Reject non-mapping YAML frontmatter before quick validation returns success.
- Add offline regression coverage for the quick validation path.
- Extend the baseline gate so the quick/full validator contract remains
  guarded.

## Verification

- `python3 -m unittest discover -s tests -p "test_story_validator.py"`
- `python3 -m unittest discover -s tests -p "test*.py"`
- `scripts/check-baseline.sh`
- `make check`
- `git diff --check`
