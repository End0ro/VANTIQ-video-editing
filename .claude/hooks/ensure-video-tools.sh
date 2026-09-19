#!/usr/bin/env bash
# Makes sure the video-editor toolchain is ready at session start.
#
# On Linux containers (remote/cloud sessions) it installs ffmpeg with apt.
# On Windows/macOS it doesn't install anything, it only reports what's
# missing so the session knows before an edit fails halfway.
#
# Every step is best-effort (|| true). A failure here should never block
# session start. The video-editor skill surfaces a clear error at the point
# of use if something it needs still isn't there.
set -uo pipefail

VIDEO_EDITOR_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}/.claude/skills/video-editor"
missing=()

if ! command -v ffmpeg >/dev/null 2>&1; then
  if command -v apt-get >/dev/null 2>&1; then
    apt-get update -qq >/dev/null 2>&1 || true
    apt-get install -y -qq ffmpeg >/dev/null 2>&1 || true
  fi
  command -v ffmpeg >/dev/null 2>&1 || missing+=("ffmpeg")
fi

if command -v uv >/dev/null 2>&1; then
  if [ -f "$VIDEO_EDITOR_DIR/pyproject.toml" ]; then
    (cd "$VIDEO_EDITOR_DIR" && uv sync --extra fallback >/dev/null 2>&1) || true
  fi
else
  missing+=("uv")
fi

if command -v npx >/dev/null 2>&1; then
  npx --yes hyperframes skills update >/dev/null 2>&1 || true
else
  missing+=("node/npx")
fi

command -v gws >/dev/null 2>&1 || missing+=("gws (Drive sync)")

if [ ${#missing[@]} -gt 0 ]; then
  echo "video-editor toolchain missing: ${missing[*]}. Install before editing."
fi
exit 0
