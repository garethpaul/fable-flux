# Fable Flux Poe Validation Log Boundary

status: completed

## Context

The Poe client already avoids logging raw upstream response bodies during story
generation parse and HTTP error paths. Model accessibility validation still
parsed a 400 response and logged the raw error object when it looked like an
invalid model response.

## Objectives

- Preserve model accessibility validation behavior.
- Avoid logging raw Poe model validation response bodies.
- Keep enough diagnostic signal by recording a response body length summary.
- Add unit coverage for the validation logging boundary.
- Extend docs and the static baseline so raw validation response logging is not
  reintroduced.

## Work Completed

- Changed 400 model validation handling to read response text only for
  invalid-model detection.
- Logged `Poe validation response body omitted from logs` with response length
  instead of the raw error object.
- Added unit coverage that verifies private validation response content is not
  logged.
- Updated README, SECURITY, VISION, CHANGES, and `scripts/check-baseline.sh`.

## Verification

- `sh -n scripts/check-baseline.sh`
- `scripts/check-baseline.sh`
- `python3 -m unittest discover -s tests -p "test*.py"`
- `make check`
- `git diff --check`
