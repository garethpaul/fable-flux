---
title: Hosted Runner Pin
date: 2026-06-12
status: completed
execution: code
---

# Hosted Runner Pin

## Summary

Replace both `ubuntu-latest` jobs with the explicit `ubuntu-24.04` runner while
preserving the Python 3.10/3.12/3.14 and Node 20/22/24 matrices, credential-free
checkout, dependency installation, tests, frontend build, lint, and audit.

## Priority

`ubuntu-latest` can move to a different operating-system image independently of
the repository. An explicit image keeps both language matrices on the reviewed
host boundary and makes future runner upgrades deliberate.

## Requirements

- Run both canonical jobs on `ubuntu-24.04` and reject every
  `ubuntu-latest` occurrence.
- Require exactly two explicit runner declarations, one for each existing job.
- Preserve action pins, checkout credential settings, permissions, timeouts,
  matrices, commands, and workflow inventory.
- Keep Python, frontend, application, package, and test behavior unchanged.
- Record local, external-working-directory, hostile-mutation, and exact-head
  hosted verification truthfully.

## Work Completed

- Pinned the Python and frontend jobs to Ubuntu 24.04.
- Added exact workflow, plan, and repository-guidance contracts.

## Verification Completed

- Local and external-working-directory gates passed the offline Python tests,
  frontend lint, production build, and moderate npm audit.
- Workflow parsing, shell syntax, and `git diff --check` passed.
- Focused hostile mutations rejected either job returning to `ubuntu-latest`,
  alternate runner labels, missing runner declarations, extra workflow files,
  and incomplete plan or documentation evidence; all hostile mutations
  rejected.
- Exact-head hosted evidence remains pending until this successor is pushed.
