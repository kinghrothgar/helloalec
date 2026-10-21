---
name: screenshots
description: "Reads macOS screenshots from ~/Pictures/screenshots and answers questions about them. Use when the user asks to look at, read, describe, or act on a screenshot, the latest screenshot, or the last N screenshots."
compatibility: opencode
---

# Screenshots

Takes the user's message as two parts: how many screenshots to look at,
and what to do with them.

## Parse the argument

- No count given (`look at the screenshot`, `what's wrong here`): N = 1,
  the most recent screenshot.
- A count (`last 2`, `last three`, `both`, `these 3`): N = that number.
- Everything else in the message is the task to carry out against the
  images.

## List

Run `scripts/screenshot-list -n N` (relative to this skill's directory).
It prints one line per screenshot, newest first: `mtime<TAB>path`.

Non-zero exit (folder missing, no images, not macOS): stop and show the
script's error message verbatim. Do not look for screenshots anywhere else.

## Read

Read each listed path with the read tool; it presents images directly.
Do not shell out to `cat`, `base64`, OCR tools, or `sips`.

## Then

Carry out the task on the images as if the user had attached them.

## Report

Start with one line naming the file(s) and their times, so the user can
confirm the right ones were picked:

```
Looked at: Screenshot 2026-10-16 at 1.11.39 PM.png (13:11:39), Screenshot 2026-10-16 at 1.11.28 PM.png (13:11:28)
```

Then the answer to the task.
