# Story Engine — `hi-story` branch

A file-backed collaborative writing engine for Claude Code. This branch extends the project beyond fiction: alongside the original **Story Engine** (collaborative novels), it adds a **History Spelunking Engine** (collaborative non-fiction history exploration, research-driven, with web search).

Both engines share the same file-backed philosophy — persistent disk state, a living continuity document, resume-anywhere via handoff files, and a book viewer for reading. What differs is genre, vocabulary, and whether the model is inventing or researching.

**Status:** Alpha. Single-author project, actively developed. `hi-story` is the working branch where the History engine is being built out toward an eventual merge into `main`. Interfaces and file layouts may still shift without deprecation notices.

---

## The Two Engines

| | **Story Engine** (`story-engine-v3.md`) | **History Spelunking Engine** (`hi-story-engine-v3.md`) |
|---|---|---|
| **Mode** | Collaborative fiction | Collaborative non-fiction |
| **Claude's role** | Co-author; writes, user steers | Curator; researches, writes, user follows curiosity |
| **Content origin** | Invented | Web-researched, fact-checked |
| **Library root** | `Books/` | `History/` |
| **Continuity doc** | `story-bible.md` | `research-bible.md` |
| **Unit of work** | Chapters, with branches for alternate timelines | Chapters, with **addenda** for tangential deep dives |
| **Session trigger** | "start a new book", "continue [book]" | "start a new exploration", "continue [exploration]" |
| **Brief template** | `Engine/new-book-template.md` | `Engine/new-exploration-template.md` |

Both engines write to disk every chapter, read from disk on resume, and use the same GUID scheme (`bk-`, `ch-`, plus `br-` for story branches and `ad-` for history addenda). The book viewer (`Engine/book-viewer.html`) renders both.

> **Known gap on this branch:** `CLAUDE.md` currently points Claude at `story-engine-v3.md` only. Until that's updated, starting a history session explicitly ("start a new exploration" or similar) is the clearest way to land on the right engine.

---

## How It Works

Every Claude Code session in this project is a writing session. Claude reads the appropriate engine prompt, loads the book or exploration state from disk, and picks up exactly where you left off.

**The loop (fiction):**
1. Claude reads the manifest, story bible, and recent chapters
2. You give a direction — a letter choice, a paragraph of steering, or just "keep going"
3. Claude writes the next chapter and saves all files
4. Claude presents a scene summary and choices for the next chapter

**The loop (history):**
1. Claude reads the manifest, research bible, and recent chapters
2. You pick a navigation thread — or say "addendum: [topic]" to fork into a rabbit hole
3. Claude researches via web search, folding findings into the bible incrementally, then writes the chapter or addendum
4. Claude presents a summary hook and navigation options

Prose is written to disk and read back from there — not held in chat memory. Stories and explorations can be as long as they need to be.

---

## Repository Structure

```
story-engine/
├── CLAUDE.md                        # Claude Code session config
├── Engine/
│   ├── story-engine-v3.md           # Fiction engine prompt
│   ├── hi-story-engine-v3.md        # History engine prompt (this branch)
│   ├── book-viewer.html             # Local browser UI for reading chapters
│   ├── new-book-template.md         # Brief for starting a new fiction book
│   ├── new-exploration-template.md  # Brief for starting a new history exploration
│   ├── guidgen.py                   # GUID generator (bk/ch/br/ad)
│   ├── migrate-book.py              # Migration: compiled book.md → v3 chapter files
│   └── Archive/                     # Previous engine versions (including hi-story-engine-v1)
├── Books/
│   └── [book-slug]/                 # Fiction books
│       ├── manifest.json
│       ├── story-bible.md
│       ├── chapters/
│       ├── planning/
│       └── branches/                # Alternate-timeline forks
├── History/
│   └── [exploration-slug]/          # History explorations
│       ├── manifest.json
│       ├── research-bible.md
│       ├── chapters/
│       ├── addenda/                 # Tangential deep dives
│       └── planning/
└── Archive/                         # Older book versions migrated from Chat
```

---

## Starting a Session

Open Claude Code in this directory and talk to Claude.

**Fiction:**

| What you say | What happens |
|---|---|
| `start a new book` | Claude asks for genre, premise, tone — then writes chapter 1 |
| `continue [book name]` | Claude resumes from the last handoff |
| `resume` | Full resume flow: manifest → bible → last chapters → handoff |
| `list books` | Shows all fiction books with status |
| `from treatment` | Starts a new pass using an existing treatment as the seed |

**History:**

| What you say | What happens |
|---|---|
| `start a new exploration` | Claude asks for topic, period, angle — researches and writes chapter 1 |
| `continue [exploration name]` | Claude resumes from the last handoff |
| `addendum: [topic]` | Forks into a tangential deep dive without advancing the main chapter count |
| `list explorations` | Shows all history explorations with status |
| `who's who?` | Prints key figures from the research bible |
| `where are we?` | Summarizes the exploration map |

You can also fill out the matching brief template (`new-book-template.md` or `new-exploration-template.md`) and paste it in.

---

## Key Concepts

### Continuity Documents

Every book or exploration has a living continuity document, rewritten after every chapter. It's how context survives across sessions.

- **Story Bible** (`story-bible.md`) — premise, tone, character registry with voice anchors, world rules, thematic threads, unresolved tensions, reader promises, timeline.
- **Research Bible** (`research-bible.md`) — subject and scope, key figures, established context, thematic threads, **threads to pull** (spotted rabbit holes), exploration map, open questions, sources of note.

