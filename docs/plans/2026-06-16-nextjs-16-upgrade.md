# Next.js 16 Frontend Upgrade

## Status: Completed

## Priority

P1 dependency maintenance. The frontend is pinned to Next.js 15.5 while the
current stable release is Next.js 16.2. The repository already runs Node 20,
22, and 24 in hosted checks, so it satisfies the Next.js 16 Node 20.9 minimum
without narrowing the supported matrix.

## Current-State Findings

- The app does not use synchronous request APIs, middleware, parallel routes,
  legacy image components, custom webpack configuration, or experimental PPR.
- React and React DOM are already current at 19.2.7.
- The `next dev --turbopack` flag is redundant because Turbopack is the Next.js
  16 default.
- The production build uses an undocumented worker environment variable and
  the removed `--no-lint` compatibility flag even though lint already runs as
  a separate maintained gate.

## Approach

- Upgrade `next` and `eslint-config-next` together to the current 16.2 line and
  regenerate `front-end/package-lock.json` from the committed manifest.
- Preserve the current React versions and all application behavior.
- Simplify development and build scripts to supported Next.js 16 commands.
- Declare the Node 20.9 runtime floor in `front-end/package.json` while retaining
  hosted Node 20, 22, and 24 coverage.
- Extend `scripts/check-baseline.sh` with version, runtime, script, plan, and
  documentation contracts that reject a partial or regressed migration.
- Synchronize contributor, README, security, vision, and changelog guidance.

## Verification

- Install exactly from `front-end/package-lock.json`.
- Run frontend lint, production build, and moderate-severity dependency audit.
- Run repository-root and external-directory `make check` with frontend
  dependencies present.
- Reject isolated mutations to the framework version, ESLint peer version,
  Node floor, supported scripts, documentation, and completed-plan evidence.
- Audit the exact diff, generated artifacts, credentials, conflict markers,
  modes, binaries, sizes, and whitespace.

## Scope Boundaries

- Do not change story generation, Modal/Poe request handling, UI composition,
  publishing behavior, workflow matrices, React versions, or Python packages.
- Do not introduce experimental Next.js features or weaken lint/build/audit
  coverage.
- Keep PR #13 and its predecessors open and preserve base-first ordering.

## Success Criteria

- Clean installs resolve Next.js and `eslint-config-next` 16.2.x together.
- `npm run lint`, `npm run build`, and `npm run audit` pass on the upgraded
  lockfile.
- The complete repository gate passes from repository and external working
  directories.
- Existing frontend behavior and optimized image rendering remain unchanged.

## References

- [Next.js 16 upgrade guide](https://nextjs.org/docs/app/guides/upgrading/version-16)
- [Next.js 16.2 release](https://nextjs.org/blog/next-16-2)

## Verification Completed

- Next.js and `eslint-config-next` 16.2.9 install together from the committed
  lockfile with React and React DOM remaining at 19.2.7.
- Native flat ESLint configuration passed after removing the legacy
  compatibility adapter. The upgraded rules also identified and eliminated a
  synchronous effect-state update in browser story storage.
- The Next.js 16 production Turbopack build passed with supported scripts,
  generated route types, and the React automatic JSX runtime.
- `npm audit --audit-level=moderate` reported zero vulnerabilities.
- Repository-root and external-directory `make check` passed the 32-test
  backend gate plus frontend lint under the upgraded dependency tree.
- Seven isolated hostile mutations were rejected across framework and ESLint
  versions, the Node floor, build scripts, storage hydration, guidance, and
  completed-plan evidence.
- Exact diff, generated artifact, credential, conflict, mode, binary, size, and
  whitespace audits passed.
- No live Modal, Poe, Hugging Face, or billable generation request was performed.
