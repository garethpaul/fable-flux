# Dataset Publishing And Model Serving Ownership

This runbook defines who approves and records Hugging Face dataset publication
and Modal model-serving changes. It does not authorize a release by itself.

## Status And Offline Limit

The repository maintenance gate is offline. It does not publish datasets,
deploy Modal applications, call Poe, generate billable stories, verify service
account ownership, prove endpoint reachability, or assess live story quality.
Record those outcomes separately for the exact released commit and artifact.

## Roles And Approval

- The repository maintainer owns source review, protected-branch state, release
  commit selection, and confirmation that local and hosted checks are green.
- The dataset publisher owns the Hugging Face namespace, least-privilege
  `HF_TOKEN`, dataset card, target visibility, upload command, and revision.
- The model-serving operator owns the Modal workspace, least-privilege
  `MODAL_API_KEY`, deployment configuration, endpoint access, billing, and
  rollback execution.
- The release reviewer independently verifies provenance, safety/privacy review,
  target namespace/workspace, and rollback readiness before a public or billable
  publication or deployment.

One person may perform the maintainer, publisher, and operator roles in a small
project, but the independent reviewer must be a different person for a public or
billable release. The record must identify each responsibility and preserve an
explicit review decision separate from possession of a publishing credential.

## Required Release Evidence

Record the source commit SHA, configuration revision, input dataset provenance,
validation commands and results, responsible owners, independent reviewer,
target Hugging Face namespace or Modal workspace, artifact/model revision,
release timestamp, visibility, and rollback target. Use identifiers and hashes;
do not attach tokens, prompts, generated stories, or private dataset rows.

## Dataset Publication

1. The repository maintainer selects the exact green commit and confirms that
   generated stories and local logs are not accidentally staged.
2. The dataset publisher verifies mapping/list metadata, provenance, licenses,
   target namespace, visibility, dataset card, and exclusion of credentials or
   private content from the JSONL artifact.
3. The release reviewer records explicit approval after child-safety, age
   appropriateness, educational-fit, privacy, and sampling review.
4. The dataset publisher uses a least-privilege token from an approved secret
   store, publishes once, and records the immutable dataset revision or commit.
5. Postflight review samples the published artifact, verifies expected metadata
   and visibility, and removes or deprecates the revision if evidence diverges.

## Model Serving

1. The repository maintainer identifies the reviewed model/configuration commit
   and the dataset revision used to produce it.
2. The model-serving operator verifies the Modal workspace, model identifier,
   resource and billing limits, server-side secrets, endpoint access policy, and
   rollback deployment before changing live service state.
3. The release reviewer records explicit approval after safety, privacy, prompt,
   output-format, timeout, and representative age-appropriate story review.
4. The operator deploys with platform-managed secrets, records the deployment
   revision and endpoint owner, then runs bounded synthetic smoke checks without
   logging prompts, generated stories, user input, or raw response bodies.
5. Postflight review verifies availability, generic failure handling, cost/error
   signals, and rollback readiness without placing service credentials in git.

## Credentials And Sensitive Data

Keep `HF_TOKEN`, `MODAL_API_KEY`, `POE_API_KEY`, endpoint credentials, and
service-specific values in approved local or platform secret stores. Use the
least privilege and shortest practical lifetime. Never place them in git,
command transcripts, CI output, issue attachments, screenshots, generated
datasets, prompts, stories, or application logs.

## Rollback And Incidents

For a bad dataset release, make the affected revision private, deprecated, or
removed as platform policy permits; preserve a redacted incident record and
restore the last reviewed revision. For a serving issue, disable or roll back
the deployment, revoke exposed endpoint access, and restore the last reviewed
configuration before resuming traffic.

If a credential or private artifact may have been exposed, stop publication or
serving, rotate the affected token, review platform audit logs, remove public
copies where possible, document scope without reproducing the secret/data, and
notify the repository maintainer, service owner, and reviewer.
