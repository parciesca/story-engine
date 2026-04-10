# Story Engine

A file-backed collaborative novel engine for Claude Code. You and Claude co-author books together — Claude writes, you steer. Stories persist across sessions in plain files so nothing is lost when context windows close.

**Status:** Alpha. Single-author project, actively developed. Interfaces and file layouts may still shift without deprecation notices.

---

## How It Works

Every Claude Code session in this project is a story session. Claude reads the engine prompt (`Engine/story-engine-v3.md`), loads the book state from disk, and picks up exactly where you left off.

**The loop:**
1. Claude reads the manifest, story bible, and recent chapters at session start
2. You give a direction — a letter choice, a paragraph of steering, or just "keep going"
3. Claude writes the next chapter and saves all files
4. Claude presents a 1–2 sentence scene summary and choices for the next chapter
5. Repeat

Prose is written to `Books/` and read back from there — not held in chat memory. This means stories can be as long as they need to be.

---

## Repository Structure

```
story-engine/
├── CLAUDE.md                        # Claude Code session config
├── Engine/
│   ├── story-engine-v3.md           # The engine prompt (Claude's operating instructions)
│   ├── book-viewer.html             # Local browser UI for reading chapters
│   ├── new-book-template.md         # Optional brief for starting a new book
│   ├── guidgen.py                   # GUID generator for book/chapter/branch IDs
│   ├── migrate-book.py              # Migration script: compiled book.md → v3 chapter files
│   └── Archive/                     # Previous engine versions (v1, v2, CYOA-v1)
├── Books/
│   └── [book-slug]/
│       ├── manifest.json            # Book state, chapter registry, branch tracking
│       ├── story-bible.md           # Living continuity document
│       ├── treatment.md             # Story treatment (at wrap-up, or imported seed)
│       ├── book.md                  # Compiled full book (generated on demand)
│       ├── chapters/
│       │   ├── 01-ch-a1b2c3d4.md   # Chapter files with YAML front matter + prose
│       │   └── ...
│       ├── planning/
│       │   ├── ch-a1b2c3d4-proposal.md   # Chapter proposal + handoff choices
│       │   ├── ch-a1b2c3d4-feedback.md   # User steering input (written outside sessions)
│       │   └── ...
│       └── branches/
│           └── br-[guid]/           # Alternate-timeline fork of the story
│               ├── story-bible.md
│               ├── chapters/
│               └── planning/
└── Archive/                         # Older book versions migrated from Chat
```

---

## Starting a Session

Open Claude Code in this directory and just talk to Claude. It handles all session types:

| What you say | What happens |
|---|---|
| `start a new book` | Claude asks for genre, premise, tone — then writes chapter 1 |
| `continue [book name]` | Claude resumes from the last handoff |
| `resume` | Full resume flow: reads manifest → bible → last chapters → handoff |
| `list books` | Shows all books with status and chapter count |
| `from treatment` | Starts a new pass using an existing treatment as the seed |

You can also fill out `Engine/new-book-template.md` and paste it in — Claude will skip whatever's already answered.

---

## Key Concepts

### Story Bible
A living `story-bible.md` file in each book directory. Claude rewrites it after every chapter. Contains: premise & tone, character registry with voice anchors, world rules, thematic threads, unresolved tensions, reader promises, and a timeline. This is how continuity survives across sessions.

### Manifest
`manifest.json` is the book's state machine — chapter registry, active branch, timestamps, word counts. Claude reads it at session start and updates it after every chapter.

### Planning Files
Each chapter has a `planning/ch-[guid]-proposal.md` that contains:
- **CHAPTER PROPOSAL** — beats, pacing, turning point assessment (written before drafting)
- **CHAPTER HANDOFF** — the exact choices or question presented to you (written after)

The handoff is the resume anchor. It's how `resume` reconstructs where you left off.

### Feedback Files
`planning/ch-[guid]-feedback.md` — write your steering here outside of a session (via the book viewer or manually). On next resume, Claude reads this and proceeds directly to writing the next chapter without waiting for input.

### Turning Points
Claude classifies each chapter's narrative weight:
- **Routine** — clear momentum, write and present A/B/C choices
- **Significant** — meaningful fork, make choices genuinely distinct  
- **Major turning point** — structural inflection; Claude pauses and asks openly instead of presenting options

