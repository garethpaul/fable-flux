#!/usr/bin/env python3
"""Out-of-band planted-defect control for the fable-flux test suite.

`make check` runs the real unittest suite and greps for the presence of guard
source and test-case names. Both of those observe *text*. Neither observes that
the suite's assertions still assert: a suite whose assertion mechanism has been
neutered (an added `tests/test_*.py` module that rebinds
`unittest.TestCase.assert*`, or an in-file rebind) keeps every pinned literal
byte-identical, runs the same number of tests, reports OK, and ships real
defects at exit 0.

This harness closes that rung by construction rather than by pinning. For each
entry in MUTATIONS it copies `src/` and `tests/` to a scratch tree, plants one
real defect, and runs the *real* suite against the copy. A defect that does not
turn the suite red is a surviving mutation and fails this script.

The construction is self-defending: a neutered assertion mechanism makes the
suite pass unconditionally, so *every* mutation survives, so this harness fails
loudly. There is no way to disable the detector without tripping it.

A clean-tree control runs first: the unmutated copy must pass. Without it a
universally-broken suite (import error, missing dependency) would report every
mutation as "detected" and prove nothing.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Each mutation is a real fail-open defect in a guard the repository documents.
# `old` must appear exactly once in the target file so that the planted defect
# is unambiguous, and every pinned literal in scripts/check-baseline.sh is left
# byte-identical -- these defects are invisible to a text-only gate.
MUTATIONS = [
    {
        "name": "story validator accepts non-list sequence metadata",
        "path": "src/story_validator.py",
        "old": """    def _validate_string_list_field(self, values: Any) -> bool:
        return (
            isinstance(values, list)
            and len(values) > 0
            and all(isinstance(value, str) and value.strip() for value in values)
        )
""",
        "new": """    def _validate_string_list_field(self, values: Any) -> bool:
        return True
""",
    },
    {
        "name": "story validator accepts empty/non-string scalars",
        "path": "src/story_validator.py",
        "old": """    def _validate_non_empty_string(self, value: Any) -> bool:
        return isinstance(value, str) and bool(value.strip())
""",
        "new": """    def _validate_non_empty_string(self, value: Any) -> bool:
        return True
""",
    },
    {
        "name": "rate limiter accepts a non-positive rate",
        "path": "src/poe_client.py",
        "old": """        if rate <= 0:
            raise ValueError("Rate limit must be positive")
""",
        "new": """        if False:
            raise ValueError("Rate limit must be positive")
""",
    },
    {
        "name": "rate limiter accepts a non-positive period",
        "path": "src/poe_client.py",
        "old": """        if per <= 0:
            raise ValueError("Rate limit period must be positive")
""",
        "new": """        if False:
            raise ValueError("Rate limit period must be positive")
""",
    },
    {
        "name": "model validation fails open for non-200 responses",
        "path": "src/poe_client.py",
        "old": """            if response.status == 200:
                logging.debug(f"Model {model} is accessible")
                return True
""",
        "new": """            if response.status < 500:
                logging.debug(f"Model {model} is accessible")
                return True
""",
    },
    {
        "name": "uploader accepts non-list dataset sequence metadata",
        "path": "src/huggingface_uploader.py",
        "old": """        if not isinstance(values, list) or not values:
            logging.warning(f"Frontmatter {field} in {file_path} must be a non-empty list")
            return None
""",
        "new": """        if False:
            logging.warning(f"Frontmatter {field} in {file_path} must be a non-empty list")
            return None
""",
    },
    {
        "name": "uploader accepts non-string items inside sequence metadata",
        "path": "src/huggingface_uploader.py",
        "old": """            if not isinstance(value, str) or not value.strip():
                logging.warning(f"Frontmatter {field} in {file_path} must contain only non-empty strings")
                return None
""",
        "new": """            if False:
                logging.warning(f"Frontmatter {field} in {file_path} must contain only non-empty strings")
                return None
""",
    },
]


def stage(destination: Path) -> None:
    """Copy the tree the suite actually imports: src/ and tests/."""
    for relative in ("src", "tests"):
        shutil.copytree(
            ROOT / relative,
            destination / relative,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )


def plant(tree: Path, mutation: dict) -> None:
    """Apply one mutation, asserting it actually altered the staged fixture."""
    target = tree / mutation["path"]
    source = target.read_text()
    occurrences = source.count(mutation["old"])
    if occurrences != 1:
        raise SystemExit(
            f"Mutation fixture is stale: {mutation['name']!r} matched "
            f"{occurrences} times in {mutation['path']} (expected exactly 1). "
            "Update scripts/test-security-mutations.py to track the source."
        )
    mutated = source.replace(mutation["old"], mutation["new"])
    if mutated == source:
        raise SystemExit(f"Mutation did not alter the fixture: {mutation['name']}")
    target.write_text(mutated)


def run_suite(tree: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test*.py"],
        cwd=tree,
        capture_output=True,
        text=True,
    )


def main() -> int:
    # Clean-tree control: the unmutated suite must pass, otherwise "every
    # mutation was detected" would be indistinguishable from "the suite is
    # universally broken" and this harness would prove nothing.
    with tempfile.TemporaryDirectory() as scratch:
        control_tree = Path(scratch) / "control"
        control_tree.mkdir()
        stage(control_tree)
        control = run_suite(control_tree)
        if control.returncode != 0:
            print(
                "Clean-tree control failed: the unmutated suite must pass before "
                "mutation results mean anything.",
                file=sys.stderr,
            )
            print(control.stdout, file=sys.stderr)
            print(control.stderr, file=sys.stderr)
            return 2
    print(f"clean-tree control: suite passes ({len(MUTATIONS)} mutations to check)")

    survivors = []
    for mutation in MUTATIONS:
        with tempfile.TemporaryDirectory() as scratch:
            tree = Path(scratch) / "mutant"
            tree.mkdir()
            stage(tree)
            plant(tree, mutation)
            result = run_suite(tree)
            if result.returncode == 0:
                survivors.append(mutation["name"])
                print(f"  SURVIVED: {mutation['name']}")
            else:
                print(f"  detected: {mutation['name']}")

    if survivors:
        print("", file=sys.stderr)
        print(
            "hostile mutation survived: the test suite did not fail for "
            f"{len(survivors)} of {len(MUTATIONS)} planted defects:",
            file=sys.stderr,
        )
        for name in survivors:
            print(f"  - {name}", file=sys.stderr)
        print(
            "\nEither a guard lost its test coverage, or the suite's assertion "
            "mechanism is no longer asserting (for example an added tests/test_*.py "
            "module rebinding unittest.TestCase.assert*).",
            file=sys.stderr,
        )
        return 2

    print(f"all {len(MUTATIONS)} planted defects were detected by the real suite")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
