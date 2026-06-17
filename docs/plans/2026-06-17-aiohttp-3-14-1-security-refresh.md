# aiohttp 3.14.1 Security Refresh

## Status: Planned

## Priority

P0 dependency security. GitHub reports eight open advisories against the
repository's `aiohttp==3.14.0` CI pin. The advisories affect aiohttp versions
through 3.14.0 and identify 3.14.1 as the first patched release.

## Current-State Findings

- `requirements-ci.txt` pins aiohttp 3.14.0 for the maintained Python test
  matrix.
- The baseline checker requires that exact vulnerable pin, so changing only
  the dependency file would fail the repository contract.
- Both canonical events currently pass Python 3.10, 3.12, and 3.14 plus the
  frontend Node 20, 22, and 24 matrix.
- The application dependency floor remains `aiohttp>=3.8.0`; this change is a
  maintained CI/test-stack refresh rather than a new runtime compatibility
  policy.

## Approach

- Upgrade the exact CI dependency pin from aiohttp 3.14.0 to 3.14.1.
- Update the baseline dependency contract to reject restoration of the
  vulnerable version and require this completed security plan.
- Preserve Python and frontend workflow matrices, application behavior, and
  the existing broad runtime dependency floor.
- Record exact local and hosted evidence after the refreshed dependency stack
  passes.

## Implementation Units

### U1: Refresh the maintained aiohttp pin

Update `requirements-ci.txt` to the first patched 3.14.1 release while leaving
the remaining offline CI dependency set unchanged.

Test scenarios:
- A clean pinned install resolves aiohttp 3.14.1 on the supported Python
  runtime.
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
  dependencies, workflow matrices, or the broad runtime dependency floor.
- Do not dismiss or suppress Dependabot alerts; resolve them through the first
  patched package release.
- Keep PR #14 and its predecessors open and preserve base-first ordering.

## Success Criteria

- `requirements-ci.txt` pins aiohttp 3.14.1.
- The exact dependency audit reports no known vulnerabilities.
- Repository, external-directory, push, and pull-request gates pass without
  weakening coverage.
- The eight aiohttp Dependabot alerts close on the exact new head or remain
  truthfully recorded if GitHub has not yet refreshed them.

## References

- [aiohttp security advisories](https://github.com/aio-libs/aiohttp/security/advisories)
- [Repository Dependabot alert #8](https://github.com/garethpaul/fable-flux/security/dependabot/8)
