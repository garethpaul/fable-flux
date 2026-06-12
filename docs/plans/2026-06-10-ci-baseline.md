# CI Baseline

status: completed

## Context

The repository had a local offline `make check` baseline for Python generation,
validation, Poe rate-limit behavior, and frontend proxy static checks, but no
hosted workflow ran it for pushes and pull requests.

## Changes

- Added a GitHub Actions workflow that installs Python 3.12 and the minimal
  offline test dependencies before running `make check`.
- Extended the shell baseline and docs so the hosted CI path stays visible.

## Verification

- `make check`
