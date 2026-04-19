# Book Viewer

`book-viewer.html` is a static, single-file reader for the books produced by this
engine. It runs entirely in the browser — no backend. It can read books from
either a local checkout (via the File System Access API) or directly from GitHub
over the REST API.

## Two sources

**Browse on GitHub (default)** — lists every `book/*` branch of the configured
repository, reads each book's `manifest.json` at its branch ref, and loads
chapters, the story bible, and planning files on demand. Anonymous requests
work out of the box (60 requests/hr per IP). Adding a personal access token in
Settings raises the limit to 5000/hr and enables saving feedback.

**Open from Disk** — pick a local `Books/` directory via the browser directory
picker (Chrome/Edge only). Reads and writes through the directory handle. No
network calls.

## Configuring the repo (forkers)

The viewer resolves the target repository in this order:

1. **Settings override** — whatever you save in the viewer's Settings modal
   (stored in `localStorage`). Always wins.
2. **URL auto-detect** — if the viewer is served from
   `<owner>.github.io/<repo>/...`, `owner/repo` is inferred from the URL.
   This means a fork hosted on the fork's own GitHub Pages "just works" with
   no edits.
3. **`Engine/viewer-config.json`** — a tiny JSON file checked into the repo:
   ```json
   { "repo": "parciesca/story-engine" }
   ```
   Forkers who don't host on GitHub Pages can change this one line and commit.
4. **First-run prompt** — if none of the above resolves a repo, the viewer
   opens Settings on load and asks the user to pick one.

## Feedback writes

Saving feedback from the GitHub source issues a `PUT /repos/{o}/{r}/contents/{path}`
against `Books/<slug>/planning/<id>-feedback.md` on branch `book/<slug>`. This
commits directly to the book branch with the PAT holder as the author. A token
is required — without one, the feedback panel surfaces a link to Settings
instead of attempting the write.

The token is stored in `localStorage` only. It is never transmitted anywhere
except `api.github.com`. Clearing it in Settings removes the local copy; revoke
the token on github.com/settings/tokens to invalidate it globally.

## What a forker typically does

- Fork the repo.
- Either:
  - Serve `Engine/book-viewer.html` from the fork's GitHub Pages (zero config), **or**
  - Edit `Engine/viewer-config.json` to point at your fork and commit.
- Open the viewer. Create a fine-grained PAT scoped to your fork with
  `Contents: Read and write` if you want to save feedback.
