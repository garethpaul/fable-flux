#!/usr/bin/env python3
import pathlib
import sys


source = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
tests = pathlib.Path(sys.argv[2]).read_text(encoding="utf-8")

contracts = {
    "fixed response limit": "MAX_POE_RESPONSE_BYTES = 1024 * 1024",
    "bounded chunk iterator": "response.content.iter_chunked(POE_RESPONSE_CHUNK_BYTES)",
    "declared-length rejection": "content_length > MAX_POE_RESPONSE_BYTES",
    "streamed-length rejection": "len(body) + len(chunk) > MAX_POE_RESPONSE_BYTES",
    "strict UTF-8 decode": 'decode("utf-8", errors="strict")',
    "shared bounded reader": "await self._read_response_text(response)",
    "redacted shape diagnostic": "Unexpected API response format from %s; response body omitted (%s)",
    "redacted validation UTF-8 diagnostic": "Poe validation response for {model} was not valid UTF-8; body omitted",
    "redacted generation UTF-8 diagnostic": "Poe response from {selected_model} was not valid UTF-8; body omitted",
}

for name, contract in contracts.items():
    expected = 2 if name == "shared bounded reader" else 1
    if source.count(contract) != expected:
        raise SystemExit(f"Poe response boundary must contain {expected} {name} contract(s).")

if "await response.text()" in source:
    raise SystemExit("Poe response paths must not use the unbounded text reader.")

if 'Unexpected API response format from {selected_model}: {result}' in source:
    raise SystemExit("Unexpected Poe response shapes must not log parsed bodies.")

for test_name in (
    "test_response_reader_rejects_declared_oversize_before_streaming",
    "test_response_reader_rejects_streamed_oversize_without_declared_length",
    "test_response_reader_rejects_invalid_utf8",
    "test_generation_extracts_story_through_bounded_reader",
    "test_unexpected_generation_shape_omits_parsed_body_from_logs",
    "test_model_validation_rejects_oversized_error_body",
    "test_response_reader_accepts_exact_byte_limit",
    "test_generation_invalid_utf8_log_omits_offending_bytes",
    "test_model_validation_invalid_utf8_log_omits_offending_bytes",
):
    if tests.count(test_name) != 1:
        raise SystemExit(f"Missing unique Poe response regression: {test_name}")