### Manifest
`manifest.json` is the state machine — chapter registry, active branch or current item, timestamps, word counts. Read at session start, updated after every chapter.

### Planning Files
Each chapter (and addendum) has a `planning/ch-[guid]-proposal.md` containing:
- **PROPOSAL** — beats/research focus, approach (written before drafting)
- **HANDOFF** — the exact choices or navigation options presented (written after)

The handoff is the resume anchor.

### Feedback Files
`planning/ch-[guid]-feedback.md` — write steering outside of a session (via the book viewer or manually). On next resume, Claude reads this and proceeds directly to writing without waiting for input.

### Turning Points (fiction only)
Claude classifies each chapter's narrative weight:
- **Routine** — clear momentum, present A/B/C choices
- **Significant** — meaningful fork, choices genuinely distinct
- **Major turning point** — structural inflection; Claude pauses and asks openly

### Branching (fiction) vs Addenda (history)
- **Branching** forks a fiction story into an alternate timeline with its own bible and chapters. Both timelines continue from there.
- **Addenda** let a history exploration follow a tangent without derailing the main thread. An addendum records `after_chapter`, has its own sequence (Addendum 1, 2…), and does not increment the chapter count. Addenda can stack off other addenda.

### Research Discipline (history only)
The history engine uses web search before every chapter, folding findings into the research bible **incrementally** — never holding research in context waiting for a complete picture. If a session runs out of room mid-research, the bible already reflects what was gathered.

---

## Book Viewer

Open `Engine/book-viewer.html` in a browser. It reads from `Books/` and `History/` and renders chapters as formatted prose. Chapter prose does not appear in chat by default — only the summary and navigation options do. The viewer is the reading interface.

It also supports writing feedback files — leaving steering notes that Claude picks up on next resume.

---

## Utility Scripts

### guidgen.py
Generates the 8-character hex GUIDs used for all IDs.

```bash
python3 Engine/guidgen.py 1 bk    # one book GUID: bk-a1b2c3d4
python3 Engine/guidgen.py 5 ch    # five chapter GUIDs
python3 Engine/guidgen.py 1 br    # one fiction branch GUID
python3 Engine/guidgen.py 1 ad    # one history addendum GUID
```

### migrate-book.py
Splits a compiled `book.md` into individual v3 chapter files with YAML front matter, generates a manifest, and sets up the full directory structure. Originally for fiction; may need extension for history-engine explorations.

---

## Commands (say these in chat)

Shared:

| Command | Effect |
|---|---|
| `keep going` / `continue` | Natural continuation |
| `compile book` | Regenerates `book.md` from all chapter files |
| `show bible` | Displays the current continuity document |
| `enable debug mode` | Shows proposals, bible diffs, file operations |
| `wrap up` | Writes a conclusion, generates treatment, compiles, marks complete |

Fiction-only:

| Command | Effect |
|---|---|
| `show branches` | Lists all story branches with fork points |
| `branch here` | Forks the story at the current chapter |
| `switch to [branch]` | Changes the active branch |
| `who's who?` | Prints dramatis personae |

History-only:

| Command | Effect |
|---|---|
| `addendum: [topic]` | Forks into a tangential deep dive |
| `who's who?` | Prints key figures from the research bible |
| `where are we?` | Displays the exploration map |

---

## Branch Model

The repo's branches are about **engine versions**, not books. The library of books and explorations is its own space — it is not enumerated here and does not belong to any particular engine branch.

- **`main`** — stable fiction engine only. Books initialize from here when the history engine isn't needed.
- **`hi-story`** *(this branch)* — adds the History Spelunking Engine alongside the fiction engine. Working toward an eventual merge into `main` once the history engine is stable and CLAUDE.md / session-routing is figured out.
- **`claude/*` branches** — ephemeral branches created by Claude Code review / PR workflows. Not intended for direct work.

**Working conventions (alpha posture):**
- Commit issue fixes and small changes directly to the working branch. Don't spin up sub-branches for individual issues.
- Only create a new branch when you're starting a genuinely distinct project (a new engine variant, a major rework, etc.).
- A book or exploration initialized while a given engine branch is active is effectively pinned to that engine version until you choose to update it.

**Future direction:** Issue #13 (backlogged) proposes a git-native backend where each book lives on its own `book/<slug>` branch, with the engine version pinned at branch-creation time. That model is **not** in effect yet. Today, books and explorations exist as folders under `Books/` and `History/` on whatever branch they were created on; the long-term direction is to separate the library entirely from engine branches.

---

## Working on the Engine

The engine is the set of files under `Engine/` plus `CLAUDE.md`. Which file to edit depends on which engine you're changing:

- **Fiction engine** — `Engine/story-engine-v3.md`
- **History engine** — `Engine/hi-story-engine-v3.md`
- **Shared infrastructure** — `Engine/book-viewer.html`, `Engine/guidgen.py`, `Engine/migrate-book.py`

Conventions:

- **Small fixes and edits** — commit directly to `hi-story` (this branch) or `main`, whichever the change belongs to.
- **Larger reworks or experiments** — start a new engine feature branch off `main`. Merge back when stable.
- **Book/exploration initialization** should always happen from a stable engine state — don't initialize new work mid-experiment unless you're deliberately pinning to that in-progress version.
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
