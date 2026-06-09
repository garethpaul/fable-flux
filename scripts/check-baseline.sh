#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
PLAN="$ROOT_DIR/docs/plans/2026-06-08-fable-flux-maintenance-baseline.md"
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
  "CHANGES.md" \
  "Makefile" \
  "README.md" \
  "SECURITY.md" \
  "VISION.md" \
  "config/generation_config.yaml" \
  "data/characters.json" \
  "data/settings.json" \
  "data/tags.json" \
  "front-end/.env.local.example" \
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
  "tests/test_poe_client.py" \
  "tests/test_story_validator.py" \
  "docs/plans/2026-06-09-fable-flux-frontmatter-mapping-guard.md" \
  "docs/plans/2026-06-09-fable-flux-poe-response-log-boundary.md" \
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

"$PYTHON" -m unittest discover -s "$ROOT_DIR/tests" -p "test*.py"

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
  ! grep -Fq "children's educational" "$ROOT_DIR/README.md"; then
  printf '%s\n' "README must document baseline verification, env keys, and responsible story generation scope." >&2
  exit 1
fi

if ! grep -Fq "scripts/check-baseline.sh" "$ROOT_DIR/VISION.md" ||
  ! grep -Fq "unused characters and settings" "$ROOT_DIR/VISION.md" ||
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
  ! grep -Fq "Poe response body omitted from logs" "$ROOT_DIR/src/poe_client.py" ||
  ! grep -Fq "response body length" "$ROOT_DIR/src/poe_client.py" ||
  ! grep -Fq "test_response_body_summary_omits_raw_response_content" "$ROOT_DIR/tests/test_poe_client.py" ||
  grep -Fq "Raw response:" "$ROOT_DIR/src/poe_client.py" ||
  grep -Eq "logging\\.(error|warning|info|debug).*response_text" "$ROOT_DIR/src/poe_client.py"; then
  printf '%s\n' "Poe client must avoid logging raw upstream response bodies." >&2
  exit 1
fi

if ! grep -Fq "isinstance(frontmatter, dict)" "$ROOT_DIR/src/story_validator.py" ||
  ! grep -Fq "test_non_mapping_frontmatter_is_invalid" "$ROOT_DIR/tests/test_story_validator.py"; then
  printf '%s\n' "Story validator must reject non-mapping YAML frontmatter at parse time." >&2
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

printf '%s\n' "fable-flux maintenance baseline checks passed."
