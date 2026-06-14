---
title: Client Request Body Boundary
type: security
date: 2026-06-14
status: in-progress
execution: code
---

# Client Request Body Boundary

## Summary

Bound the public story-generation request body before JSON parsing. Reject
unsupported media types, invalid declared lengths, oversized streamed bodies,
invalid UTF-8, and malformed JSON before reading Modal configuration or
starting a billable upstream request.

## Prioritized Engineering Tasks

1. Require an `application/json` request media type.
2. Reject invalid or greater-than-4-KiB `Content-Length` values before reading.
3. Stream at most 4 KiB when length is absent or inaccurate, cancelling the
   reader on overflow.
4. Decode strict UTF-8 and parse JSON behind a generic 400 response.
5. Preserve the existing 1-to-200-character prompt and Modal request controls.

## Requirements

- R1. Client request bodies must be limited to 4 KiB by declared and observed
  byte count.
- R2. Request JSON must use `application/json`, allowing normal parameters such
  as `charset=utf-8`.
- R3. Invalid UTF-8, malformed JSON, missing bodies, and size violations must
  fail before environment configuration and Modal dispatch.
- R4. Error responses must not echo body content or parser details.
- R5. Existing prompt, timeout, redirect, response media type, response size,
  and story-shape validation must remain unchanged.

## Non-Goals

- Adding authentication or distributed rate limiting.
- Changing the 200-character prompt contract.
- Making live or billable Modal requests during validation.

## Verification

- Pending implementation and bounded validation.
