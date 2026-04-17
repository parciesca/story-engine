# Engine Roadmap

Snapshot of planning state as of 2026-04-14. Captures what's low-hanging, the rough order of the filed issues, and known gaps. Not a commitment — a map.

## Q1: Low-hanging engine fruit

Small, independent cleanups worth doing any time. None require the #22 vision work to land first.

1. **Commit after each chapter write** — filed as #28. Five-line prompt change, big usability win.
2. **Update File System Architecture section.** `Engine/story-engine.md` lines 19–43 still describe the pre-#17/#19 GUID + Books/History split. Reality now: one book per `book/<slug>` branch, `main` is engine-only. Rewrite to match.
3. **"List books" uses git, not filesystem.** Line 482 and 635 of the fiction engine tell the engine to ls `Books/`. On a book branch there's only one book; the real book catalog is `git branch -r --list 'origin/book/*'`. Update the prompt to use that on new-book entry points.
4. **Archive path.** Line 640 references archiving books into an `Archive/` folder. With the branch-per-book layout, archive semantics need redefining (see Q3 gap). At minimum, stop telling the engine to move files into a folder that doesn't exist on a book branch.
5. **Close #17, #19, #20.** All three are implemented and merged. Housekeeping.
6. **Verify #2 (GUID manual approval).** GUIDs were dropped in #17 — #2 may already be moot. Confirm and close if so.

## Q2: Roadmap order

Rough dependency tiers for the open issues. Within a tier, pick by appetite.

### Tier 0 — housekeeping (Q1 items above)

#28, engine prompt rewrite for post-#19 reality, close #17/#19/#20, verify #2.

### Tier 1 — foundation

- **#6** — feedback discovery + classification + consumed-marker. Everything in the feedback family builds on this.
- **#23** — branch-aware init router. Everything in the #22 vision builds on this.

These two are independent and can be worked in either order or in parallel.

### Tier 2 — middle

- **#7** — retrospective feedback disposition UX (needs #6)
- **#24** — resumable new-book progressive commits (needs #23 for the resume-detection side)
- **#25** — port feedback architecture into the fiction engine (needs #6, #7)

### Tier 3 — top

- **#8** — chapter rewrite (needs #7)
- **#9** — deferred feedback ledger (needs #7)
- **#10** — orphan feedback handling (needs #6, #7)
- **#11** — viewer alignment with feedback architecture (needs #6)
- **#26** — treatment-classified feedback + git-branch what-if (needs #6, #7, #25)

### Tier 4 — independent tracks

- **#27** — viewer GitHub REST API integration. No hard dependency on the feedback family; can land any time.
- **#3** — viewer History support. Mostly obviated by #19 but worth a re-read.
- **#4** — hi-story engine outputting prose to chat. Bug fix, independent.
- **#12** — research-grounded craft improvements. Ongoing, not blocking.

### Tier 5 — backlog

- **#21** — library branch aggregator. Explicitly backlog.
- **#13** — git-as-backend research issue. Largely absorbed into #22 and children; keep open as the research thread.
- **#22** — parent tracker. Stays open until all children close.

## Q3: Gaps in the roadmap

Things that aren't filed and probably should be, or policy decisions that haven't been written down.

1. **Engine prompt alignment with post-#19 reality.** The fiction engine prompt still talks about `Books/` + `History/` + GUIDs in places. Rolled into Q1 items 2–4. No separate issue needed yet; one housekeeping PR covers it.

2. **Engine updates to book branches — policy.** *Resolved by user decision:* book branches are the user's problem. When engine changes land on `main`, the book owner merges `main` into their book branch and handles any migration the book needs (e.g. manifest schema changes, new required files). No automated migration tooling. No separate issue needed.

3. **Archive semantics under branch-per-book.** With `Archive/` being a folder under `main` that book branches don't see, and books living on their own branches, "archive" probably means one of: (a) rename the branch `archive/<slug>`, (b) merge the branch to a long-lived `archive` branch, (c) just mark manifest.status=archived and leave the branch where it is. Worth a small issue to decide. Not urgent.

4. **What happens when you want to abandon a partial new-book.** Flagged as an open question in #24 but not filed separately. If #24 ships and abandonment turns out to be painful, file then.

## Notes

- Current branch: `book/alone-on-the-bosphorus`. Chapter 13 is the last written chapter per the manifest. Feedback for Ch 12 (a single letter "B") is still pending disposition — that's the natural next reading/writing session, independent of any engine work above.
- The vision work (#22 and children) is a good chunk of engineering. The Q1 housekeeping is hours, not days. Doing Q1 first before starting Tier 1 is the right sequencing.
