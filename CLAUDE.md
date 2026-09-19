# Video Editing Workspace

Ahmed's video editing workspace for his personal-brand content (Reels, talking heads, educational videos). Editing only. Business context, voice, scripts and content strategy live in the AIOS repo (`claude-files`), not here.

Edits run **locally on this PC** (`C:\code\video-editing`). Video files are too big for remote/phone sessions.

## How to edit a video

1. Read `references/video-editing-styles.md` first. It picks the style (educational vs. talking head) and sets fonts, captions, colors and motion graphics.
2. Run `/video-editor`. Hand it the folder with the raw footage.
3. For talking heads, use the approved house style (2026-09-19). Build script: `references/examples/talking-head-captions.py`. Copy it into `<videos_dir>/edit/`, swap in the new words and cards, keep the style.

## Rules

- **All outputs go in `<videos_dir>/edit/`.** Never inside this repo. Never commit footage or renders (`.gitignore` blocks them).
- **Check `transcription_source` on every transcript.** ElevenLabs Scribe is primary. Local Whisper is the fallback and misses more "um"/"uh", so don't trust its filler-word tags blindly.
- **Confirm the plan before cutting.** Plain-English strategy first, execute after Ahmed says yes.
- **Sync to Drive after every major step** with `helpers/sync_to_drive.sh <videos_dir>`. It mirrors the edit state to `VANTIQ Video Edits/<project>` in Google Drive via `gws`. That's the backup.
- **Colors:** this is personal-brand content. Don't use the VANTIQ agency palette (`VANTIQ/brand-guidelines.md` in the AIOS repo).
- Captions are Ahmed's own spoken words. Content is mostly Russian.

## Tools

- `/video-editor` skill in `.claude/skills/video-editor/`, vendored from `browser-use/video-use` (MIT). Helpers in `helpers/`.
- HyperFrames skills (`hyperframes*`) for motion graphics, refreshed every session by `.claude/hooks/ensure-video-tools.sh`.
- Needs: `ffmpeg`, `uv` (Python deps via `uv sync --extra fallback`), `node/npx`, `gws`. The hook prints anything missing at session start.
- `ELEVENLABS_API_KEY` in the environment or `.env` at `.claude/skills/video-editor/` for Scribe (gitignored). Without it, transcription falls back to Whisper.

## Writing style (when talking to Ahmed)

- Never use em dashes.
- Simple words, short bullets, lead with the answer.
- No buzzwords, no rhetorical questions, no overexplaining.
