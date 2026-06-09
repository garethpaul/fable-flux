# Fable Flux Poe Rate Limiter Guard

status: completed

## Context

The Poe client uses a local token-bucket limiter to keep concurrent story
generation within provider limits. The limiter accepted zero or negative rate
settings and the depleted-token path slept once without rechecking token state
or consuming the newly available token afterward.

## Objectives

- Reject invalid rate limiter configuration before client setup continues.
- Recheck token state after waiting so sleeping callers consume a real token.
- Keep sleeping outside the lock so concurrent callers do not block token
  accounting.
- Add deterministic offline tests for the wait path without real time delays.
- Extend project docs and the baseline so this boundary stays covered.

## Work Completed

- Switched the limiter clock to injectable `time.monotonic` and sleep hooks.
- Added validation for positive rate and period values.
- Changed `acquire` to loop, refill under lock, and consume a token after
  each wait.
- Added unit coverage for invalid limits and the depleted-token wait path.
- Updated README, VISION, SECURITY, CHANGES, and `scripts/check-baseline.sh`.

## Verification

- `python3 -m unittest discover -s tests -p "test*.py"`
- `scripts/check-baseline.sh`
- `make check`
- `git diff --check`
