---
name: clawd-animator
description: Make hand-painted cartoon animation clips (p5.js + p5.brush, character Clawd) for educational videos. Use when Ahmed wants an animated B-roll, explainer cartoon or illustrated scene instead of footage or motion graphics.
---

# Clawd animator

Vendored from `JohnHeibel/ClaudeAnimationBase` (MIT) into `animation/` in this repo.

## When to use
- Storytelling or metaphor shots: a character acts something out.
- Not for captions, charts, diagrams or UI mockups. Use Remotion or HyperFrames for those.

## How
1. Read `animation/ANIMATION_GUIDE.md` fully. It holds the rules, workflow and API.
2. Write the storyboard in chat first and get Ahmed's yes. Do not commit it as a file.
3. Put the scene in `animation/src/scenes/<name>.js`, swap the script tag in `animation/studio.html`, set `duration` and `bpm` in `animation/src/config.js`.
4. Review with contact sheets and strips (commands in the guide), then render:
   `node render.mjs --clip --chrome="C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" --out=<videos_dir>/edit/clawd_<name>.mp4`
5. Drop the clip into the edit as B-roll or an overlay, then run `helpers/sync_to_drive.sh <videos_dir>`.

## Overrides for Ahmed's content
- The guide bans text. For Russian captions, use the normal caption pipeline on top of the clip, not `letter()`.
- Default canvas is 1920x1080. For Reels change `W`/`H` in `src/core.js` to 1080x1920 and recompose.
- Outputs go in `<videos_dir>/edit/`, never in this repo.

## Known issues
- Chrome is not installed on this PC. Edge launches headless by hand but fails under puppeteer ("Code: 0"). See status in CLAUDE.md.
- Without a dedicated GPU, watercolor fills render at seconds per frame. Ask for flat washes if too slow.
