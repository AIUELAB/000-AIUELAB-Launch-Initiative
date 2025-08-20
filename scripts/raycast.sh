#!/usr/bin/env bash
set -euo pipefail

cmd="${1:-}"
case "$cmd" in
  launch)
    open -a "/Applications/Raycast.app"
    ;;
  confetti)
    open "raycast://extensions/raycast/raycast/confetti"
    ;;
  *)
    echo "Usage: $0 {launch|confetti}" >&2
    exit 1
    ;;
esac
