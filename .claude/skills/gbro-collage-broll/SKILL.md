---
name: gbro-collage-broll
description: Turn a ~5 second voiceover line or abstract idea into an editorial halftone paper-collage B-roll clip that assembles itself from an empty color field. Use when Ahmed says "collage b-roll", "paper collage b-roll", "halftone collage", or wants one spoken line turned into a visual metaphor clip for educational videos or Reels. Runs in Google Flow through the browser (Nano Banana for the still, Omni 1.1 Flash Frames mode for the video), so there is no API key and no per-clip bill. Strict three-gate approval: metaphor, then still, then video.
---

# Collage B-roll (Flow edition)

Adapted from `pyang5166/gbro-collage-broll` (MIT). The original calls the Gemini API and Codex `image_gen`. This version drives Google Flow in the browser on Ahmed's Google AI Pro plan instead. The original files are kept in `references/` (`SKILL.original.md`, `original-scripts/`). Original prompt templates and QA rules still apply and are summarized below.

One spoken line becomes one sharp visual idea, then a 5 to 8 second silent clip where paper pieces slide in and assemble from an empty color field.

## Why Flow, not the API

- Ahmed's Google AI Pro plan includes Flow credits (1,050 on 2026-10-15). The API is billed separately.
- Flow has what the skill needs: Nano Banana for stills, and a **Frames** video mode with a First and a Last slot on **Omni 1.1 Flash**.
- Measured on 2026-10-15: Omni 1.1 Flash, 720p, 8s, x2 outputs = 24 credits (12 per clip). Image generation showed 0 credits. Re-check the cost line in the settings popover before each batch.

## Hard rules

- Never enter Ahmed's Google password. If Flow shows a sign-in page, stop and ask him to sign in himself in the browser.
- Three gates. Never skip one. Never generate video before the still is approved.
- Ask before downloading each file (a rule from the browser safety policy), unless Ahmed already approved that exact download in chat.
- Leave "visible watermark" OFF in Flow account details (it was off by default).
- Do not use credits for anything outside the approved item. One test clip first, then batch.
- Use the browser tools in this order: Claude in Chrome (his logged-in Chrome) if connected, otherwise the built-in browser pane signed in by Ahmed.

## Gate 1: Metaphor (no generation, no credits)

Compress the line into one visual proposition. Deliver per line:

- Core meaning, emotion, one-sentence visual idea
- 3 to 6 key objects (more makes assembly unstable)
- Background color (hex) and 1 to 2 accent colors
- Assembly order: structure, then subject or cards, then connectors, then action, then result

Stop. Wait for "ok", "approved", or per-item edits. Only approved items go to Gate 2.

Color guide (flat, bold field, change per meaning):
- burnt orange or red: time, labor, urgency
- mustard: tools, warnings, lost experience
- dark green: thinking, taste, system reset
- deep purple: rules, accumulated knowledge
- teal: judgment, collaboration, automation

## Gate 2: Still frame (Flow, Nano Banana)

1. Write the visual spec and image prompt (templates below).
2. In Flow: settings popover, tab **Изображение (Image)**, aspect **9:16**, model **Nano Banana 2.1**, outputs **x2**. Paste the prompt, generate.
3. Look at both results. Pick the better one or regenerate. Check the still QA list.
4. Download the chosen image into `<videos_dir>/edit/broll/<item>/last-frame-original.png` (ask first).
5. Show Ahmed the still. Stop. Wait for approval.

Still prompt template:

```text
Use case: ads-marketing
Asset type: final still frame for a 9:16 image-to-video B-roll clip
Primary request: Create a finished editorial paper-collage image expressing [one-sentence visual idea].
Scene/backdrop: perfectly flat [color] paper field [hex] with subtle uncoated paper fiber.
Style/medium: premium editorial stop-motion paper collage; black-and-white halftone photographic cut-outs mixed with selective [accent] colored cardstock.
Composition/framing: vertical 9:16 locked poster frame; central subject within the middle 70 percent; generous clean color-field negative space; 3-6 large separable paper groups for later assemble-from-empty animation.
Materials/textures: visible printed halftone dots, crisp machine-cut edges, thin warm-cream paper keylines, soft low-opacity physical drop shadows.
Constraints: [the relationship that must read at a glance].
Avoid: no typography, no readable letters, no numerals, no logos, no watermark, no UI, no subtitles, no glossy 3D, no photoreal environment, no clutter.
```

Still QA: metaphor reads instantly, subject centered, no fake text or logos, enough flat color for assembly, 3 to 6 clear groups, same texture across a batch with different colors.

## Gate 3: Video (Flow, Omni 1.1 Flash, Frames mode)

