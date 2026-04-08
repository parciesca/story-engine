# Story Engine

A file-backed collaborative novel engine for Claude Code. You and Claude co-author books together — Claude writes, you steer. Stories persist across sessions in plain files so nothing is lost when context windows close.

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

## Active Books

| Title | Genre | Chapters | Status |
|---|---|---|---|
| Alone on the Bosphorus | Historical fiction | 12 | Active |
| Creation Beyond Existence | Hard sci-fi | 22 | Active |
| Load-Bearing | — | 1 | Active |
| The Burn Pattern | — | 1 | Active |
| The Physick Garden | — | 2 | Active |
| The Winding | — | 1 | Active |
