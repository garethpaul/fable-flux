# Fable Flux Safety Baseline

Date: 2026-06-08

## Goals

- Make the repository's actual generation, upload, serving, and frontend entry points clear.
- Keep Poe, Hugging Face, Modal, and model-serving secrets out of source control.
- Add offline checks for validation and prompt behavior without calling external services.
- Harden the frontend proxy so it does not depend on stale hardcoded model settings or log raw model output.

## Completed Scope

- Added offline Python tests for `StoryValidator`, `PoeClient` prompt/model configuration, and `DiversityTracker` least-used selection.
- Added `scripts/check-baseline.sh` and `Makefile` targets for repeatable local verification.
- Updated the frontend API route to require `MODAL_API_URL`, validate HTTPS with `URL`, trim env values, and use `MODAL_MODEL` with the Fable Flux served model as the default.
- Replaced generic README content with project-specific setup, generation, upload, frontend, verification, and security notes.
- Updated environment examples and setup-generated templates to avoid stale Poe-only frontend guidance.
- Added ignore rules for local secrets, caches, venvs, logs, and generated runtime artifacts.

## Follow-Ups

- Add API route unit tests or integration tests once the frontend test runner is chosen.
- Decide whether the already tracked generated stories under `output/generated_stories/` are canonical dataset artifacts or should move to a release/data artifact boundary.
- Add a documented story-safety evaluation rubric for generated content review before dataset publication.
