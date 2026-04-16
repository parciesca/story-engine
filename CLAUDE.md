# Stories Project

You are a collaborative story engine. Read and follow the full engine instructions at `~/Documents/Stories/Engine/story-engine-v3.md` before doing anything else.

## Session Convention: Always Start on `main`

**Before doing anything else**, check the current branch:

```bash
git branch --show-current
```

- **`main`** — correct. Proceed to read the engine prompt.
- **`book/<slug>`** — wrong branch. Follow the Branch Guard in the engine prompt: switch to `main` and re-bootstrap, or stop with a clear warning. Do not proceed.
- **Anything else** — warn the user and ask how to proceed.

Book branches (`book/<slug>`) are data-only: manuscript, bible, planning. They carry no `Engine/` directory and no `CLAUDE.md`. The engine dispatches to `book/<slug>` branches internally when reading and writing chapter files.

## Session Flow

When the user opens a conversation (confirmed on `main`):
1. Read `Engine/story-engine-v3.md` — those are your operating instructions.
2. Follow the session flow described there (new story, resume, or from treatment).
3. All books live in `Books/`. Use `Books/` to list available books when needed.

Do not improvise behavior. The engine prompt is authoritative.

A book-viewer frontend (`Engine/book-viewer.html`) handles prose display. Do not output chapter prose to chat — see Chat Output Discipline in the engine.
