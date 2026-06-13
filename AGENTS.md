# AGENTS.md

## Repository purpose

Fable Flux is an AI-assisted educational story pipeline. The repository contains Python tools for generating and validating children's educational stories, Hugging Face dataset upload helpers, Modal/vLLM serving configuration, and a Next.js frontend that proxies story requests to a Modal-hosted model.

## Project structure

- `Makefile` - repository verification targets
- `scripts` - baseline checks and helper scripts
- `docs` - plans, notes, and generated README assets
- `src` - primary source code
- `tests` - tests and fixtures
- `requirements.txt` - Python runtime dependencies

## Development commands

- Install dependencies: `python3 -m pip install -r requirements.txt`; `python3 -m pip install -e .`
- Full baseline: `make check`
- Lint/static checks: `make lint`
- Tests: `make test`
- Build: `make build`
- If a command above skips because a platform toolchain is missing, verify on a machine with that SDK before claiming platform behavior is tested.

## Coding conventions

- Prefer dependency-free tests or stdlib checks when legacy packages are unavailable.

## Testing guidance

- Test-related files detected: `front-end/test-env.js`, `tests/`, `tests/test_diversity_tracker.py`, `tests/test_huggingface_uploader.py`, `tests/test_poe_client.py`, `tests/test_story_validator.py`
- Start with the narrowest relevant test or Make target, then run `make check` before handing off if the change is not documentation-only.
- Keep README verification notes in sync when commands, fixtures, or supported toolchains change.

## PR / change guidance

- Keep diffs focused on the requested repository and avoid unrelated modernization or formatting churn.
- Preserve public APIs, sample behavior, file formats, and documented environment variables unless the task explicitly changes them.
- Update tests, README notes, or docs/plans when behavior, security posture, or validation commands change.
- Call out skipped platform validation, legacy toolchain assumptions, and any risky files touched in the final summary.

## Safety and gotchas

- Notebook outputs can be large or noisy; clear unnecessary execution output before committing notebooks.
- Keep `POE_API_KEY`, `HF_TOKEN`, `MODAL_API_KEY`, and service-specific values in local environment files only. Checked-in examples must remain placeholders.
- Keep hosted checks offline. Tests and CI must not call Poe, Hugging Face, Modal, publish datasets, or generate billable stories.
- Do not log prompts, generated stories, user input, or raw upstream response bodies. Preserve the existing length-only Poe response summaries.
- Story and uploader frontmatter must remain mappings, and `characters` and `tags` must remain non-empty lists of non-empty strings before validation or publishing.
- Poe rate limits must stay positive and recheck token state after sleeping. Retries must sleep once per actual retry and return immediately after the retry budget is exhausted.
- The frontend proxy must use server-side environment configuration, require an HTTPS Modal endpoint with a hostname, bound prompt length, and avoid raw generated-content logs.
- Treat `data/stories`, `output`, and `logs` as potentially sensitive generated content. Do not commit new generated stories or runtime logs during maintenance work.
- Follow `docs/publishing-serving-ownership.md` before any Hugging Face publication or Modal deployment. Preserve explicit owner/reviewer evidence, provenance, safety/privacy review, least-privilege secret storage, rollback, and incident rotation boundaries; offline CI does not authorize a release.

## Agent workflow

1. Inspect the README, Makefile, manifests, and the files directly related to the request.
2. Make the smallest source or docs change that satisfies the task; avoid generated, vendored, or local-environment files unless required.
3. Run the narrowest useful validation first, then `make check` or the documented package/platform gate when available.
4. If a required SDK, service credential, or external runtime is unavailable, record the skipped command and why.
5. Summarize changed files, commands run, and remaining risks or follow-up validation.