### Branching
`branch here` or `what if instead...` forks the story into an alternate timeline. The new branch gets its own story bible and chapter files. Both timelines continue from there. Branches can be switched between or abandoned without losing anything.

---

## Book Viewer

Open `Engine/book-viewer.html` in a browser. It reads from `Books/` and renders chapters as formatted prose. Chapter prose does not appear in chat by default — only the scene summary and choices do. The viewer is the reading interface.

It also supports writing feedback files — leaving steering notes that Claude picks up on next resume.

---

## Utility Scripts

### guidgen.py
Generates the 8-character hex GUIDs used for all book/chapter/branch IDs.

```bash
python3 Engine/guidgen.py 1 bk    # one book GUID: bk-a1b2c3d4
python3 Engine/guidgen.py 5 ch    # five chapter GUIDs
python3 Engine/guidgen.py 1 br    # one branch GUID
```

### migrate-book.py
Splits a compiled `book.md` into individual v3 chapter files with YAML front matter, generates a manifest, and sets up the full directory structure. Useful for importing books that were written in Chat or as a single file.

```bash
python3 Engine/migrate-book.py Books/my-book/book.md \
    --title "My Novel" \
    --genre "Historical fiction" \
    --tone "Immersive, grounded" \
    --out Books/my-book/
```

---

## Commands (say these in chat)

| Command | Effect |
|---|---|
| `keep going` / `continue` | Claude picks the natural continuation |
| `compile book` | Generates/regenerates `book.md` from all chapter files |
| `show bible` | Displays the current story bible |
| `show branches` | Lists all branches with fork points |
| `branch here` | Forks the story at the current chapter |
| `switch to [branch]` | Changes the active branch |
| `who's who?` | Prints the dramatis personae |
| `where are we?` | Summarizes current story state from the bible |
| `enable debug mode` | Shows chapter proposals, bible diffs, file operations |
| `wrap up` | Writes a conclusion, generates treatment, compiles book, marks complete |

---

## Branch Model

The repo's branches are about **engine versions**, not books. The library of books is its own space — it is not enumerated here and does not belong to any particular engine branch.

- **`main`** — the stable, canonical engine. This is what new work orients against and what books should initialize from.
- **Engine feature branches** (e.g. `hi-story`) — in-progress engine variants with their own goals. `hi-story` in particular is working toward a distinct engine posture and is not a superset of `main`. Merged back into `main` only when stable.
- **`claude/*` branches** — ephemeral branches created by Claude Code review / PR workflows. Not intended for direct work.

**Working conventions (alpha posture):**
- Commit issue fixes and small changes directly to the working branch. Don't spin up sub-branches for individual issues.
- Only create a new branch when you're starting a genuinely distinct project (a new engine variant, a major rework, etc.).
- A book initialized while a given engine branch is active is effectively pinned to that engine version until you choose to update it.

**Future direction:** Issue #13 (backlogged) proposes a git-native backend where each book lives on its own `book/<slug>` branch, with the engine version pinned at branch-creation time. That model is **not** in effect yet — if you read it in an older issue or comment, treat it as aspirational. Today, books exist as folders under `Books/` on whatever branch they were created on; the long-term direction is to separate the library entirely from engine branches.

---

## Working on the Engine

The engine is the set of files under `Engine/` plus `CLAUDE.md`. To change how Claude behaves in a story session, edit `Engine/story-engine-v3.md` (the authoritative prompt) or the supporting scripts.

- **Small fixes and edits** — commit directly to the branch you're on (`main` for stable work, `hi-story` for the in-progress variant).
- **Larger reworks or experiments** — start a new engine feature branch off `main`. Merge back when stable.
- **Book initialization** should always happen from a stable branch (`main`). Books initialized mid-experiment inherit whatever engine state was live at the time.
- **Book viewer** (`Engine/book-viewer.html`) is a static file — open it in a browser, no build step.

---

## Issue Tracker

Issues are tracked on GitHub. Labels in active use:

| Label | Meaning |
|---|---|
| `high-priority` | Should be addressed soon; blocks other work or orientation |
| `backlog` | Tracked but not actively scheduled |
| `enhancement` | New feature or capability |
| `bug` | Something isn't behaving correctly |
| `documentation` | Docs, READMEs, contributor orientation |
| `question` | Open design question; discussion welcome |

When filing an issue, prefer concrete "what's needed" and "why" sections over open-ended discussion — the backlog is small enough that issues double as specs.

