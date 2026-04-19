# File Formats — story-engine

Reference for the file shapes this engine reads and writes inside `$LIBRARY_ROOT/Books/<slug>/`. SKILL.md links here from the write flow; open when you need the exact structure.

For manifest shape see `manifest-schema.md`.

---

## Chapter file — `chapters/NN.md`

Zero-padded sequence number (`01.md`, `02.md`, `13.md`). YAML frontmatter followed by prose:

```markdown
---
chapter: 1
title: "Chapter Title"
branch: main
written: 2026-04-06
word_count: 1050
---

[Chapter prose here]
```

Branch chapters live under `branches/<branch-slug>/chapters/NN.md` with the same shape. Numbers collide across branches by design — they're in different directories.

---

## Planning file — `planning/NN-proposal.md`

One file per chapter, number matches the chapter it belongs to. Two sections written at different points in the chapter lifecycle; both accumulate in the same file — never overwritten.

```
CHAPTER PROPOSAL
  Chapter: [number]
  Branch: [branch slug]
  Follows from: [user's choice/direction]
  This chapter accomplishes: [1-2 sentences]
  Key beats: [3-6 moments to hit]
  Pacing note: [tension level, tempo]
  Story bible implications: [what changes after this chapter]
  Turning point assessment: [routine / significant / major turning point]

---

CHAPTER HANDOFF
  Type: [multiple-choice / turning-point-pause]
  Written: [date]

  [For multiple-choice: the exact A/B/C/D options as presented to the user.
   For turning-point-pause: the exact question or prompt given to the user.
   Copy verbatim — this is the resume anchor for the next session.]
```

The **PROPOSAL** is written before drafting. The **HANDOFF** is written after presenting the chapter — it must be the text the user actually saw, verbatim. The HANDOFF is the resume anchor; without it, resume has nothing to orient against.

Branch planning files live at `branches/<branch-slug>/planning/NN-proposal.md`.

---

## Feedback file — `planning/NN-feedback.md`

One file per chapter, number matches the chapter the feedback **responds to**. Contains the user's steering response to a CHAPTER HANDOFF — the same kind of input they would type in chat (a letter choice, custom direction, or open-ended steering).

```
CHAPTER FEEDBACK
  For: NN
  Written: YYYY-MM-DD

[User's verbatim response to the handoff]
```

`NN` is the chapter number the feedback responds to, zero-padded (`01`, `02`, `13`).

### Who writes feedback files

Two paths produce them:

1. **The book viewer** — when the user steers between sessions, the viewer commits a feedback file directly to `book/<slug>`.
2. **The engine** — when the user steers in chat in response to the prior chapter's handoff, the engine writes the user's message verbatim as part of the next chapter's write pass.

### Engine write rules

- Write only if the file does not already exist. If the viewer already wrote one, trust it — **do not overwrite**.
- Write the user's message **verbatim**. A letter choice (`"B"`), `"keep going"`, or a full direction paragraph all go in as-is.
- Use the exact format above.
- Stage it in the same commit as the next chapter — no separate commit.
- Off-book / meta chat ("show bible", "who's who?", tonal notes between chapters) is not handoff steering and does not produce a feedback file.

Outside this carve-out, feedback files are read-only for the engine — never overwrite or modify them. They are consumed during resume.

---

## Story bible — `story-bible.md`

Plain markdown (no frontmatter), rewritten after every chapter. Structure:

```
STORY BIBLE
============

PREMISE & TONE
  Genre: [established at init]
  Tone: [established at init, can evolve]
  Core premise: [1-2 sentence distillation]

DRAMATIS PERSONAE
  [Name] — [Role/identity]. [Voice anchor: a line or behavioral note
    that captures how this character speaks/acts distinctly].
    [Status: active/deceased/departed/unknown]
  ...

WORLD RULES
  [Things established as true in this world. Physics, magic systems,
   technology, social structures — whatever the story has committed to.]
  ...

THEMATIC THREADS
  [Themes that have emerged — not imposed, but observed from what the
   story is actually doing. Updated as the story reveals itself.]
  ...

UNRESOLVED TENSIONS
  [Open questions, dangling threads, promises made to the reader that
   haven't been paid off yet. This is a checklist — things here should
   eventually be addressed or deliberately left ambiguous.]
  ...

TIMELINE & STATE
  Current location: [where we are]
  Inventory/resources: [if relevant to genre]
  Time position: [where we are chronologically]
  Key events so far: [1-line summaries per chapter]
  ...

READER PROMISES
  [Things the narrative has set up that the reader will expect payoff
   for. Chekhov's guns. Foreshadowing. Character arcs in motion.
   Different from "unresolved tensions" — these are structural
   commitments the story has made.]
  ...
```

**Which bible to read:** check `active_branch` in the manifest. If `"main"`, read `story-bible.md` in the book root. Otherwise read `branches/<branch-slug>/story-bible.md`.

---

## Treatment — `treatment.md`

Written at wrap-up — captures what the story *became*, not what it was planned to be. Keep under 1500 words. See the Wrap-Up section of SKILL.md for structure.

---

## Compiled book — `book.md`

Regenerated on demand by "compile book". Concatenates chapter files in order with chapter headings and a title page. Always regenerable from chapter files — not a source of truth.
