---
name: find-broll
description: Find or make B-roll for a video, one visual per noun phrase in the transcript. Tries three sources in order: a real clip of the person or product, a screen recording of the real website, then AI video generated in Google Flow (Omni 1.1 Flash). Keeps a provenance ledger so no scene repeats. Use when Ahmed says "find b-roll", "get footage for this", "record the website", "pull a clip of him", or when a short-form edit needs moving inserts.
---

# Find B-roll

Rules come from Nate Herk's playbook (`docs/herk-edit-kit/EDITING-PLAYBOOK.md`, B-roll section) and his `short-form-edit` skill. The Flow generation step is Ahmed's own route: no Kie.ai, no API key.

## Order (never skip down without a reason)

1. **Real clip** of the person, product or thing named.
2. **Screen recording** of the real site or app.
3. **Animated UI mock** (typing, rows ticking). Label it as an example.
4. **AI video from Flow**, only when nothing real exists.

Video beats images, always. An AI still used as B-roll is an error. Stills are only first or last frames for AI video.

## Step 0: plan (no downloads, no credits)

1. Read the transcript (`<videos_dir>/edit/transcripts/*.json`, check `transcription_source`).
2. List each noun phrase that needs a visual: anchor phrase, start time, source choice (1 to 4), why.
3. Show the list to Ahmed. Wait for "ok" before downloading, recording or generating anything.

## Source 1: real clip

- Prefer the person's own site, channel or an official media kit. Save the source URL.
- Download the full stream with `yt-dlp` into `<videos_dir>/edit/broll/downloads/`, then cut locally. Seeking over HTTP for a 3 s clip took 10+ minutes in Nate's tests.
- Ask before each download (filename, source, size).
- Rights: a short, clearly attributed excerpt is the lower-risk case. Say so to Ahmed when the clip is a named person's footage in a branded reel. His call, not yours.
- Never generate a likeness and present it as the real person. Never play an AI voiceover over footage of a real person talking.

## Source 2: website screen recording

- Use Claude in Chrome (his logged-in Chrome) or the built-in browser pane.
- Record the exact part being spoken about: zoom in, visible cursor, real scroll or click. Crop to the phrase, not the whole page.
- Close cookie and terms dialogs. Never click Accept.
- Docs sites often scroll an inner container. Scroll with the mouse wheel, not `window.scrollTo`.
- Capture frame by frame if the recorder outputs small video (high-DPR screens record CSS pixels).
- Never show credentials, tokens or private data in the capture.
- Logos: official asset only, source URL saved. Never draw or generate a brand mark. If none exists, use the plain name as text.

## Source 4: Flow AI video

Run through Google Flow in the browser. Rules and UI steps are in `../gbro-collage-broll/SKILL.md` (Gate 2 and Gate 3). Same hard rules apply:

- Never enter Ahmed's Google password. If Flow asks to sign in, stop and ask him.
- Check the credit cost line before each batch (12 credits per 720p 8 s clip on 2026-10-15). One test clip first.
- Ask before each download. Visible watermark stays OFF.
- Concrete metaphors work ("burning money" = a bill burning). Generic "person at a computer" reads as stock.
- Models often cut to a second camera angle around 2.5 to 3 s. Use only the first continuous seconds.
- Text on AI screens turns to gibberish. Keep screens small in frame. Check all four corners across the whole selected interval.
- Consecutive shots of the same person must match (outfit, room). Pass the previous frame as a reference.
- Gate every generation: Ahmed approves the idea before credits are spent.

## Ledger (required)

Write `<videos_dir>/edit/broll/footage-ledger.json`, one row per shot:

```json
{ "scene": "s03", "sourceSceneId": "gh-pricing-page", "asset": "broll/s03.mp4",
  "sha256": "<64 hex>", "sourceStart": 2.0, "sourceEnd": 3.6,
  "kind": "screen-recording|real-clip|ui-mock|flow-ai",
  "sourceUrl": "https://...", "framing": "9:16 contain, cursor visible" }
```

- Each scene is used once per reel. A new crop, speed, reverse or grade is not a new scene.
- Compute the hash with `sha256sum`. Keep authentic and AI footage separate in the totals.
- Validator logic lives in `.claude/skills/short-form-edit/scripts/validate-footage.mjs`. It expects a `plan.json` from `short-form-edit`; for a plain edit, apply the same checks by hand (no duplicate `sourceSceneId`, valid intervals, hash present).

## Finish

- Never invent numbers or results to decorate a claim.
- Contain framing by default. Check start, middle and end at phone size.
- Run `helpers/sync_to_drive.sh <videos_dir>` so the ledger and assets are backed up.
