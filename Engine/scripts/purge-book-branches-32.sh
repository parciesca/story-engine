#!/usr/bin/env bash
# Purge Engine/ and CLAUDE.md from all book/* branches.
# Issue: https://github.com/parciesca/story-engine/issues/32
#
# Prerequisites: #33 (always-start-on-main) and #34 (manifest engine fields)
# must be merged to v4 before running this script.
#
# Usage: bash Engine/scripts/purge-book-branches-32.sh
set -euo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel)
COMMIT_MSG="Drop Engine/ and CLAUDE.md — engine lives on main (#32)"

echo "Pre-purge SHAs:"
for branch in $(git branch -r | grep 'origin/book/' | sed 's|.*origin/||'); do
  sha=$(git rev-parse "origin/$branch")
  echo "  $branch -> $sha"
done
echo ""

for branch in $(git branch -r | grep 'origin/book/' | sed 's|.*origin/||'); do
  echo "=== Processing $branch ==="

  WORKTREE="$REPO_ROOT/.worktrees/$branch"
  mkdir -p "$(dirname "$WORKTREE")"

  if [ -d "$WORKTREE" ]; then
    git worktree remove --force "$WORKTREE" 2>/dev/null || true
  fi

  # Always reset local branch to remote tip to avoid stale-branch errors.
  git fetch origin "$branch"
  git branch -f "$branch" "origin/$branch"
  git worktree add "$WORKTREE" "$branch"

  pushd "$WORKTREE" > /dev/null

  CHANGED=0

  if [ -d "Engine" ]; then
    git rm -r Engine/
    CHANGED=1
    echo "  Removed Engine/"
  else
    echo "  Engine/ not present, skipping"
  fi

  if [ -f "CLAUDE.md" ]; then
    git rm CLAUDE.md
    CHANGED=1
    echo "  Removed CLAUDE.md"
  else
    echo "  CLAUDE.md not present, skipping"
  fi

  if [ "$CHANGED" -eq 1 ]; then
    git commit -m "$COMMIT_MSG"
    git push origin "$branch"
    echo "  Committed and pushed."
  else
    echo "  Nothing to remove — skipping commit."
  fi

  popd > /dev/null
  git worktree remove --force "$WORKTREE" 2>/dev/null || true
  echo ""
done

echo "Done. All book/* branches purged."
