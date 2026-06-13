## Fable Flux Vision

This document explains the current state and direction of the project.
Project overview and developer docs: [`README.md`](README.md)

Fable Flux is an AI-powered educational story generation system for children's
stories. It includes Python story generation, dataset publishing, model
fine-tuning notes, Modal/vLLM serving, and a Next.js frontend.

The goal is to create a high-quality, safe, and inspectable pipeline for
generating personalized educational stories. Project overview and setup details
live in [`README.md`](README.md).

The current focus is:

Priority:

- Preserve the end-to-end story generation pipeline and frontend experience
- Keep API keys, Hugging Face tokens, and Poe/OpenAI credentials out of git
- Maintain quality controls for story length, reading level, sentiment, and
  educational value
- Keep generated datasets and model artifacts traceable to configuration

Current baseline:

- Tracked local Python virtualenv and bytecode cache artifacts have been
  removed.
- `.gitignore` excludes generated environments, Python caches, frontend
  installs, logs, and local generated output.
- `scripts/check-baseline.sh` compiles app-owned Python sources and verifies
  generated environments are not tracked.
- Diversity selection accounts for unused characters and settings before
  reusing previously selected story elements.
- Story validation rejects non-mapping YAML frontmatter in quick and full
  validation before content quality checks run.
- Story validation requires `characters` and `tags` metadata to be non-empty
  string lists before quick or full validation passes.
- Dataset upload parsing rejects non-mapping YAML frontmatter before building
  Hugging Face records, and keeps `characters` and `tags` as non-empty string
  lists before JSONL export.
- `make lint`, `make test`, and `make build` all run the offline baseline while
  the project has no narrower installed lint/build toolchain.
- The frontend proxy requires environment-backed Modal configuration with an
  HTTPS hostname and server-side prompt bounds.
- Modal generation requests have a 30-second server-side deadline and generic
  timeout failures.
- The Python Poe client avoids logging raw upstream response bodies and records
  response length for failed parse/HTTP paths.
- Poe model validation response bodies are also omitted from logs and summarized
  by length.
- Poe model preflight accepts only HTTP 200 as proof of accessibility and fails
  closed for all other statuses.
- The Poe client rate limiter validates positive limits and rechecks token
  state after sleeps before permitting the next upstream request.
- Poe retries use one failure-specific backoff delay per actual retry and
  return immediately when the configured retry budget is exhausted.
- Local Python and frontend environments are recreated from `requirements.txt`
  and `front-end/package-lock.json`.
- GitHub Actions runs the offline Python baseline and clean frontend
  lint/build/audit checks across active Python and Node releases without
  persisting checkout credentials.

Next priorities:

- Add API route tests and broaden retry/error-path coverage
- Document dataset publishing and model-serving ownership boundaries
- Keep frontend API proxy behavior secure and user-friendly
- Keep the hosted GitHub Actions baseline aligned with local offline checks
- Keep the pinned Ubuntu runner deliberate across both language matrices
- Add evaluation notes for story safety, age appropriateness, and educational fit

Contribution rules:

- One PR = one focused generation, validation, serving, frontend, or docs change.
- Run `scripts/check-baseline.sh` before pushing repository hygiene or Python
  pipeline changes.
- Run the relevant Python checks and frontend `npm run lint`/`npm run build`
  before pushing touched areas.
- Document changes to prompts, model choices, datasets, or API contracts.
- Keep generated outputs out of source control unless they are intentional fixtures.

## Security And Responsible Use

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)

Children's educational content needs careful safety boundaries. Generated stories
should avoid inappropriate content, unsafe advice, and hidden data collection.

API keys and model-serving credentials must remain in environment configuration.
Prompts, generated stories, and user inputs should not be logged or published
without a clear purpose and consent.

## What We Will Not Merge (For Now)

- Committed API tokens, model credentials, or private generated datasets
- Story-generation changes without validation or safety notes
- Frontend proxy behavior that exposes server-side keys
- Model or dataset claims without reproducible configuration

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
