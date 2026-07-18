# Test Assertion Mechanism Control

status: completed

## Context

`make check` runs the real unittest suite and greps `src/` and `tests/` for
guard source and test-case names. Both observe *text* and *outcomes*. Neither
observes that the suite's assertions still assert.

`unittest discover` imports every `tests/test*.py` module in sorted order before
running any case, so a module sorting first can rebind
`unittest.TestCase.assert*` to no-ops that affect every subsequently-run case.
Nothing pinned the assertion mechanism, and `tests/` was not closed-world, so
this needed no edit to any pinned file:

- With `tests/test_aaa_shadow.py` added and a real fail-open defect planted in
  `StoryValidator._validate_string_list_field` (its `def` line and the
  `non-empty list of strings` diagnostic left byte-identical, so every pinned
  literal still matched), the suite reported `Ran 36 tests ... OK` and the gate
  printed `fable-flux maintenance baseline checks passed` at exit 0.
- The same defect *without* the added module was correctly caught at exit 2,
  confirming the suite is real and load-bearing and that the added module — not
  the defect — was what went unobserved.

The workflow directory was already closed-world via a `find` inventory, which is
the right idiom; it was one directory short of covering `tests/`.

Every existing `hostile mutations were rejected` string the gate enforces is
prose recorded in a plan document. The gate pinned the *claim* that mutation
testing happened; no planted-defect control ran.

## Design

Two layers, in the order the gate reaches them.

`tests/` becomes closed-world through the same `find` inventory idiom already
used for `.github/workflows`, so an added module is named and rejected.

An inventory alone cannot stop an in-file rebind that keeps the directory
closed-world, so `scripts/test-security-mutations.py` adds an out-of-band
planted-defect control. For each of seven real fail-open defects it stages
`src/` and `tests/` to a scratch tree, plants one defect, and runs the *real*
suite, requiring the suite to go red. A clean-tree control runs first: the
unmutated copy must pass, otherwise "every mutation was detected" could not be
distinguished from a universally broken suite. Each mutation asserts its anchor
matches exactly once, so a fixture that drifts from the source fails loudly
instead of silently planting nothing.

The construction is self-defending rather than pinned. A neutered assertion
mechanism makes the suite pass unconditionally, so *every* mutation survives, so
the control fails. Weakening the mutation table has the same effect: a defect the
suite cannot catch is a survivor. The detector cannot be disabled without
tripping it.

## Verification

- Clean-tree `make check` passed at exit 0 with all 36 backend tests and all
  seven planted defects detected.
- The same gate passed from an external working directory (`make -f
  /tmp/.../Makefile check`), preserving the location-independent contract.
- Added-module attack (`tests/test_aaa_shadow.py` plus the real fail-open
  defect): the suite still reported `OK`, and the test inventory rejected the
  run at exit 2, naming `tests/test_aaa_shadow.py`.
- In-file rebind attack (assertion no-ops appended to the pinned
  `tests/test_diversity_tracker.py`, directory left closed-world, no source
  defect): the clean-tree control passed and all seven mutations SURVIVED, so the
  control failed at exit 2 by construction.
- The control immediately found a real coverage gap on the base branch:
  `test_parse_story_file_rejects_non_string_sequence_items` asserted only
  `assertIsNone`, which `parse_story_file`'s outer `except Exception` also
  returns when a removed guard lets an incidental `AttributeError` escape. The
  test passed with the guard deleted. It now asserts the guard's own
  `must contain only non-empty strings` diagnostic, so its removal is
  detectable. The pinned test name was preserved.
- `git diff --check` passed.

## Scope

This adds verification only; no runtime or generation behavior changes. Local
frontend lint remained skipped because `node_modules` was not installed, so
hosted Node matrices remain required. The control staged `src/` and `tests/`
because those are the trees the suite imports. It was exercised on Python 3.12;
the hosted 3.10, 3.12, and 3.14 matrices remain the authority. No live Poe,
Hugging Face, or Modal request was performed, and no billable story was
generated.
