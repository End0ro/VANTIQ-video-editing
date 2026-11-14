# Video Editing Workspace

Ahmed's video editing workspace for his personal-brand content (Reels, talking heads, educational videos). Editing only. Business context, voice, scripts and content strategy live in the AIOS repo (`claude-files`), not here.

Edits run **locally on this PC** (`C:\code\video-editing`). Video files are too big for remote/phone sessions.

## How to edit a video

1. Read `references/video-editing-styles.md` first. It picks the style (educational vs. talking head) and sets fonts, captions, colors and motion graphics.
2. Run `/video-editor`. Hand it the folder with the raw footage.
3. For talking heads, use the approved house style (2026-09-19). Build script: `references/examples/talking-head-captions.py`. Copy it into `<videos_dir>/edit/`, swap in the new words and cards, keep the style.

## Two editing tracks

- **Talking head (house style, default):** `/video-editor` plus `references/examples/talking-head-captions.py`. No cuts, no B-roll.
- **Cut-based reels with B-roll:** `/short-form-edit` (hook gate, quality gates), `/cut-silences` and `/cut-mistakes` (review-gated cuts), `/find-broll` (real clip, website recording, then Flow AI video), `/video-storytelling`, `/hyperframes-video-beats`, `/style-library`. Full pipeline: `/edit-video`. Use the "B-roll reel" style in `references/video-editing-styles.md`.
- `/website-to-hyperframes` turns a site into a video. For VANTIQ promos, not personal-brand content.
- Bridge between the two engines: `node scripts/video-use-to-hyperframes-transcript.mjs <edl.json>`.

## Rules

- **All outputs go in `<videos_dir>/edit/`.** Never inside this repo. Never commit footage or renders (`.gitignore` blocks them).
- **Check `transcription_source` on every transcript.** ElevenLabs Scribe is primary. Local Whisper is the fallback and misses more "um"/"uh", so don't trust its filler-word tags blindly.
- **Confirm the plan before cutting.** Plain-English strategy first, execute after Ahmed says yes.
- **Notes become rules.** When Ahmed gives a note on a draft, fix the edit, then write the note into the relevant skill or `references/` file as a rule or check, so it never needs repeating. Record the note and the rule together. (Method from `docs/herk-edit-kit/EDITING-PLAYBOOK.md`.)
- **Sync to Drive after every major step** with `helpers/sync_to_drive.sh <videos_dir>`. It mirrors the edit state to `VANTIQ Video Edits/<project>` in Google Drive via `gws`. That's the backup.
- **Colors:** this is personal-brand content. Don't use the VANTIQ agency palette (`VANTIQ/brand-guidelines.md` in the AIOS repo).
- Captions are Ahmed's own spoken words. Content is mostly Russian.

## Tools

- `/video-editor` skill in `.claude/skills/video-editor/`, vendored from `browser-use/video-use` (MIT). Helpers in `helpers/`.
- Remotion skills (`remotion-*`) in `.claude/skills/`, copied from `remotion-dev/remotion` (`packages/skills/skills`, v4.0.532). Start with `/remotion-best-practices`, it routes to the rest. Code-based video and animation in React. To update, re-copy that folder from upstream.
- `/design-taste-frontend` in `.claude/skills/design-taste-frontend/`, from `Leonxlnx/taste-skill` (MIT). Anti-slop UI design rules. Use it when building the visual side of Remotion compositions or any web UI.
- Emil Kowalski's animation and design skills in `.claude/skills/` (from `emilkowalski/skills`, MIT): `/emil-design-eng` (main), `/animate`, `/review-animations`, `/find-animation-opportunities`, `/animation-vocabulary`, `/apple-design`. Written for web UI, so use them for motion decisions (easing, duration, springs) in Remotion compositions and captions. Remotion's own skills still win on Remotion APIs.
- `/onetake` in `.claude/skills/onetake/`, from `feitangyuan/onetake` (PolyForm Noncommercial, commercial use needs onetake Pro). Continuous-camera motion animation method. Use its `references/` for ideas, check the license before publishing anything made with it.
- Skills imported from `nateherkai/herk-edit-kit` (MIT, 2026-10-16): `short-form-edit`, `cut-silences`, `cut-mistakes`, `edit-video`, `video-storytelling`, `hyperframes-video-beats`, `style-library`, `website-to-hyperframes`. Adapted: outputs go to `<videos_dir>/edit/`, transcription uses `video-editor`, generated B-roll uses Google Flow (no Kie.ai), captions use Ahmed's fonts. Docs in `docs/herk-edit-kit/`, helper scripts in `scripts/`, cards in `style-library/`. Licenses in `licenses/`. The AIS brand assets from his repo were not imported.
- `/find-broll` is Ahmed's own skill, built on Nate's B-roll rules. It holds the Google Flow route (Nano Banana stills, Omni 1.1 Flash video, no API key, 15 credits per 10 s clip as of 2026-10-15). Ahmed shows the style he wants, we copy it.
- Lip-sync note: `scripts/concat-drift-test/` showed `video-editor`'s per-segment concat drifting up to 173 ms over 12 cuts. See Known issue under Hard Rule 2 in its SKILL.md.
- HyperFrames skills (`hyperframes*`) for motion graphics, refreshed every session by `.claude/hooks/ensure-video-tools.sh`.
- Node scripts need `npm ci` once (`package.json`, Node 22+).
- Needs: `ffmpeg`, `uv` (Python deps via `uv sync --extra fallback`), `node/npx`, `gws`. The hook prints anything missing at session start.
- `ELEVENLABS_API_KEY` in the environment or `.env` at `.claude/skills/video-editor/` for Scribe (gitignored). Without it, transcription falls back to Whisper.

## Writing style (when talking to Ahmed)

- Never use em dashes.
- Simple words, short bullets, lead with the answer.
- No buzzwords, no rhetorical questions, no overexplaining.
