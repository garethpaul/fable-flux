# aiohttp 3.14.1 Security Refresh

## Status: Completed

## Priority

P1 dependency security. GitHub reports eight open advisories against the
repository's `aiohttp==3.14.0` CI pin. The advisories affect aiohttp versions
through 3.14.0 and identify 3.14.1 as the first patched release.

## Current-State Findings

- `requirements-ci.txt` pins aiohttp 3.14.0 for the maintained Python test
  matrix.
- The baseline checker requires that exact vulnerable pin, so changing only
  the dependency file would fail the repository contract.
- Both canonical events currently pass Python 3.10, 3.12, and 3.14 plus the
  frontend Node 20, 22, and 24 matrix.
- `requirements.txt` and the setup helper still accept aiohttp 3.8.0, so
  upgrading only the CI pin would leave fresh or pre-existing runtime
  environments able to satisfy the project contract with vulnerable releases.

## Approach

- Upgrade the exact CI dependency pin from aiohttp 3.14.0 to 3.14.1.
- Raise the runtime dependency floor to aiohttp 3.14.1 in both maintained
  dependency declarations.
- Update the baseline dependency contract to reject restoration of the
  vulnerable version and require this completed security plan.
- Preserve Python and frontend workflow matrices and application behavior
  while narrowing the runtime dependency floor to patched releases.
- Record exact local and hosted evidence after the refreshed dependency stack
  passes.

## Implementation Units

### U1: Refresh the maintained aiohttp pin

Update `requirements-ci.txt` to the first patched 3.14.1 release while leaving
the remaining offline CI dependency set unchanged. Raise the matching runtime
floor in `requirements.txt` and the setup helper so vulnerable versions no
longer satisfy the project contract.

Test scenarios:
- A clean pinned install resolves aiohttp 3.14.1 on the supported Python
  runtime.
- Both runtime dependency declarations reject aiohttp releases before 3.14.1.
- Dependency auditing reports no known vulnerability in the exact CI set.

### U2: Enforce the security boundary

Update `scripts/check-baseline.sh` so the complete gate requires aiohttp 3.14.1
and retains durable completion evidence in this plan.

Test scenarios:
- The unchanged repository passes the baseline from repository and external
  working directories.
- Isolated mutations to the aiohttp version, plan status, and recorded
  verification evidence are rejected.

## Verification

- Install the exact CI dependency set in an isolated environment and audit it.
- Run the complete repository gate from repository and external directories.
- Run the supported hosted Python/frontend matrices on push and pull request.
- Audit the intended diff, generated artifacts, credentials, file modes,
  conflict markers, and whitespace before committing.

## Scope Boundaries

- Do not change application request behavior, Poe/Modal integrations, frontend
  dependencies, or workflow matrices.
- Do not dismiss or suppress Dependabot alerts; resolve them through the first
  patched package release.
- Keep PR #14 and its predecessors open and preserve base-first ordering.

## Success Criteria

- `requirements-ci.txt` pins aiohttp 3.14.1.
- Runtime dependency guidance requires aiohttp 3.14.1 or newer.
- The exact dependency audit reports no known vulnerabilities.
- Repository, external-directory, push, and pull-request gates pass without
  weakening coverage.
- The eight aiohttp Dependabot alerts close on the exact new head or remain
  truthfully recorded if GitHub has not yet refreshed them.

## References

- [aiohttp security advisories](https://github.com/aio-libs/aiohttp/security/advisories)
- [Repository Dependabot alert #8](https://github.com/garethpaul/fable-flux/security/dependabot/8)

## Verification Completed

- An isolated Python 3.12 environment installed `aiohttp==3.14.1`, PyYAML
  6.0.3, and `pip-audit==2.10.0` from the maintained CI requirements.
- The exact dependency audit reported no known vulnerabilities.
- All 32 backend tests passed with the refreshed aiohttp release.
- Frontend lockfile installation, lint, the Next.js 16.2.9 production build,
  and the moderate-severity npm audit passed with zero vulnerabilities.
- The complete repository and external-working-directory `make check` gates
  passed, including frontend lint when dependencies were installed.
- Six isolated hostile mutations were rejected across the exact and runtime
  aiohttp floors, hosted audit step, completed plan status, and
  no-vulnerability evidence.
- Exact diff, generated-artifact, credential, mode, conflict-marker, and
  whitespace audits passed before the implementation commit.
- Hosted push run `27709947843` and pull-request run `27709983810` passed all
  12 Python and frontend matrix jobs at implementation head
  `5602a07d51813644d90ef7a86393a31ce827db7e`.
- The eight aiohttp Dependabot alerts remain open against the default branch
  until the stacked remediation is integrated; the exact branch audit is
  clean, and no alert dismissal or suppression is used.
