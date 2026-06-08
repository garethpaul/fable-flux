## Fable Flux Vision

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

Next priorities:

- Strengthen tests around prompt construction, validation, and retry behavior
- Document dataset publishing and model-serving ownership boundaries
- Keep frontend API proxy behavior secure and user-friendly
- Add evaluation notes for story safety, age appropriateness, and educational fit

Contribution rules:

- One PR = one focused generation, validation, serving, frontend, or docs change.
- Run the relevant Python checks and frontend `npm run lint`/`npm run build`
  before pushing touched areas.
- Document changes to prompts, model choices, datasets, or API contracts.
- Keep generated outputs out of source control unless they are intentional fixtures.

## Security And Responsible Use

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
