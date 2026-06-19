# Modal Response Body Boundary

Status: Completed

## Problem

The frontend Modal proxy parsed successful JSON responses with `Response.json`,
which buffers an unbounded body before runtime shape validation.

## Requirements

1. Reject declared and streamed bodies above 1 MiB.
2. Decode UTF-8 strictly and parse JSON only after the byte limit.
3. Preserve timeout, redirect, status, media-type, and story-shape boundaries.

## Verification

- Root and external-directory `make check` passed frontend and repository gates.
- Six hostile mutations were rejected for size, streaming, cancellation,
  strict-decoding, documentation, and plan-status regressions.
- No live Modal request was performed.
