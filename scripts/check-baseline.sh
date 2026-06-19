#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
PLAN="$ROOT_DIR/docs/plans/2026-06-08-fable-flux-maintenance-baseline.md"
QUICK_FRONTMATTER_PLAN="$ROOT_DIR/docs/plans/2026-06-09-fable-flux-quick-frontmatter-guard.md"
UPLOADER_SEQUENCE_PLAN="$ROOT_DIR/docs/plans/2026-06-09-fable-flux-uploader-sequence-metadata-guard.md"
VALIDATOR_SEQUENCE_PLAN="$ROOT_DIR/docs/plans/2026-06-09-fable-flux-validator-sequence-metadata-guard.md"
POE_VALIDATION_LOG_PLAN="$ROOT_DIR/docs/plans/2026-06-09-fable-flux-poe-validation-log-boundary.md"
POE_RATE_LIMITER_PLAN="$ROOT_DIR/docs/plans/2026-06-09-fable-flux-poe-rate-limiter-guard.md"
POE_RETRY_PLAN="$ROOT_DIR/docs/plans/2026-06-10-fable-flux-poe-retry-backoff.md"
POE_STATUS_PLAN="$ROOT_DIR/docs/plans/2026-06-12-poe-model-validation-status.md"
CI_PLAN="$ROOT_DIR/docs/plans/2026-06-10-ci-baseline.md"
RUNNER_PIN_PLAN="$ROOT_DIR/docs/plans/2026-06-12-hosted-runner-pin.md"
PYTHON=${PYTHON:-python3}

cleanup_bytecode() {
  find "$ROOT_DIR" -maxdepth 4 -type d -name "__pycache__" -prune -exec rm -rf {} + 2>/dev/null || true
  find "$ROOT_DIR" -maxdepth 4 -type f -name "*.pyc" -delete 2>/dev/null || true
}

trap cleanup_bytecode EXIT
cleanup_bytecode

require_file() {
  path=$1
  if [ ! -f "$ROOT_DIR/$path" ]; then
    printf '%s\n' "Required file missing: $path" >&2
    exit 1
  fi
}

for path in \
  ".env.example" \
  ".gitignore" \
  ".github/workflows/check.yml" \
  "CHANGES.md" \
  "Makefile" \
  "README.md" \
  "requirements-ci.txt" \
  "SECURITY.md" \
  "VISION.md" \
  "config/generation_config.yaml" \
  "data/characters.json" \
  "data/settings.json" \
  "data/tags.json" \
  "front-end/.env.local.example" \
  "front-end/package-lock.json" \
  "front-end/package.json" \
  "front-end/src/app/api/chat/completions/route.ts" \
  "generate_stories.py" \
  "requirements.txt" \
  "serving/main.py" \
  "setup.py" \
  "src/diversity_tracker.py" \
  "src/poe_client.py" \
  "src/story_validator.py" \
  "tests/test_diversity_tracker.py" \
  "tests/test_huggingface_uploader.py" \
  "tests/test_poe_client.py" \
  "tests/test_story_validator.py" \
  "docs/plans/2026-06-09-fable-flux-uploader-sequence-metadata-guard.md" \
  "docs/plans/2026-06-09-fable-flux-poe-validation-log-boundary.md" \
  "docs/plans/2026-06-09-fable-flux-uploader-frontmatter-guard.md" \
  "docs/plans/2026-06-09-fable-flux-quick-frontmatter-guard.md" \
  "docs/plans/2026-06-09-fable-flux-validator-sequence-metadata-guard.md" \
  "docs/plans/2026-06-09-fable-flux-frontmatter-mapping-guard.md" \
  "docs/plans/2026-06-09-fable-flux-poe-response-log-boundary.md" \
  "docs/plans/2026-06-09-fable-flux-poe-rate-limiter-guard.md" \
  "docs/plans/2026-06-10-fable-flux-poe-retry-backoff.md" \
  "docs/plans/2026-06-12-poe-model-validation-status.md" \
  "docs/plans/2026-06-12-hosted-runner-pin.md" \
  "docs/plans/2026-06-10-ci-baseline.md" \
  "docs/plans/2026-06-08-fable-flux-maintenance-baseline.md"; do
  require_file "$path"
done

