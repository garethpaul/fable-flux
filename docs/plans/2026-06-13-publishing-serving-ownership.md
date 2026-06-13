---
title: Dataset Publishing And Model Serving Ownership
type: operations
status: completed
date: 2026-06-13
---

# Dataset Publishing And Model Serving Ownership

## Summary

Define accountable, reviewable boundaries for Hugging Face dataset publication
and Modal model serving without placing credentials, live publishing, billable
generation, or deployment actions in the offline maintenance gate.

## Requirements

- R1. Separate repository maintainer, dataset publisher, model-serving operator,
  and reviewer responsibilities; do not imply that one credential holder may
  unilaterally approve and publish every artifact.
- R2. Require source commit, configuration, input provenance, validation result,
  target namespace, artifact revision, and responsible owner for publication or
  deployment evidence.
- R3. Require least-privilege `HF_TOKEN`, `MODAL_API_KEY`, and related secrets to
  remain in approved local or platform secret stores and never in git, logs,
  issue attachments, or generated datasets.
- R4. Define preflight, explicit approval, publish/deploy, postflight, rollback,
  incident, and credential-rotation responsibilities.
- R5. Keep child-safety, age-appropriateness, educational-fit, prompt/story log,
  and dataset privacy review explicit before release.
- R6. State that CI remains offline and cannot prove live Hugging Face ownership,
  Modal deployment, endpoint reachability, billing, or generated story quality.
- R7. Enforce the runbook sections, core ownership assertions, completed local
  verification evidence, and roadmap update in the maintenance gate.

## Non-Goals

- Publishing a dataset, pushing a model, deploying Modal, or generating stories.
- Adding, rotating, validating, or exposing real service credentials.
- Changing uploader, serving, frontend, prompt, dataset, or model behavior.
- Claiming live service evidence from local or hosted offline checks.

## Implementation Units

### 1. Ownership Runbook

Files: `docs/publishing-serving-ownership.md`

- Define roles, required evidence, release sequence, rollback, incidents, and
  offline verification limits.

### 2. Maintenance Contract

Files: `scripts/check-baseline.sh`, this plan

- Require the runbook and section-scoped ownership, credential, provenance,
  safety, rollback, and limitation assertions.
- Reject isolated hostile mutations for each high-risk boundary.

### 3. Project Guidance

Files: `README.md`, `AGENTS.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`

- Link the runbook, preserve offline CI boundaries, and move the completed
  ownership-documentation item out of next priorities.

## Verification Plan

- Run the full Python and frontend maintenance gate without network services.
- Apply isolated mutations to role separation, provenance, least privilege,
  explicit approval, safety review, rollback, incident rotation, offline limits,
  roadmap, and plan status; require each mutation to fail.
- Run shell syntax, `git diff --check`, exact-path, manifest/workflow, secret-like
  addition, and generated-artifact checks.
- Take one bounded exact-head hosted snapshot after push; do not poll.

## Risks

- A runbook cannot enforce external organization permissions or service roles.
- Ownership names and platform procedures can drift unless release operators
  update the evidence for every publication or deployment.

## Verification

- An isolated full `make check` passed all 23 offline Python tests; frontend
  lint was explicitly skipped because this worktree has no installed
  `front-end/node_modules`.
- Eleven isolated hostile mutations were rejected for weakened independent
  review, distinct reviewer identity, provenance, secret lifetime, approval,
  child-safety, rollback, incident token rotation, offline limits, roadmap, and
  plan-status requirements.
- No Poe, Hugging Face, Modal, dataset publication, deployment, network request,
  billable generation, prompt, generated story, or real credential was used.
- Shell syntax, `git diff --check`, exact eight-path review, unchanged source,
  test, configuration, manifest, lockfile, workflow, and Makefile inspection,
  credential-value addition inspection, and generated-artifact inspection passed.
- The exact pushed head still requires the clean hosted offline Python and
  frontend matrices plus one bounded hosted snapshot.

## Work Completed

- Added accountable roles, explicit approval, release evidence, dataset and
  serving procedures, least-privilege credential handling, postflight review,
  rollback, and incident response.
- Added section-scoped maintenance contracts and updated project guidance while
  preserving the offline verification boundary.
