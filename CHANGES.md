# Changes

## 2026-07-18T00:00:00Z - P1 - Observe that the test suite still asserts

### Summary
Closed the gate's terminal verification rung: `make check` ran the real suite and
pinned guard and test-case text, but nothing observed that the suite's assertions
still assert. An added `tests/test*.py` module rebinding
`unittest.TestCase.assert*` shipped a real fail-open story-validator defect at
exit 0 with every pinned literal byte-identical.

### Work completed
- Made `tests/` closed-world with the `find` inventory idiom already used for the
  workflow directory, so an added module is named and rejected.
- Added `scripts/test-security-mutations.py`, an out-of-band planted-defect
  control that stages `src/` and `tests/`, plants each of seven real fail-open
  defects, and requires the real suite to go red, behind a clean-tree control.
  A neutered suite makes every mutation survive, so the control fails by
  construction rather than by pinning.
- Wired the control into `scripts/check-baseline.sh` so hosted `make check`
  reaches it, and pinned its planted-defect loop and mutation count.
- Strengthened `test_parse_story_file_rejects_non_string_sequence_items`, which
  the new control caught passing with its guard deleted because the outer
  `except Exception` returns `None` for the incidental `AttributeError` too. It
  now asserts the guard's own diagnostic.

### Threads
- None; no open pull requests by the author existed on the repository.

## 2026-06-27T00:39:00Z - P2 - Lazily load package exports

### Summary
Decoupled dependency-free story utilities from optional network and generation
dependencies while preserving the package's convenience import API.

### Work completed
- Replaced eager `src` imports with a PEP 562 lazy export map.
- Preserved `from src import StoryGenerator`, `DiversityTracker`, `PoeClient`,
  `StoryValidator`, and `BatchProcessor` behavior on first access.
- Added a regression proving package import and `DiversityTracker` access do not
  load the Poe client or story generator.

### Threads
- None; no open pull requests or issues existed, and the stale documentation
  branch was behind the protected default branch.

### Files changed
- `src/__init__.py` — resolve public exports lazily and cache loaded values.
- `tests/test_package_exports.py` — enforce optional-dependency isolation.
- `README.md` — document lightweight package imports.
- `docs/plans/2026-06-27-lazy-package-exports.md` — record design/evidence.

### Validation
- Focused regression before implementation — failed because importing `src`
  immediately required unavailable `aiohttp`.
- Dependency-free package and diversity tests — passed without `aiohttp`.
- Validator/uploader tests — passed with their documented optional fallbacks.
- Exact `requirements-ci.txt` virtual environment — `make check` passed all 36
  backend tests; frontend lint truthfully skipped without `node_modules`.
- `git diff --check` — passed.

### Bugs / findings
- Python imports execute package `__init__` before a requested submodule, so the
  eager convenience imports made stdlib-only modules depend on every optional
  client dependency.

### Blockers
- Local frontend dependencies were not installed; hosted Node matrices remain
  authoritative for lint, production build, and audit.

### Next action
- Require the exact pull-request head to pass all hosted Python and Node
  matrices plus CodeQL before merge.

## 2026-06-18

- Rejected unsupported story types, non-string identifiers and settings, plus
  non-positive or boolean word counts before validation or Hugging Face record
  creation.
- Refreshed the compatible frontend lockfile to Tailwind CSS 4.3.1 and the
  latest Node 20 type definitions while preserving all framework and major
  version boundaries.

## 2026-06-16

- The frontend targets Next.js 16.2 on Node 20.9 or newer and uses native flat ESLint configuration.
- Story storage now uses React's external-store contract so hydration does not
  rely on synchronous state updates inside an effect.

## 2026-06-15

- Replaced the five raw home-page images with dimensioned Next.js image
  components, eliminating the maintained frontend image lint warnings.

## 2026-06-14

- The frontend bounds Modal JSON responses to 1 MiB of strict UTF-8.
- The public frontend route bounds client JSON requests to 4 KiB of strict UTF-8
  before parsing or Modal configuration access.
- Bounded Poe validation error and generation responses to 1 MiB of strict
  UTF-8 and removed parsed upstream content from shape-error logs.
- The Modal proxy rejects HTTP redirects after endpoint validation.

## 2026-06-13

- Made Make verification independent of the caller's working directory.
- Added one runtime shape guard for generated and stored stories so malformed
  string fields or character lists fail before API success or React rendering.
- Require successful Modal responses to declare `application/json` before body
  parsing, with generic failures for missing or non-JSON media types.
- Bounded Modal generation requests to 30 seconds and return a generic 504
  response without logging raw request exceptions.
- Added explicit ownership, approval, provenance, credential, safety/privacy,
  postflight, rollback, and incident boundaries for Hugging Face dataset
  publication and Modal model serving.

## 2026-06-12

- Pinned both hosted jobs to Ubuntu 24.04 and added exact runner, plan, and
  documentation contracts that reject floating image labels.
- Made Poe model preflight fail closed for every status except HTTP 200 instead
  of treating unhandled 2xx, 3xx, and 4xx responses as accessible.
- Added regression coverage for unexpected success, redirect, authentication,
  authorization, rate-limit, and server responses without logging bodies.

## 2026-06-10

- Corrected Poe retry backoff so timeout and rate-limit failures sleep once per
  actual retry and exhausted attempts return without an unnecessary delay.
- Added pinned Python 3.10/3.12/3.14 and Node 20/22/24 GitHub Actions matrices
  for offline tests, frontend linting, production builds, and npm audit.
- Disabled persisted checkout credentials in both hosted jobs and enforced the
  read-only workflow boundary in the offline source contract.
- Pinned minimal CI dependencies, refreshed compatible frontend packages, and
  updated React and React DOM to 19.2.7.

## 2026-06-09

- Hardened the Poe client rate limiter to reject invalid limits and recheck
  token state after sleeping before allowing another upstream request.
- Omitted raw Poe model validation response bodies from logs and recorded a
  length summary instead.
- Rejected non-string story validator `characters`/`tags` metadata in both
  full and quick validation.
- Rejected scalar or mixed-type uploader `characters`/`tags` metadata before
  Hugging Face dataset record creation, and exposed `make lint`/`make build`
  aliases for the offline baseline.
- Aligned quick story validation with the full mapping-shaped frontmatter
  parser and added regression coverage.
- Rejected non-mapping YAML story frontmatter at parse time and added unit and
  baseline coverage for malformed metadata.
- Stopped logging raw Poe response bodies on Python client parse and HTTP error
  paths.
- Added a response-length summary helper, unit coverage, and baseline guard for
  the Poe logging boundary.
- Rejected non-mapping story frontmatter in the Hugging Face uploader before
  dataset record creation.

## 2026-06-08

- Added an offline maintenance baseline with `make check` and `scripts/check-baseline.sh`.
- Added offline unit tests for story validation, Poe model configuration, prompt shape, and diversity selection of unused characters/settings.
- Hardened the Next.js Modal proxy to require a configured HTTPS endpoint with a hostname, trim server-side env values, avoid raw upstream content logging, and use the Fable Flux served model name by default.
- Split the story page into a dynamic server wrapper and client component so the stable `next build` production path succeeds.
- Updated environment examples, setup script output, frontend docs, and deployment notes for `POE_API_KEY`, `HF_TOKEN`, `MODAL_API_KEY`, `MODAL_API_URL`, and `MODAL_MODEL`.
- Added ignore rules for local secrets, Python caches, virtual environments, logs, and generated runtime output.
