#!/usr/bin/env bash
# commit-chapter.sh — worktree-based chapter commit/push for the story engine.
# Issue: https://github.com/parciesca/story-engine/issues/36
#
# Manages a git worktree for a book branch so the engine can read, write, and
# commit chapter files without ever switching HEAD off main.
#
# Usage:
#   commit-chapter.sh --setup   --slug <slug>             (existing branch)
#   commit-chapter.sh --setup   --slug <slug> --create    (new branch, forked from HEAD)
#       Creates (or resets) the worktree for book/<slug>.
#       Prints the absolute worktree path to stdout.
#
#   commit-chapter.sh --commit  --slug <slug> --message <msg>
#       Injects engine_commit into manifest.json, stages all changes under
#       Books/<slug>/, commits with <msg>, pushes to origin/book/<slug>.
#       On push failure: leaves commit locally; exits 2 with retry hint.
#       On success: tears down the worktree.
#
#   commit-chapter.sh --teardown --slug <slug>
#       Removes the worktree without committing (read-only or aborted session).
#       Refuses if unpushed commits exist.

set -euo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel)

MODE=""
SLUG=""
MESSAGE=""
CREATE_BRANCH=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --setup)    MODE="setup";           shift ;;
    --commit)   MODE="commit";          shift ;;
    --teardown) MODE="teardown";        shift ;;
    --slug)     SLUG="$2";              shift 2 ;;
    --message)  MESSAGE="$2";           shift 2 ;;
    --create)   CREATE_BRANCH=true;     shift ;;
    *) echo "Unknown argument: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$SLUG" ]]; then
  echo "Error: --slug is required." >&2
  exit 1
fi

BRANCH="book/$SLUG"
WORKTREE="$REPO_ROOT/.worktrees/$BRANCH"

# ── setup ─────────────────────────────────────────────────────────────────────
if [[ "$MODE" == "setup" ]]; then

  # Refresh the remote-tracking ref so the worktree reflects committed state
  # written outside this session (e.g. feedback files saved by the book viewer).
  REMOTE_EXISTS=false
  if git ls-remote --exit-code --heads origin "$BRANCH" &>/dev/null; then
    REMOTE_EXISTS=true
    git fetch origin "$BRANCH"
  fi

  if ! git show-ref --verify --quiet "refs/heads/$BRANCH"; then
    if $CREATE_BRANCH; then
      git branch "$BRANCH"
    elif $REMOTE_EXISTS; then
      git branch "$BRANCH" "refs/remotes/origin/$BRANCH"
    else
      echo "Error: branch '$BRANCH' not found locally or at origin." >&2
      echo "  For a new book, add --create to create the branch from the current HEAD." >&2
      exit 1
    fi
  elif $REMOTE_EXISTS; then
    LOCAL_SHA=$(git rev-parse "refs/heads/$BRANCH")
    REMOTE_SHA=$(git rev-parse "refs/remotes/origin/$BRANCH")
    if [[ "$LOCAL_SHA" != "$REMOTE_SHA" ]]; then
      if git merge-base --is-ancestor "$LOCAL_SHA" "$REMOTE_SHA"; then
        # Local behind origin — fast-forward so the worktree mirrors the remote.
        git update-ref "refs/heads/$BRANCH" "$REMOTE_SHA"
      elif git merge-base --is-ancestor "$REMOTE_SHA" "$LOCAL_SHA"; then
        # Local ahead — preserve unpushed commits from a prior failed push.
        :
      else
        echo "Warning: local '$BRANCH' has diverged from origin." >&2
        echo "  Local:  $LOCAL_SHA" >&2
        echo "  Remote: $REMOTE_SHA" >&2
        echo "  Worktree will use local HEAD; resolve manually before committing." >&2
      fi
    fi
  fi

  if [[ -d "$WORKTREE" ]]; then
    git worktree remove --force "$WORKTREE" 2>/dev/null || true
  fi

  mkdir -p "$(dirname "$WORKTREE")"
  git worktree add "$WORKTREE" "$BRANCH"
  echo "$WORKTREE"

# ── commit ────────────────────────────────────────────────────────────────────
elif [[ "$MODE" == "commit" ]]; then

  if [[ -z "$MESSAGE" ]]; then
    echo "Error: --message is required for --commit." >&2
    exit 1
  fi

  if [[ ! -d "$WORKTREE" ]]; then
    echo "Error: worktree not found at '$WORKTREE'." >&2
    echo "  Run: Engine/scripts/commit-chapter.sh --setup --slug $SLUG" >&2
    exit 1
  fi

  BOOKS_DIR="$WORKTREE/Books/$SLUG"
  if [[ ! -d "$BOOKS_DIR" ]]; then
    echo "Error: book directory not found: $BOOKS_DIR" >&2
    exit 1
  fi

  # Inject current engine SHA into manifest so every chapter commit records
  # which engine version wrote it (issue #34).
  MANIFEST="$BOOKS_DIR/manifest.json"
  if [[ -f "$MANIFEST" ]]; then
    ENGINE_SHA=$(git rev-parse --short HEAD)
    python3 - <<PYEOF
import json, sys
path = "$MANIFEST"
with open(path, "r", encoding="utf-8") as f:
    m = json.load(f)
m["engine_commit"] = "$ENGINE_SHA"
with open(path, "w", encoding="utf-8") as f:
    json.dump(m, f, indent=2, ensure_ascii=False)
    f.write("\n")
PYEOF
  fi

  pushd "$WORKTREE" > /dev/null

  git add "Books/$SLUG/"

  if git diff --cached --quiet; then
    echo "Nothing staged — no changes to commit." >&2
    popd > /dev/null
    exit 0
  fi

  git commit -m "$MESSAGE"

  # Push; on failure leave the commit locally for retry — do NOT tear down.
  if ! git push -u origin "$BRANCH"; then
    popd > /dev/null
    echo "" >&2
    echo "Push failed. The commit is saved locally on '$BRANCH'." >&2
    echo "Retry when connectivity is restored:" >&2
    echo "  git -C '$WORKTREE' push origin $BRANCH" >&2
    echo "Then clean up: Engine/scripts/commit-chapter.sh --teardown --slug $SLUG" >&2
    exit 2
  fi

  popd > /dev/null
  git worktree remove --force "$WORKTREE" 2>/dev/null || true
  echo "Done: '$MESSAGE' committed and pushed to $BRANCH."

# ── teardown ──────────────────────────────────────────────────────────────────
elif [[ "$MODE" == "teardown" ]]; then

  if [[ ! -d "$WORKTREE" ]]; then
    echo "No worktree found at '$WORKTREE' — nothing to do."
    exit 0
  fi

  # Refuse if there are commits that haven't been pushed.
  UNPUSHED=$(git -C "$WORKTREE" log "origin/$BRANCH..$BRANCH" --oneline 2>/dev/null | wc -l || echo 0)
  if [[ "$UNPUSHED" -gt 0 ]]; then
    echo "Error: worktree has $UNPUSHED unpushed commit(s) on '$BRANCH'." >&2
    echo "Push first: git -C '$WORKTREE' push origin $BRANCH" >&2
    exit 1
  fi

  git worktree remove --force "$WORKTREE"
  echo "Worktree for $BRANCH removed."

else
  echo "Usage:" >&2
  echo "  commit-chapter.sh --setup   --slug <slug> [--create]" >&2
  echo "  commit-chapter.sh --commit  --slug <slug> --message <msg>" >&2
  echo "  commit-chapter.sh --teardown --slug <slug>" >&2
  exit 1
fi
