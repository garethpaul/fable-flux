---
title: Fable Flux Uploader Frontmatter Guard
date: 2026-06-09
status: completed
execution: code
---

## Context

Story validation already rejects YAML frontmatter that is not a mapping, but the
Hugging Face dataset uploader has its own parser. Sequence, scalar, or empty
frontmatter should not fall through to broad exception handling or produce
records with default metadata.

## Goals

- Require uploader frontmatter metadata to be a mapping.
- Return a parse failure before dataset records are constructed.
- Add offline regression coverage for malformed uploader metadata.
- Extend the baseline so the uploader and validator stay aligned.

## Implementation

- Added an `isinstance(metadata, dict)` guard in `StoryParser.parse_story_file`.
- Added `tests/test_huggingface_uploader.py` with valid and non-mapping
  frontmatter cases.
- Updated the static baseline and project docs to cover the dataset export
  parser boundary.

## Verification

- `python3 -m unittest discover -s tests -p "test_huggingface_uploader.py"`
- `python3 -m unittest discover -s tests -p "test*.py"`
- `scripts/check-baseline.sh`
- `make check`
- `git diff --check`
