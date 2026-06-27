# Lazy Package Exports

status: completed

## Context

Python executes `src/__init__.py` before loading a requested `src.*` submodule.
The package eagerly imported every convenience export, so importing the
stdlib-only diversity tracker also required `aiohttp` through the story
generator and Poe client.

## Design

Keep the existing five public package names in `__all__`, map each name to its
owning module, and resolve it through module `__getattr__` only on first access.
Cache the resolved value in package globals so later access has normal import
cost and identity. Unknown names continue to raise `AttributeError`.

This preserves `from src import DiversityTracker` and the other convenience
imports without making unrelated submodules depend on optional clients.

## Verification

- The focused regression failed before implementation with missing `aiohttp`.
- Package and diversity tests passed on a clean host without `aiohttp`.
- Story validator and uploader tests passed with documented optional fallbacks.
- An isolated environment installed exact `requirements-ci.txt` pins and
  `make check` passed all 36 backend tests.
- Frontend lint was skipped locally because `node_modules` was not installed;
  hosted Node matrices remain required.
- `git diff --check` passed.

## Scope

This changes import timing only. Accessing a network, generation, or publishing
export still requires that export's declared dependencies.
