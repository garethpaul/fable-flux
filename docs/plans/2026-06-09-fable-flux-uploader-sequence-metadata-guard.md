---
title: Fable Flux Uploader Sequence Metadata Guard
date: 2026-06-09
status: completed
execution: code
---

## Context

The Hugging Face uploader parses YAML story metadata into JSONL records with
sequence-shaped `characters` and `tags` fields. Mapping-shaped frontmatter is
already required, but scalar or mixed-type sequence fields could still produce
records that do not match the dataset card.

## Goals

- Keep valid story metadata unchanged for dataset export.
- Reject scalar `characters` or `tags` metadata before record creation.
- Reject non-string or blank sequence items before record creation.
- Expose explicit `make lint`, `make test`, and `make build` gates for the
  offline baseline.

## Implementation

- Added `StoryParser._metadata_string_list` to validate list-typed metadata.
- Added uploader unit tests for scalar and mixed-type sequence metadata.
- Extended the static baseline, README, vision, security notes, and change log.
- Added Makefile aliases for lint and build gates while the project uses the
  offline baseline as its installed verification tool.

## Verification

- `python3 -m unittest discover -s tests -p "test_huggingface_uploader.py"`
- `python3 -m unittest discover -s tests -p "test*.py"`
- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`
