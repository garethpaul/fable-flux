# Compatible Frontend Lock Refresh

## Status: Completed

## Priority

P2 dependency maintenance. The maintained frontend manifest permits compatible
updates that are not yet represented in the lockfile: Tailwind CSS and its
PostCSS integration resolve to 4.3.0 instead of 4.3.1, and the Node 20 type
definitions resolve to 20.19.42 instead of 20.19.43.

## Current-State Findings

- The exact Next.js 16.2.9, React 19.2.7, React DOM 19.2.7, and
  `eslint-config-next` 16.2.9 compatibility boundary is already current.
- `@tailwindcss/postcss` and `tailwindcss` allow compatible 4.x updates, while
  `@types/node` intentionally remains on the maintained 20.x line.
- `npm outdated` reports ESLint 10, TypeScript 6, and Node type definitions 25
  as separate major-version migrations; they require dedicated compatibility
  work and are outside this refresh.
- The current lockfile installs, lints, builds, and audits cleanly across the
  Node 20, 22, and 24 hosted matrix.

## Approach

- Refresh only `front-end/package-lock.json` to resolve Tailwind CSS,
  `@tailwindcss/postcss`, and their platform packages at 4.3.1 and
  `@types/node` at 20.19.43.
- Preserve the existing manifest ranges and all exact framework pins.
- Extend the baseline gate with a structured lockfile contract that rejects
  stale compatible resolutions without relying on textual lockfile matching.
- Retain the existing Python and frontend validation matrices and record exact
  local and hosted evidence after the refreshed lock passes.

## Implementation Units

### U1: Refresh compatible lockfile resolutions

Update the npm lockfile through the package manager while leaving
`front-end/package.json` unchanged.

Test scenarios:
- A clean install resolves Tailwind CSS and `@tailwindcss/postcss` 4.3.1.
- A clean install resolves `@types/node` 20.19.43 while retaining the Node 20
  declaration boundary.
- Lint, production build, and the moderate-severity audit pass on Node 20, 22,
  and 24.

### U2: Enforce the compatible dependency boundary

Update `scripts/check-baseline.sh` so the complete gate parses the lockfile and
requires the intended versions while preserving the manifest's existing major
boundaries.

Test scenarios:
- The complete baseline passes from repository and external working
  directories.
- Isolated mutations to each compatible lock resolution, the manifest
  boundary, plan status, and verification evidence are rejected.

## Verification

- Install the refreshed lockfile on Node 20, 22, and 24, then run lint,
  production build, and the moderate-severity npm audit on each runtime.
- Run the complete repository gate from repository and external directories.
- Run mutation-sensitive checks for lockfile versions, manifest boundaries,
  completed plan status, and verification evidence.
- Audit the intended diff, generated artifacts, credentials, file modes,
  conflict markers, and whitespace before committing.
- Capture one bounded exact-head snapshot for push and pull-request checks.

## Scope Boundaries

- Do not change application behavior, UI output, Python dependencies, or
  workflow matrices.
- Do not migrate to ESLint 10, TypeScript 6, or Node type definitions 25 in
  this compatible refresh.
- Do not alter the exact Next.js, React, React DOM, or
  `eslint-config-next` versions.
- Keep PR #16 and its predecessors open and preserve base-first ordering.

## Success Criteria

- The lockfile resolves Tailwind CSS and `@tailwindcss/postcss` 4.3.1 and
  `@types/node` 20.19.43.
- `front-end/package.json` retains its existing compatible major ranges and
  exact framework pins.
- Repository, external-directory, push, and pull-request gates pass without
  weakening coverage.
- Dependency audits report no known moderate-or-higher npm vulnerabilities.

## Verification Completed

- Clean lockfile installs on Node 20.19.5, 22.22.2, and 24.16.0 resolved
  Tailwind CSS and `@tailwindcss/postcss` 4.3.1 plus `@types/node` 20.19.43.
- Frontend lint and the Next.js 16.2.9 production build passed on Node 20, 22,
  and 24.
- The moderate-severity npm audit reported zero vulnerabilities on each
  supported Node runtime.
- The baseline's 32 backend tests passed with the refreshed lockfile and
  structured dependency contract in place.
- Repository-root and external-directory `make check` passed, including all
  32 backend tests and the installed frontend lint gate.
- Ten isolated hostile mutations were rejected across the Tailwind PostCSS,
  Tailwind CSS, Tailwind node/oxide core, Node type, platform version,
  complete platform set, manifest-major, plan status, and completed
  audit-evidence contracts.
