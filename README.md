# Story Engine

A file-backed collaborative writing engine for Claude Code. Two engines share the same infrastructure: the **Story Engine** (collaborative fiction) and the **History Spelunking Engine** (collaborative non-fiction history exploration, research-driven, with web search).

Both engines share the same file-backed philosophy — persistent disk state, a living continuity document, resume-anywhere via handoff files, and a book viewer for reading. What differs is genre, vocabulary, and whether the model is inventing or researching.

**Status:** Alpha. Single-author project, actively developed. Interfaces and file layouts may still shift without deprecation notices.

**v4 shipped 2026-04-17.** Manifest engine, `/open` dispatcher, branch-worktree write flow, always-start-on-main, push-button chapter commit. The last v3 state is tagged [`v3-final`](https://github.com/parciesca/story-engine/releases/tag/v3-final).

---

## The Two Engines

| | **Story Engine** (`story-engine.md`) | **History Spelunking Engine** (`hi-story-engine.md`) |
|---|---|---|
| **Mode** | Collaborative fiction | Collaborative non-fiction |
| **Claude's role** | Co-author; writes, user steers | Curator; researches, writes, user follows curiosity |
| **Content origin** | Invented | Web-researched, fact-checked |
| **Library root** | `Books/` | `Books/` |
| **Continuity doc** | `story-bible.md` | `research-bible.md` |
| **Unit of work** | Chapters, with branches for alternate timelines | Chapters, with **addenda** for tangential deep dives |
| **Session trigger** | "start a new book", "continue [book]" | "start a new exploration", "continue [exploration]" |
| **Brief template** | `Engine/new-book-template.md` | `Engine/new-exploration-template.md` |

Both engines write to disk every chapter, read from disk on resume, and use the same slug-based identity scheme. The book viewer (`Engine/book-viewer.html`) renders both.

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
│   ├── story-engine.md              # Fiction engine prompt
│   ├── hi-story-engine.md           # History engine prompt
│   ├── book-viewer.html             # Local browser UI for reading chapters
│   ├── new-book-template.md         # Brief for starting a new fiction book
│   └── new-exploration-template.md  # Brief for starting a new history exploration
└── Books/
    └── [book-slug]/                 # All books (fiction and history), on book/<slug> branches
        ├── manifest.json
        ├── story-bible.md           # or research-bible.md for history explorations
        ├── chapters/
        ├── planning/
        ├── addenda/                 # History explorations only: tangential deep dives
        └── branches/                # Fiction only: alternate-timeline forks
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

Open `Engine/book-viewer.html` in a browser. It reads from `Books/` and renders chapters as formatted prose. Chapter prose does not appear in chat by default — only the summary and navigation options do. The viewer is the reading interface.

It also supports writing feedback files — leaving steering notes that Claude picks up on next resume.

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

The repo's branches are about **engine versions**, not books. Each book lives on its own `book/<slug>` branch and is separate from engine development branches.

- **`main`** — stable engine. Sessions always start here; the engine dispatches to `book/<slug>` for reads and writes.
- **`book/<slug>`** — data-only branches, one per book. Carry no `Engine/` directory. Created by the engine at book initialization.
- **`claude/*` branches** — ephemeral branches created by Claude Code review / PR workflows. Not intended for direct work.

**Working conventions (alpha posture):**
- Commit issue fixes and small changes directly to the working branch. Don't spin up sub-branches for individual issues.
- Only create a new branch when you're starting a genuinely distinct project (a new engine variant, a major rework, etc.).

---

## Working on the Engine

The engine is the set of files under `Engine/` plus `CLAUDE.md`. Which file to edit depends on which engine you're changing:

- **Fiction engine** — `Engine/story-engine.md`
- **History engine** — `Engine/hi-story-engine.md`
- **Shared infrastructure** — `Engine/book-viewer.html`, `Engine/scripts/commit-chapter.sh`

Conventions:

- **Small fixes and edits** — commit directly to `main`.
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
