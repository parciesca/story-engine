#!/usr/bin/env bash
# migrate-34-engine-fields.sh
# Adds `engine` and `engine_commit` to manifest.json on every book/* branch.
# All existing books use the "story" engine.
# engine_commit is set to the v3 tag SHA (the engine revision that wrote these books).
#
# Usage: bash Engine/scripts/migrate-34-engine-fields.sh
# Run from the repo root. Requires git and python3 (for json editing).

set -euo pipefail

V3_SHA=$(git rev-parse --short v3)
COMMIT_MSG="Manifest: add engine + engine_commit fields (#34)"

BRANCHES=$(git branch -r | grep 'origin/book/' | sed 's|.*origin/||' | tr -d ' ')

for BRANCH in $BRANCHES; do
  echo "==> $BRANCH"
  SLUG="${BRANCH#book/}"
  MANIFEST="Books/$SLUG/manifest.json"

  # Use a temporary worktree to avoid disturbing the main working tree
  WORKTREE_DIR=$(mktemp -d)
  git worktree add "$WORKTREE_DIR" "$BRANCH" 2>/dev/null || \
    git worktree add "$WORKTREE_DIR" -b "${BRANCH}-migrate-tmp" "origin/$BRANCH"

  # Patch the manifest in-place with python
  python3 - "$WORKTREE_DIR/$MANIFEST" "$V3_SHA" <<'PYEOF'
import sys, json

manifest_path, engine_commit = sys.argv[1], sys.argv[2]
with open(manifest_path, encoding="utf-8") as f:
    m = json.load(f)

if "engine" in m and "engine_commit" in m:
    print(f"  already patched, skipping")
    sys.exit(0)

m["engine"] = "story"
m["engine_commit"] = engine_commit

with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(m, f, indent=2, ensure_ascii=False)
    f.write("\n")

print(f"  patched: engine=story engine_commit={engine_commit}")
PYEOF

  (
    cd "$WORKTREE_DIR"
    git add "$MANIFEST"
    # Only commit if there's something staged
    if ! git diff --cached --quiet; then
      git commit -m "$COMMIT_MSG"
      git push origin "HEAD:$BRANCH"
      echo "  committed + pushed"
    else
      echo "  nothing to commit (already had fields)"
    fi
  )

  git worktree remove --force "$WORKTREE_DIR"
done

echo ""
echo "Done. Verify with: git log --all --oneline --grep='#34'"
