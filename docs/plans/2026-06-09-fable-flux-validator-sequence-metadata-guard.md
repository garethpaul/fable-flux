# Fable Flux Validator Sequence Metadata Guard

status: completed

## Context

The Hugging Face uploader already rejects malformed `characters` and `tags`
frontmatter before building dataset records. The story validator still accepted
mixed-type sequences in full validation, and quick validation only verified that
frontmatter was mapping-shaped.

## Objectives

- Keep quick and full story validation aligned on metadata shape.
- Require `characters` and `tags` to be non-empty string lists before a story
  can pass validation.
- Preserve existing story content validation and quality checks.
- Extend the offline baseline and docs so validator and uploader metadata
  boundaries stay aligned.

## Work Completed

- Added a shared `_validate_string_list_field()` helper in `StoryValidator`.
- Updated frontmatter validation to reject non-string or blank
  `characters`/`tags` sequence items.
- Updated quick validation to run frontmatter validation after parsing.
- Added regression tests for full and quick validation of malformed sequence
  metadata.
- Extended `scripts/check-baseline.sh` to require the validator helper, tests,
  documentation, and completed plan.
- Documented the guard in README, SECURITY, VISION, and CHANGES.

## Verification

- `sh -n scripts/check-baseline.sh`
- `scripts/check-baseline.sh`
- `python3 -m unittest discover -s tests -p "test*.py"`
- `make check`
- `make lint`
- `make test`
- `make build`
- `git diff --check`