"$PYTHON" -m py_compile \
  "$ROOT_DIR/generate_stories.py" \
  "$ROOT_DIR/upload_to_huggingface.py" \
  "$ROOT_DIR/setup.py" \
  "$ROOT_DIR/serving/main.py" \
  "$ROOT_DIR"/src/*.py \
  "$ROOT_DIR"/tests/*.py

(cd "$ROOT_DIR" && "$PYTHON" -m unittest discover -s tests -p "test*.py")

"$PYTHON" - "$ROOT_DIR" <<'PY'
import json
import sys
from pathlib import Path

import yaml

root = Path(sys.argv[1])

def fail(message):
    print(message, file=sys.stderr)
    raise SystemExit(1)

config = yaml.safe_load((root / "config/generation_config.yaml").read_text())
for section in ["generation", "quality", "diversity", "poe_api", "paths"]:
    if section not in config:
        fail(f"Missing config section: {section}")

generation = config["generation"]
if generation["start_id"] > generation["end_id"]:
    fail("Generation start_id must not exceed end_id.")
if generation["concurrent_requests"] > config["poe_api"]["rate_limit"]:
    fail("Concurrent requests must not exceed the configured Poe rate limit.")

for filename, key in [
    ("data/characters.json", "characters"),
    ("data/settings.json", "settings"),
    ("data/tags.json", "tags"),
]:
    data = json.loads((root / filename).read_text())
    values = data.get(key)
    if not isinstance(values, list) or len(values) < 10:
        fail(f"{filename} must contain a non-empty {key} list.")
PY

if ! grep -Fq "make check" "$ROOT_DIR/README.md" ||
  ! grep -Fq "POE_API_KEY" "$ROOT_DIR/README.md" ||
  ! grep -Fq "MODAL_API_URL" "$ROOT_DIR/README.md" ||
  ! grep -Fq "Validator and uploader metadata" "$ROOT_DIR/README.md" ||
  ! grep -Fq "Poe model validation response bodies" "$ROOT_DIR/README.md" ||
  ! grep -Fq "Poe rate-limit tests" "$ROOT_DIR/README.md" ||
  ! grep -Fq "GitHub Actions" "$ROOT_DIR/README.md" ||
  ! grep -Fq "rechecks token state after sleeping" "$ROOT_DIR/README.md" ||
  ! grep -Fq "string lists so quality checks" "$ROOT_DIR/README.md" ||
  ! grep -Fq "children's educational" "$ROOT_DIR/README.md"; then
  printf '%s\n' "README must document baseline verification, env keys, and responsible story generation scope." >&2
  exit 1
fi

if ! grep -Fq "scripts/check-baseline.sh" "$ROOT_DIR/VISION.md" ||
  ! grep -Fq "unused characters and settings" "$ROOT_DIR/VISION.md" ||
  ! grep -Fq "Story validation requires" "$ROOT_DIR/VISION.md" ||
  ! grep -Fq "Poe model validation response bodies" "$ROOT_DIR/VISION.md" ||
  ! grep -Fq "GitHub Actions" "$ROOT_DIR/VISION.md" ||
  ! grep -Fq "rate limiter validates positive limits" "$ROOT_DIR/VISION.md" ||
  ! grep -Fq "string lists before quick" "$ROOT_DIR/VISION.md" ||
  ! grep -Fq "frontend proxy" "$ROOT_DIR/VISION.md"; then
  printf '%s\n' "VISION must describe the current baseline and guarded surfaces." >&2
  exit 1
fi

if ! grep -Fq "POE_API_KEY=your_poe_api_key_here" "$ROOT_DIR/.env.example" ||
  ! grep -Fq "HF_TOKEN=your_huggingface_token_here" "$ROOT_DIR/.env.example" ||
  ! grep -Fq "MODAL_API_KEY=your_modal_api_key_here" "$ROOT_DIR/front-end/.env.local.example" ||
  ! grep -Fq "MODAL_API_URL=https://your-modal-endpoint.example.com/v1/chat/completions" "$ROOT_DIR/front-end/.env.local.example" ||
  ! grep -Fq "MODAL_MODEL=garethpaul/gpt-oss-20b-fableflux-mxfp4" "$ROOT_DIR/front-end/.env.local.example"; then
  printf '%s\n' "Environment examples must use placeholders for Poe, Hugging Face, and Modal configuration." >&2
  exit 1
fi

if ! grep -Fq "usage_counts = {char: self.character_usage.get(char, 0)" "$ROOT_DIR/src/diversity_tracker.py" ||
  ! grep -Fq "test_character_selection_includes_unused_candidates" "$ROOT_DIR/tests/test_diversity_tracker.py"; then
  printf '%s\n' "Diversity baseline must keep coverage for unused character and setting selection." >&2
  exit 1
fi

if ! grep -Fq "def _response_body_summary" "$ROOT_DIR/src/poe_client.py" ||
  ! grep -Fq "clock=time.monotonic" "$ROOT_DIR/src/poe_client.py" ||
  ! grep -Fq "Rate limit must be positive" "$ROOT_DIR/src/poe_client.py" ||
  ! grep -Fq "Rate limit period must be positive" "$ROOT_DIR/src/poe_client.py" ||
  ! grep -Fq "await self._sleep" "$ROOT_DIR/src/poe_client.py" ||
  ! grep -Fq "Poe response body omitted from logs" "$ROOT_DIR/src/poe_client.py" ||
  ! grep -Fq "Poe validation response body omitted from logs" "$ROOT_DIR/src/poe_client.py" ||
  ! grep -Fq "response body length" "$ROOT_DIR/src/poe_client.py" ||
  ! grep -Fq "test_rate_limiter_rejects_invalid_limits" "$ROOT_DIR/tests/test_poe_client.py" ||
  ! grep -Fq "test_rate_limiter_rechecks_token_after_waiting" "$ROOT_DIR/tests/test_poe_client.py" ||
  ! grep -Fq "test_response_body_summary_omits_raw_response_content" "$ROOT_DIR/tests/test_poe_client.py" ||
  ! grep -Fq "test_model_validation_logs_response_summary_without_raw_body" "$ROOT_DIR/tests/test_poe_client.py" ||
  ! grep -Fq "test_model_validation_accepts_only_http_200" "$ROOT_DIR/tests/test_poe_client.py" ||
  ! grep -Fq "(400, False)" "$ROOT_DIR/tests/test_poe_client.py" ||
  ! grep -Fq "(404, False)" "$ROOT_DIR/tests/test_poe_client.py" ||
  ! grep -Fq "(429, False)" "$ROOT_DIR/tests/test_poe_client.py" ||
  ! grep -Fq "Model {model} validation returned status {response.status}" "$ROOT_DIR/src/poe_client.py" ||
  grep -Fq "return response.status < 500" "$ROOT_DIR/src/poe_client.py" ||
  ! grep -Fq "if attempt < max_retries" "$ROOT_DIR/src/poe_client.py" ||
  ! grep -Fq "await asyncio.sleep(retry_delay)" "$ROOT_DIR/src/poe_client.py" ||
  ! grep -Fq "test_timeout_retry_sleeps_once_and_exhausted_attempt_returns_immediately" "$ROOT_DIR/tests/test_poe_client.py" ||
  ! grep -Fq "test_rate_limit_retry_uses_provider_backoff_once" "$ROOT_DIR/tests/test_poe_client.py" ||
  grep -Fq "error_data" "$ROOT_DIR/src/poe_client.py" ||
  grep -Fq "Raw response:" "$ROOT_DIR/src/poe_client.py" ||
  grep -Eq "logging\\.(error|warning|info|debug).*response_text" "$ROOT_DIR/src/poe_client.py"; then
  printf '%s\n' "Poe client must avoid logging raw upstream response bodies." >&2
  exit 1
fi

"$PYTHON" - "$ROOT_DIR/tests/test_poe_client.py" <<'PY'
import ast
import sys
from pathlib import Path

test_path = Path(sys.argv[1])
tree = ast.parse(test_path.read_text(), filename=str(test_path))
expected = {
    200: True,
    201: False,
    302: False,
    400: False,
    401: False,
    403: False,
    404: False,
    429: False,
    500: False,
}
matrix = None

for node in ast.walk(tree):
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        continue
    if node.name != "test_model_validation_accepts_only_http_200":
        continue
    for child in ast.walk(node):
        if not isinstance(child, ast.For):
            continue
        if not isinstance(child.target, (ast.Tuple, ast.List)):
            continue
        names = [item.id for item in child.target.elts if isinstance(item, ast.Name)]
        if names != ["status", "expected"]:
            continue
        try:
            matrix = dict(ast.literal_eval(child.iter))
        except (TypeError, ValueError, SyntaxError):
            pass

if matrix is None or any(matrix.get(status) is not result for status, result in expected.items()):
    print(
        "Poe validation test must retain the complete explicit HTTP status matrix.",
        file=sys.stderr,
    )
    raise SystemExit(1)
PY

if ! grep -Fq "isinstance(frontmatter, dict)" "$ROOT_DIR/src/story_validator.py" ||
  ! grep -Fq "def _validate_string_list_field" "$ROOT_DIR/src/story_validator.py" ||
  ! grep -Fq "non-empty list of strings" "$ROOT_DIR/src/story_validator.py" ||
  ! grep -Fq "frontmatter_valid, _frontmatter_errors = self._validate_frontmatter(frontmatter)" "$ROOT_DIR/src/story_validator.py" ||
  ! grep -Fq "self._parse_story_structure(content)" "$ROOT_DIR/src/story_validator.py" ||
  ! grep -Fq "test_quick_validate_rejects_non_mapping_frontmatter" "$ROOT_DIR/tests/test_story_validator.py" ||
  ! grep -Fq "test_validate_story_rejects_non_string_sequence_metadata" "$ROOT_DIR/tests/test_story_validator.py" ||
  ! grep -Fq "test_quick_validate_rejects_non_string_sequence_metadata" "$ROOT_DIR/tests/test_story_validator.py" ||
  ! grep -Fq "test_non_mapping_frontmatter_is_invalid" "$ROOT_DIR/tests/test_story_validator.py"; then
  printf '%s\n' "Story validator must reject malformed YAML frontmatter and sequence metadata in full and quick validation." >&2
  exit 1
fi

if ! grep -Fq "non-empty string lists" "$ROOT_DIR/SECURITY.md"; then
  printf '%s\n' "SECURITY must document story metadata sequence boundaries." >&2
  exit 1
fi

if ! grep -Fq "Poe model validation response bodies" "$ROOT_DIR/SECURITY.md"; then
  printf '%s\n' "SECURITY must document Poe model validation logging boundaries." >&2
  exit 1
fi

if ! grep -Fq "fail closed for every response except HTTP 200" "$ROOT_DIR/SECURITY.md"; then
  printf '%s\n' "SECURITY must document fail-closed Poe model accessibility validation." >&2
  exit 1
fi

if ! grep -Fq "post-sleep token check" "$ROOT_DIR/SECURITY.md"; then
  printf '%s\n' "SECURITY must document Poe rate limiter boundaries." >&2
  exit 1
fi

if ! grep -Fq "one backoff delay per actual retry" "$ROOT_DIR/SECURITY.md"; then
  printf '%s\n' "SECURITY must document Poe retry backoff boundaries." >&2
  exit 1
fi

if ! grep -Fq "status: completed" "$POE_RETRY_PLAN"; then
  printf '%s\n' "Poe retry plan must remain completed: $POE_RETRY_PLAN" >&2
  exit 1
fi

"$PYTHON" - "$POE_STATUS_PLAN" <<'PY'
import re
import sys
from pathlib import Path

plan_path = Path(sys.argv[1])
text = plan_path.read_text()
status_headings = re.findall(r"^## Status: .+$", text, flags=re.MULTILINE)

try:
    verification = text.split("## Verification Completed\n", 1)[1]
except IndexError:
    verification = ""

required_evidence = (
    "- `make check` passes locally with 23 tests.",
    "- GitHub Actions push run `27391848731` passed",
    "- GitHub Actions pull-request run `27391849643` passed",
)

if (
    status_headings != ["## Status: Completed"]
    or any(evidence not in verification for evidence in required_evidence)
    or re.search(r"\b(?:pending|todo|tbd|not run)\b", verification, flags=re.IGNORECASE)
):
    print(
        "Poe validation status plan must remain completed with actual hosted matrix verification recorded.",
        file=sys.stderr,
    )
    raise SystemExit(1)
PY

if ! grep -Fq "GitHub Actions" "$ROOT_DIR/SECURITY.md"; then
  printf '%s\n' "SECURITY must document the hosted baseline." >&2
  exit 1
fi

workflow="$ROOT_DIR/.github/workflows/check.yml"
workflow_files=$(find "$ROOT_DIR/.github/workflows" -mindepth 1 -maxdepth 1 -type f -print | sort)
if [ "$workflow_files" != "$workflow" ]; then
  printf '%s\n' "GitHub Actions workflow inventory must contain only check.yml." >&2
  exit 1
fi

if ! grep -Fq "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405" "$workflow" ||
  ! grep -Fq "actions/setup-node@48b55a011bda9f5d6aeb4c2d9c7362e8dae4041e" "$workflow" ||
  [ "$(grep -Fc "runs-on: ubuntu-24.04" "$workflow")" -ne 2 ] ||
  grep -Fq "ubuntu-latest" "$workflow" ||
  ! grep -Fq 'python-version: ["3.10", "3.12", "3.14"]' "$workflow" ||
  ! grep -Fq "node-version: [20, 22, 24]" "$workflow" ||
  ! grep -Fq "python -m pip install -r requirements-ci.txt" "$workflow" ||
  ! grep -Fq "run: make check" "$workflow" ||
  ! grep -Fq "run: npm ci" "$workflow" ||
  ! grep -Fq "run: npm run lint" "$workflow" ||
  ! grep -Fq "run: npm run build" "$workflow" ||
  ! grep -Fq "run: npm run audit" "$workflow" ||
  ! grep -Fq "workflow_dispatch:" "$workflow" ||
  ! grep -Fq "cancel-in-progress: true" "$workflow"; then
  printf '%s\n' "GitHub Actions workflow must run pinned Python and frontend matrices." >&2
  exit 1
fi

if ! grep -Fq "status: completed" "$RUNNER_PIN_PLAN" ||
  ! grep -Fq "exactly two explicit runner declarations" "$RUNNER_PIN_PLAN" ||
  ! grep -Fq "Local and external-working-directory gates passed" "$RUNNER_PIN_PLAN" ||
  ! grep -Fq "hostile mutations rejected" "$RUNNER_PIN_PLAN"; then
  printf '%s\n' "Hosted runner plan must record completed status and verification." >&2
  exit 1
fi

if ! grep -Fq "Ubuntu 24.04" "$ROOT_DIR/README.md" ||
  ! grep -Fq "explicit Ubuntu 24.04" "$ROOT_DIR/SECURITY.md" ||
  ! grep -Fq "pinned Ubuntu runner" "$ROOT_DIR/VISION.md" ||
  ! grep -Fq "Pinned both hosted jobs to Ubuntu 24.04" "$ROOT_DIR/CHANGES.md"; then
  printf '%s\n' "Repository guidance must document the hosted runner boundary." >&2
  exit 1
fi

if [ "$(grep -Ec '^[[:space:]]+(-[[:space:]]+)?uses: actions/checkout@' "$workflow")" -ne 2 ]; then
  printf '%s\n' "GitHub Actions must contain exactly one checkout step per job." >&2
  exit 1
fi

if ! awk '
  function finish_step() {
    if (checkout) {
      checkout_count[current_job]++
      if (persist_credentials) {
        secure_checkout_count[current_job]++
      }
    }
    checkout = 0
    with_block = 0
    persist_credentials = 0
  }

  /^  (python|frontend):$/ {
    finish_step()
    current_job = $1
    sub(/:$/, "", current_job)
    jobs_seen[current_job] = 1
    next
  }

  /^      - / {
    finish_step()
  }

  /^        uses: actions\/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10([[:space:]]+#.*)?$/ {
    checkout = 1
  }

  /^      - uses: actions\/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10([[:space:]]+#.*)?$/ {
    checkout = 1
  }

  checkout && /^        with:$/ {
    with_block = 1
  }

  checkout && with_block && /^          persist-credentials: false$/ {
    persist_credentials = 1
  }

  END {
    finish_step()
    python_secure = jobs_seen["python"] && checkout_count["python"] == 1 && secure_checkout_count["python"] == 1
    frontend_secure = jobs_seen["frontend"] && checkout_count["frontend"] == 1 && secure_checkout_count["frontend"] == 1
    exit !(python_secure && frontend_secure)
  }
' "$workflow"; then
  printf '%s\n' "Every pinned checkout step must disable persisted credentials." >&2
  exit 1
fi

if ! awk '
  /^permissions:$/ {
    permissions_count++
    in_permissions = 1
    next
  }

  in_permissions && /^[^[:space:]]/ {
    in_permissions = 0
  }

  in_permissions && /^  contents: read$/ {
    contents_read++
    next
  }

  in_permissions && /^  [[:alnum:]_-]+:/ {
    unexpected_permission++
  }

  END {
    exit !(permissions_count == 1 && contents_read == 1 && unexpected_permission == 0)
  }
' "$workflow" ||
  grep -Eq '^[[:space:]]+permissions:' "$workflow" ||
  grep -Eq '^[[:space:]]*permissions:[[:space:]]*write-all([[:space:]]*(#.*)?)?$' "$workflow" ||
  grep -Eq '^[[:space:]]+[[:alnum:]_-]+:[[:space:]]*write([[:space:]]*(#.*)?)?$' "$workflow"; then
  printf '%s\n' "GitHub Actions must grant only top-level read access to repository contents." >&2
  exit 1
fi


if ! grep -Fq "checkout credentials are not persisted" "$ROOT_DIR/README.md"; then
  printf '%s\n' "README must document the credential-free checkout boundary." >&2
  exit 1
fi

if ! grep -Fxq "PyYAML==6.0.3" "$ROOT_DIR/requirements-ci.txt" ||
  ! grep -Fxq "aiohttp==3.14.0" "$ROOT_DIR/requirements-ci.txt"; then
  printf '%s\n' "Minimal offline CI dependencies must remain pinned." >&2
  exit 1
fi

if ! grep -Fq '"react": "19.2.7"' "$ROOT_DIR/front-end/package.json" ||
  ! grep -Fq '"react-dom": "19.2.7"' "$ROOT_DIR/front-end/package.json" ||
  ! grep -Fq '"audit": "npm audit --audit-level=moderate"' "$ROOT_DIR/front-end/package.json"; then
  printf '%s\n' "Frontend React and audit contracts must remain pinned." >&2
  exit 1
fi
if ! grep -Fq "isinstance(metadata, dict)" "$ROOT_DIR/src/huggingface_uploader.py" ||
  ! grep -Fq "def _metadata_string_list" "$ROOT_DIR/src/huggingface_uploader.py" ||
  ! grep -Fq "must be a non-empty list" "$ROOT_DIR/src/huggingface_uploader.py" ||
  ! grep -Fq "test_parse_story_file_rejects_non_mapping_frontmatter" "$ROOT_DIR/tests/test_huggingface_uploader.py"; then
  printf '%s\n' "Hugging Face uploader must reject malformed YAML frontmatter before dataset record creation." >&2
  exit 1
fi

if ! grep -Fq "test_parse_story_file_rejects_scalar_sequence_metadata" "$ROOT_DIR/tests/test_huggingface_uploader.py" ||
  ! grep -Fq "test_parse_story_file_rejects_non_string_sequence_items" "$ROOT_DIR/tests/test_huggingface_uploader.py"; then
  printf '%s\n' "Hugging Face uploader tests must cover malformed characters/tags sequence metadata." >&2
  exit 1
fi

if ! grep -Fq "lint: check" "$ROOT_DIR/Makefile" ||
  ! grep -Fq "test: check" "$ROOT_DIR/Makefile" ||
  ! grep -Fq "build: check" "$ROOT_DIR/Makefile"; then
  printf '%s\n' "Makefile must expose lint, test, and build gates." >&2
  exit 1
fi

route="$ROOT_DIR/front-end/src/app/api/chat/completions/route.ts"
if ! grep -Fq "process.env.MODAL_API_KEY" "$route" ||
  ! grep -Fq "process.env.MODAL_API_URL" "$route" ||
  ! grep -Fq "process.env.MODAL_MODEL" "$route" ||
  ! grep -Fq "new URL" "$route" ||
  ! grep -Fq 'url.protocol === "https:"' "$route" ||
  ! grep -Fq "url.hostname.length > 0" "$route" ||
  ! grep -Fq "trimmedPrompt.length === 0 || trimmedPrompt.length > 200" "$route" ||
  grep -Eq "Modal_API_KEY|POE_API_KEY" "$route" ||
  grep -Fq "GPT-5-Mini" "$route" ||
  grep -Eq "console\\.error\\(.*(storyContent|modalData|errorText)" "$route"; then
  printf '%s\n' "Frontend proxy must require env-backed Modal config, HTTPS URL parsing, bounded prompts, and no raw generated-content logs." >&2
  exit 1
fi

if grep -Eq 'shell=True|Popen\(" "\.join\(cmd\)' "$ROOT_DIR/serving/main.py" ||
  ! grep -Fq "subprocess.Popen(cmd)" "$ROOT_DIR/serving/main.py"; then
  printf '%s\n' "Modal serving launcher must pass argv directly and avoid shell=True." >&2
  exit 1
fi

tracked_generated=$(
  git -C "$ROOT_DIR" ls-files |
    grep -E '(^story_generator/|(^|/)__pycache__/|\.pyc$)' |
    while IFS= read -r path; do
      if [ -e "$ROOT_DIR/$path" ]; then
        printf '%s\n' "$path"
      fi
    done || true
)
if [ -n "$tracked_generated" ]; then
  printf '%s\n' "Generated Python environment/cache artifacts must not be tracked:" >&2
  printf '%s\n' "$tracked_generated" | sed -n '1,40p' >&2
  exit 1
fi

if ! grep -Fq "__pycache__/" "$ROOT_DIR/.gitignore" ||
  ! grep -Fq "story_generator/" "$ROOT_DIR/.gitignore" ||
  ! grep -Fq ".venv/" "$ROOT_DIR/.gitignore" ||
  ! grep -Fq "*.py[cod]" "$ROOT_DIR/.gitignore" ||
  ! grep -Fq "front-end/node_modules/" "$ROOT_DIR/.gitignore" ||
  ! grep -Fq "output/generated_stories/" "$ROOT_DIR/.gitignore"; then
  printf '%s\n' "Generated Python/frontend artifacts must stay ignored." >&2
  exit 1
fi

if [ -d "$ROOT_DIR/story_generator" ]; then
  printf '%s\n' "Tracked virtual environment directory must be removed from the working tree." >&2
  exit 1
fi

if [ -d "$ROOT_DIR/front-end/node_modules" ]; then
  (cd "$ROOT_DIR/front-end" && npm run lint)
else
  printf '%s\n' "Skipping frontend lint: front-end/node_modules is not installed."
fi

if ! grep -Fq "status: completed" "$PLAN"; then
  printf '%s\n' "Plan must be marked completed." >&2
  exit 1
fi

if ! grep -Fq "status: completed" "$ROOT_DIR/docs/plans/2026-06-09-fable-flux-poe-response-log-boundary.md"; then
  printf '%s\n' "Poe response logging boundary plan must be marked completed." >&2
  exit 1
fi

if ! grep -Fq "status: completed" "$ROOT_DIR/docs/plans/2026-06-09-fable-flux-frontmatter-mapping-guard.md"; then
  printf '%s\n' "Frontmatter mapping guard plan must be marked completed." >&2
  exit 1
fi

if ! grep -Fq "status: completed" "$QUICK_FRONTMATTER_PLAN"; then
  printf '%s\n' "Quick frontmatter guard plan must be marked completed." >&2
  exit 1
fi

if ! grep -Fq "status: completed" "$ROOT_DIR/docs/plans/2026-06-09-fable-flux-uploader-frontmatter-guard.md"; then
  printf '%s\n' "Uploader frontmatter guard plan must be marked completed." >&2
  exit 1
fi

if ! grep -Fq "status: completed" "$UPLOADER_SEQUENCE_PLAN"; then
  printf '%s\n' "Uploader sequence metadata guard plan must be marked completed." >&2
  exit 1
fi

if ! grep -Fq "status: completed" "$VALIDATOR_SEQUENCE_PLAN"; then
  printf '%s\n' "Validator sequence metadata guard plan must be marked completed." >&2
  exit 1
fi

if ! grep -Fq "status: completed" "$POE_VALIDATION_LOG_PLAN"; then
  printf '%s\n' "Poe validation logging boundary plan must be marked completed." >&2
  exit 1
fi

if ! grep -Fq "make check" "$VALIDATOR_SEQUENCE_PLAN"; then
  printf '%s\n' "Validator sequence metadata guard plan must record make check verification." >&2
  exit 1
fi

if ! grep -Fq "make check" "$POE_VALIDATION_LOG_PLAN"; then
  printf '%s\n' "Poe validation logging boundary plan must record make check verification." >&2
  exit 1
fi

if ! grep -Fq "status: completed" "$CI_PLAN" ||
  ! grep -Fq "make check" "$CI_PLAN"; then
  printf '%s\n' "CI baseline plan must record completed make check verification." >&2
  exit 1
fi

printf '%s\n' "fable-flux maintenance baseline checks passed."