1. Prepare frames with ffmpeg (needs `ffmpeg`, already required by this repo):

```bash
# last frame: crop/scale approved still to 1080x1920
ffmpeg -y -i last-frame-original.png \
  -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920" last-frame.png
# first frame: empty paper field, same hex as the still background
ffmpeg -y -f lavfi -i color=c=0xRRGGBB:s=1080x1920 -frames:v 1 first-frame.png
```

2. In Flow: settings popover, tab **Видео (Video)**, mode **Кадры (Frames)**, aspect **9:16**, model **Omni 1.1 Flash**, **720p**, duration **6 s** (use 8 s only if the metaphor needs it), outputs **x2**.
3. Put `first-frame.png` in the **Первый (First)** slot and `last-frame.png` in the **Последний (Last)** slot, using the file upload control. Do not click the native file picker; use the page's file input.
4. Paste the motion prompt (template below), then press generate.
5. Wait for both results. Pick the better one.
6. Ask, then download as `final.mp4` into `<videos_dir>/edit/broll/<item>/`.
7. Strip audio, run QA:

```bash
ffmpeg -y -i final.mp4 -map 0:v:0 -c:v copy -an final-noaudio.mp4
ffmpeg -y -i final-noaudio.mp4 -vf "fps=1,scale=270:480,tile=6x1" -frames:v 1 contact-sheet.jpg
```

Motion prompt template:

```text
Paper-collage stop-motion assembly, using Image 1 as the exact empty first frame and Image 2 as the exact completed last frame. In one continuous locked-off vertical shot, open on the empty flat [color] paper field.

Assemble the scene piece by piece with crisp physical stop-motion timing: [3-6 elements, in order: slide in, snap into place, connect, finish the action]. End by holding the supplied completed composition.

Preserve the exact 9:16 framing, [hex] color field, colored cardstock accents, uncoated paper grain, halftone dots, cream keylines, crisp cut edges and soft shadows. Restrained tactile 2D paper craft only.

No scene cuts, no camera movement, no zoom, no morphing, no new objects, no text, no letters, no numbers, no logos, no watermark, no UI, no sound.
```

Video QA (check the whole assembly, not only the end):
- First frame close to an empty color field (a sliver of paper at the edge is fine)
- Middle shows pieces entering one by one, not a fade
- No cuts, zoom, 3D look or photoreal drift
- No fake text, logo, watermark or UI
- Last frame matches the approved still (small pose drift is fine if the meaning holds)
- Silent output (the Flow clip has audio; strip it)

Common fixes:
- Weak assembly: fewer objects, explicit "slides in / snaps into place" order
- Last frame drifts: repeat "Image 2 is the exact completed last frame" and "End by holding the supplied completed composition"
- Fake text appears: go back to the still, do not patch with the video prompt
- One clip failed: rerun only that item

## Folder layout

All outputs live outside this repo, in `<videos_dir>/edit/broll/`:

```text
broll/
  01-concept-name/
    brief.md
    last-frame-original.png
    first-frame.png
    last-frame.png
    final.mp4
    final-noaudio.mp4
    contact-sheet.jpg
```

## Use in the edit

- Delivered clip is 9:16, silent, 720p, 6 to 8 s. Lay it under the talking head as B-roll.
- For strict control of layers, camera moves or a real empty first frame, use HyperFrames or Remotion instead.
- Keep Ahmed's personal-brand palette in mind. Pick background colors per meaning, not from the VANTIQ agency palette.

## Fallback: API route

If Flow credits run out or the UI changes, the original API scripts are in `references/original-scripts/` (needs `GEMINI_API_KEY`, billed per use). Do not use unless Ahmed asks.

## Verified on the first test run (2026-10-15)

- No file upload is needed. The First and Last slots open a picker of the project's own images, so make both frames inside Flow.
- Make the empty First frame with Nano Banana: attach the approved still via the "+" button and prompt "use this exact image but remove every object, leave only the flat [color] paper field". This keeps the background tone identical, which a flat ffmpeg color would not.
- Image generation (Nano Banana, x2) costs 0 credits. Omni 1.1 Flash 720p 10 s x1 = 15 credits (8 s x2 = 24).
- A 10 s clip took about 2 minutes to render. Output is 720x1280, 10 s.
- Settings (Image/Video, mode, aspect, duration, outputs) persist in the popover between generations. Re-check them before each run.
- To QA without downloading, open the clip and seek the `<video>` element with JavaScript (`currentTime`), then screenshot.
- Still unverified: the download button and any quality prompt.
- Flow UI is Russian for Ahmed's account. Button names above are given in both languages.
