# Story Engine

Two Claude Code skills for collaborative long-form writing: the **Story Engine** (fiction) and the **Hi-Story Engine** (non-fiction history exploration, research-driven with web search).

Books are stored as git branches (`book/<slug>`). Any git repo with `book/<slug>` branches is a compatible library. This repo doubles as the skill source tree and as the author's own library — the author's books live on `book/<slug>` branches here.

**Status:** Alpha. Single-author project, actively developed.

---

## Install

```bash
git clone https://github.com/parciesca/story-engine.git
ln -s <repo>/skills/story-engine ~/.claude/skills/story-engine
ln -s <repo>/skills/hi-story-engine ~/.claude/skills/hi-story-engine
```

Or copy instead of symlink. Then invoke explicitly — skills do not auto-invoke:

```
/story-engine
/hi-story-engine
```

---

## Pointing the skill at a library

By default the skill uses whichever git repo you're in when you invoke it. Three equivalent ways to target a specific library:

1. `cd` into any git repo with `book/<slug>` branches and invoke the skill.
2. Pass the path as a skill argument: `/story-engine /path/to/library-repo`
3. Set `LIBRARY_ROOT=/path/to/library-repo` in the environment before invoking.

Any git repo with `book/<slug>` branches qualifies. No required directory structure on `main`. The skill discovers books by enumerating branches.

A library repo benefits from a one-liner `CLAUDE.md` — `This is a story library. Invoke /story-engine to work on books.` — for discoverability, but it's not required.

---

## The Two Engines

| | Story Engine | Hi-Story Engine |
|---|---|---|
| **Mode** | Collaborative fiction | Collaborative non-fiction |
| **Claude's role** | Co-author; writes, user steers | Curator; researches, writes, user follows curiosity |
| **Content origin** | Invented | Web-researched, fact-checked |
| **Continuity doc** | `story-bible.md` | `research-bible.md` |
| **Unit of work** | Chapters + alternate-timeline branches | Chapters + tangential addenda |

---

## How It Works

Prose is written to disk on a `book/<slug>` branch, not held in chat. Sessions resume anywhere via a handoff file.

**Fiction loop:**
1. Claude reads the manifest, story bible, and recent chapters
2. You give direction — a letter choice, a paragraph of steering, or "keep going"
3. Claude writes the chapter and saves all files
4. Claude presents a scene summary and choices for the next chapter

**History loop:**
1. Claude reads the manifest, research bible, and recent chapters
2. You pick a navigation thread — or say `addendum: [topic]` to fork into a rabbit hole
3. Claude researches via web search, folds findings into the bible incrementally, then writes the chapter
4. Claude presents a summary hook and navigation options

---

## Key Concepts

**Manifest** (`manifest.json`) — state machine: chapter registry, active branch, timestamps, word counts. Read at session start, updated after every chapter.

**Continuity document** — living document rewritten after every chapter. How context survives across sessions.
- Story Bible (`story-bible.md`) — premise, tone, character registry, world rules, thematic threads, timeline.
- Research Bible (`research-bible.md`) — subject and scope, key figures, established context, threads to pull, open questions.

**Planning files** — `planning/ch-[guid]-proposal.md` — proposal written before drafting, handoff written after. The handoff is the resume anchor.

**Feedback files** — `planning/ch-[guid]-feedback.md` — leave steering between sessions. On next resume, Claude reads it and writes without waiting for input.

**Turning points (fiction)** — Claude classifies each chapter as Routine, Significant, or Major Turning Point, and paces how much it pauses for steering accordingly.

**Branching (fiction)** — forks a story into an alternate timeline. Both timelines continue independently from the fork point.

**Addenda (history)** — tangential deep dives that record `after_chapter` and do not increment the chapter count. Addenda can stack off other addenda.

---

## Commands

Shared:

| Command | Effect |
|---|---|
| `resume` | Full resume flow: manifest → bible → last chapters → handoff |
| `list books` | Shows all books with status |
| `keep going` / `continue` | Natural continuation |
| `compile book` | Regenerates `book.md` from all chapter files |
| `show bible` | Displays the current continuity document |
| `enable debug mode` | Shows proposals, bible diffs, file operations |
| `wrap up` | Writes a conclusion, generates treatment, compiles, marks complete |

Fiction-only:

| Command | Effect |
|---|---|
| `branch here` | Forks the story at the current chapter |
| `switch to [branch]` | Changes the active story branch |
| `show branches` | Lists all story branches with fork points |
| `who's who?` | Prints dramatis personae |

History-only:

| Command | Effect |
|---|---|
| `addendum: [topic]` | Forks into a tangential deep dive |
| `who's who?` | Prints key figures from the research bible |
| `where are we?` | Displays the exploration map |

---

## Repo Layout

```
story-engine/
├── skills/
│   ├── story-engine/      # installable Claude Code skill (fiction)
│   └── hi-story-engine/   # installable Claude Code skill (history)
├── viewer/                # static book reader (browser)
├── CLAUDE.md
└── README.md
```

`book/<slug>` branches carry book data; `main` carries the skill source.

---

## Branch Model

- **`main`** — skill source. Sessions always start here.
- **`book/<slug>`** — data-only branches, one per book. Created by the engine at book initialization.
- Engine development branches (e.g. `v5`) merge to `main` on release.

The last v3 state is tagged [`v3-final`](https://github.com/parciesca/story-engine/releases/tag/v3-final). v4 shipped 2026-04-17.

---

## Working on the Engine

Edit files under `skills/story-engine/` or `skills/hi-story-engine/`. Both skill directories are intentionally duplicated — shared content drifts independently rather than being symlinked.

| What to change | Where |
|---|---|
| Fiction engine behavior | `skills/story-engine/SKILL.md` |
| History engine behavior | `skills/hi-story-engine/SKILL.md` |
| Chapter commit script | `skills/<name>/scripts/commit-chapter.sh` |
| Manifest schema | `skills/<name>/manifest-schema.md` |
| File formats | `skills/<name>/file-formats.md` |

Small fixes commit directly to `main`. Larger reworks go on a branch and merge on release.

---

## Issue Tracker

Issues are tracked on GitHub. Labels in active use:

| Label | Meaning |
|---|---|
| `high-priority` | Blocks other work or orientation |
| `backlog` | Tracked but not actively scheduled |
| `enhancement` | New feature or capability |
| `bug` | Something isn't behaving correctly |
| `documentation` | Docs, READMEs, contributor orientation |
