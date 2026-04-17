# Engine/scripts

Utility scripts for the story engine.

---

## commit-chapter.sh

Worktree-based chapter commit/push. Keeps the session on `main` by managing a
temporary git worktree for the book branch — no HEAD switches needed.

**Issue:** [#36](https://github.com/parciesca/story-engine/issues/36)

### Usage

```bash
# 1. Set up (or reset) the worktree — prints the worktree path to stdout
worktree=$(bash Engine/scripts/commit-chapter.sh --setup --slug <slug>)

# For a new book (creates the branch from the current HEAD first):
worktree=$(bash Engine/scripts/commit-chapter.sh --setup --slug <slug> --create)

# 2. Write all book files to $worktree/Books/<slug>/
#    (chapter, planning, bible, manifest — engine's job)

# 3. Commit, push, and tear down the worktree
bash Engine/scripts/commit-chapter.sh --commit --slug <slug> --message "Ch N: Title"

# Read-only session cleanup (no chapter written)
bash Engine/scripts/commit-chapter.sh --teardown --slug <slug>
```

### Behaviour

| Situation | Behaviour |
|-----------|-----------|
| Worktree already exists at setup | Removed and recreated (stale cleanup) |
| Branch missing locally and remotely at setup | Exit 1 with suggestion; use `--create` for new books |
| Nothing staged at commit | Exits 0 silently |
| Push failure | Commit kept locally; exits 2 with retry instructions; worktree preserved |
| Unpushed commits at teardown | Exits 1; refuses to remove worktree |

`engine_commit` in `manifest.json` is injected with the current `HEAD` short SHA
during `--commit`, so the engine never needs to call `git rev-parse` itself.

Worktrees live under `.worktrees/book/<slug>/` (git-ignored).
