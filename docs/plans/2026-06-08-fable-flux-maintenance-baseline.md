---
title: Fable Flux maintenance baseline
date: 2026-06-08
status: completed
execution: code
---

## Context

Fable Flux is a Python and Next.js project for generating personalized
children's educational stories, publishing datasets, serving a fine-tuned model,
and providing a frontend story prompt flow. The repository contains generated
story data and previously included generated Python environment artifacts.

## Goals

- Keep story validation and diversity behavior testable without Poe, Modal, or
  Hugging Face credentials.
- Fix diversity balancing so unused characters and settings are not starved.
- Require frontend Modal proxy configuration from environment variables,
  reject malformed endpoints, and reject unsafe or empty prompts.
- Remove tracked virtualenv and Python bytecode artifacts.
- Add a repeatable baseline command that checks Python source, config/data
  integrity, environment examples, frontend proxy guardrails, and docs.

## Scope Boundaries

- Do not regenerate or bulk-edit the existing story corpus in this pass.
- Do not call Poe, Modal, Hugging Face, or model-serving endpoints in default
  verification.
- Do not redesign the frontend.
- Do not change the generated story payload contract.

## Implementation

- `DiversityTracker` includes unseen characters and settings when selecting
  least-used values.
- `tests/` covers diversity balancing and offline `StoryValidator` behavior.
- The frontend API route requires `MODAL_API_KEY` and a parseable HTTPS
  `MODAL_API_URL` with a hostname, bounds prompt length, and avoids logging raw
  generated story content.
- `.gitignore` excludes local env files, virtualenvs, bytecode, frontend build
  outputs, and dependency directories.
- `scripts/check-baseline.sh` and `Makefile` expose the static/offline gate.

## Verification

- `make check`
- `python3 -m pytest tests`
- `git diff --check`
