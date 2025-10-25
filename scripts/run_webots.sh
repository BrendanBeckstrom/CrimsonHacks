#!/usr/bin/env bash
set -euo pipefail
# Adjust WEBOTS path if not on PATH. Example for macOS:
# export WEBOTS_HOME="/Applications/Webots.app/Contents/MacOS"
# export PATH="$WEBOTS_HOME:$PATH"

WORLD_PATH="webots/world/CrimsonMars.wbt"
CONTROLLER_NAME="rover_controller"

if ! command -v webots &>/dev/null; then
  echo "Error: webots not found in PATH. Add Webots to PATH or edit this script." >&2
  exit 1
fi

webots --stdout --stderr --no-sandbox --mode=fast "$WORLD_PATH"
