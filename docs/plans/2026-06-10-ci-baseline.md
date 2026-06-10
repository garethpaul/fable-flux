# CI Baseline

status: completed

## Context

The repository had a local offline `make check` baseline for Python generation,
validation, Poe rate-limit behavior, and frontend proxy static checks, but no
hosted workflow ran it for pushes and pull requests.

## Changes

- Added a GitHub Actions Python 3.10/3.12/3.14 matrix that installs pinned
  minimal offline dependencies before running `make check`.
- Added a Node 20/22/24 matrix that performs `npm ci`, frontend linting,
  production builds, and moderate-severity npm audits.
- Pinned workflow actions by commit, granted read-only repository access,
  enabled stale-run cancellation, and bounded every job.
- Refreshed compatible frontend dependencies and updated React/React DOM to
  19.2.7 while retaining the established Next 15 production build.
- Extended the shell baseline and docs so the hosted CI path stays visible.

## Verification

- Clean Python installs and `make check` on Python 3.10, 3.12, and 3.14
- Clean frontend lint/build/audit runs on Node 20, 22, and 24
