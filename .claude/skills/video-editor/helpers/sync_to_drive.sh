#!/usr/bin/env bash
# Mirrors <videos_dir>/edit/ durable state to Google Drive via `gws`.
#
# Why: sessions run in ephemeral containers. If a session ends or the user
# switches sessions mid-edit, everything on local disk (edl.json, cut
# decisions, transcripts, renders) is gone — it was never pushed anywhere.
# This script is the durability layer: call it after every major step
# (transcription pack, edl.json write, each render) so an interrupted
# session never loses more than the step in progress.
#
# Usage: sync_to_drive.sh <videos_dir>
#
# Only syncs regenerable-but-slow-to-rebuild state, not everything in
# edit/: skips clips_graded/, downloads/, verify/, animations/ (large,
# and reproducible from source + edl.json + grade.py). Uploads whichever
# of the following exist:
#   project.md, takes_packed.md, edl.json, master.srt, preview.mp4, final.mp4
#
# Best-effort: a missing gws auth, no network, or a Drive API hiccup
# should never abort the edit session. Failures print a warning and exit
# 0 so the calling skill step isn't blocked by this.

set -uo pipefail

VIDEOS_DIR="${1:?Usage: sync_to_drive.sh <videos_dir>}"
EDIT_DIR="$VIDEOS_DIR/edit"
ROOT_FOLDER_NAME="VANTIQ Video Edits"
PROJECT_FOLDER_NAME="$(basename "$VIDEOS_DIR")"

if ! command -v gws >/dev/null 2>&1; then
  echo "warning: gws not found, skipping Drive sync for $VIDEOS_DIR" >&2
  exit 0
fi

if [ ! -d "$EDIT_DIR" ]; then
  echo "warning: $EDIT_DIR does not exist, nothing to sync" >&2
  exit 0
fi

# find_or_create_folder <name> <parent_id_or_empty>
find_or_create_folder() {
  local name="$1" parent="$2" query id
  query="name = \"$name\" and mimeType = \"application/vnd.google-apps.folder\" and trashed = false"
  if [ -n "$parent" ]; then
    query="$query and \"$parent\" in parents"
  fi
  id=$(gws drive files list --params "{\"q\":\"$query\",\"fields\":\"files(id,name)\"}" 2>/dev/null \
    | jq -r '.files[0].id // empty')
  if [ -n "$id" ]; then
    echo "$id"
    return 0
  fi
  local body
  if [ -n "$parent" ]; then
    body="{\"name\":\"$name\",\"mimeType\":\"application/vnd.google-apps.folder\",\"parents\":[\"$parent\"]}"
  else
    body="{\"name\":\"$name\",\"mimeType\":\"application/vnd.google-apps.folder\"}"
  fi
  gws drive files create --json "$body" --params '{"fields":"id"}' 2>/dev/null | jq -r '.id // empty'
}

# Drive's search index lags a few seconds behind a create, so back-to-back
# calls in the same session (this script runs after every major step) can
# otherwise each fail to find the folder the last call just made and create
# a duplicate. Cache the resolved IDs locally once found/created per session.
STATE_FILE="$EDIT_DIR/.drive_sync_ids.json"
ROOT_ID=""
PROJECT_ID=""
if [ -f "$STATE_FILE" ]; then
  ROOT_ID=$(jq -r '.root_id // empty' "$STATE_FILE" 2>/dev/null)
  PROJECT_ID=$(jq -r '.project_id // empty' "$STATE_FILE" 2>/dev/null)
fi

if [ -z "$ROOT_ID" ]; then
  ROOT_ID=$(find_or_create_folder "$ROOT_FOLDER_NAME" "")
fi
if [ -z "$ROOT_ID" ]; then
  echo "warning: could not find/create '$ROOT_FOLDER_NAME' in Drive, skipping sync" >&2
  exit 0
fi

if [ -z "$PROJECT_ID" ]; then
  PROJECT_ID=$(find_or_create_folder "$PROJECT_FOLDER_NAME" "$ROOT_ID")
fi
if [ -z "$PROJECT_ID" ]; then
  echo "warning: could not find/create project folder '$PROJECT_FOLDER_NAME', skipping sync" >&2
  exit 0
fi

# Same index-lag risk applies to individual files re-synced seconds apart
# (e.g. edl.json updated after every edit), so cache file IDs too.
save_state() {
  jq -n --arg r "$ROOT_ID" --arg p "$PROJECT_ID" --argjson f "$1" \
    '{root_id: $r, project_id: $p, files: $f}' > "$STATE_FILE" 2>/dev/null || true
}
FILE_IDS=$(jq -c '.files // {}' "$STATE_FILE" 2>/dev/null || echo '{}')
save_state "$FILE_IDS"

SYNCED=0
# `gws --upload` refuses paths outside the current directory, so cd into
# edit/ and pass bare filenames.
ORIG_DIR="$(pwd)"
cd "$EDIT_DIR" || exit 0

for name in project.md takes_packed.md edl.json master.srt preview.mp4 final.mp4; do
  [ -f "$name" ] || continue

  existing_id=$(echo "$FILE_IDS" | jq -r --arg n "$name" '.[$n] // empty')
  if [ -z "$existing_id" ]; then
    existing_id=$(gws drive files list \
      --params "{\"q\":\"name = \\\"$name\\\" and \\\"$PROJECT_ID\\\" in parents and trashed = false\",\"fields\":\"files(id)\"}" \
      2>/dev/null | jq -r '.files[0].id // empty')
  fi

  if [ -n "$existing_id" ]; then
    if gws drive files update --params "{\"fileId\":\"$existing_id\"}" --upload "$name" >/dev/null 2>&1; then
      SYNCED=$((SYNCED + 1))
      FILE_IDS=$(echo "$FILE_IDS" | jq -c --arg n "$name" --arg i "$existing_id" '.[$n] = $i')
    else
      echo "warning: failed to update $name in Drive" >&2
    fi
  else
    new_id=$(gws drive files create --json "{\"name\":\"$name\",\"parents\":[\"$PROJECT_ID\"]}" --upload "$name" --params '{"fields":"id"}' 2>/dev/null | jq -r '.id // empty')
    if [ -n "$new_id" ]; then
      SYNCED=$((SYNCED + 1))
      FILE_IDS=$(echo "$FILE_IDS" | jq -c --arg n "$name" --arg i "$new_id" '.[$n] = $i')
    else
      echo "warning: failed to upload $name to Drive" >&2
    fi
  fi
done

cd "$ORIG_DIR" || true
save_state "$FILE_IDS"
echo "synced $SYNCED file(s) to Drive: $ROOT_FOLDER_NAME/$PROJECT_FOLDER_NAME"
