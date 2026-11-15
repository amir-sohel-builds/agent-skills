#!/usr/bin/env bash
# Install agent-skills into Claude Code (~/.claude/skills)
# and Cursor (~/.cursor/skills) when it exists.
# Skills live in skills/ and in tools-and-automation/.
# Run from the repo root: bash install.sh
# Never pipe this script from the internet. Clone the repo, read it, then run it.
set -euo pipefail
shopt -s nullglob

REPO_URL="https://github.com/amir-sohel-builds/agent-skills.git"
ONLY=""
DRY_RUN=0

while [ $# -gt 0 ]; do
  case "$1" in
    --only)
      ONLY="${2:?--only needs a skill name}"; shift 2 ;;
    --dry-run)
      DRY_RUN=1; shift ;;
    *)
      echo "usage: install.sh [--only <skill>] [--dry-run]" >&2; exit 1 ;;
  esac
done

if [ -n "$ONLY" ]; then
  case "$ONLY" in
    *[!a-z0-9-]*)
      echo "invalid skill name: $ONLY" >&2; exit 1 ;;
  esac
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-.}")" && pwd)"
SRC="$SCRIPT_DIR"

TARGETS=("$HOME/.claude/skills")
if [ -d "$HOME/.cursor" ]; then
  TARGETS+=("$HOME/.cursor/skills")
fi

if [ ! -d "$SRC/skills" ] && [ ! -d "$SRC/tools-and-automation" ]; then
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "dry run: would clone $REPO_URL, then install skills to ${TARGETS[*]}"
    exit 0
  fi
  TMP="$(mktemp -d)"
  git clone --depth 1 "$REPO_URL" "$TMP/repo" >/dev/null 2>&1
  SRC="$TMP/repo"
fi

skill_dir() {
  local name="$1"
  if [ -d "$SRC/skills/$name" ]; then echo "$SRC/skills/$name"; return 0; fi
  if [ -d "$SRC/tools-and-automation/$name" ]; then echo "$SRC/tools-and-automation/$name"; return 0; fi
  return 1
}

install_one() {
  local name="$1" src="$2"
  for target in "${TARGETS[@]}"; do
    if [ "$DRY_RUN" -eq 1 ]; then
      echo "dry run: would install $name to $target/$name"
    else
      mkdir -p "$target"
      rm -rf "$target/$name"
      cp -r "$src" "$target/$name"
      echo "installed $name to $target/$name"
    fi
  done
}

if [ -n "$ONLY" ]; then
  src="$(skill_dir "$ONLY")" || { echo "no skill named $ONLY" >&2; exit 1; }
  install_one "$ONLY" "$src"
else
  for dir in "$SRC"/skills/*/ "$SRC"/tools-and-automation/*/; do
    [ -d "$dir" ] || continue
    install_one "$(basename "$dir")" "$dir"
  done
fi
