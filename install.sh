#!/usr/bin/env bash
# Install the skills into ~/.claude/skills and drop a starter config. Safe by default:
# a skill folder that already exists is skipped unless you pass --force.
#   ./install.sh            install missing skills, keep yours
#   ./install.sh --force    replace same-named skills (yours are moved to ~/.claude/skills-backup/<stamp>/ first,
#                           outside the skills folder so Claude Code does not load the old copies)
#   ./install.sh --list     show what would be installed
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
dest="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
cfg_dir="${XDG_CONFIG_HOME:-$HOME/.config}/company-aios"
mode="${1:-}"

mkdir -p "$dest"
stamp="$(date +%Y%m%d-%H%M%S)"
backup="$(dirname "$dest")/skills-backup/$stamp"
for src in "$here"/skills/*/; do
  name="$(basename "$src")"
  if [ "$mode" = "--list" ]; then echo "$name"; continue; fi
  if [ -e "$dest/$name" ]; then
    if [ "$mode" != "--force" ]; then echo "skip   $name (already installed; --force replaces it)"; continue; fi
    mkdir -p "$backup"
    mv "$dest/$name" "$backup/$name"
    echo "backup $backup/$name"
  fi
  cp -R "$src" "$dest/$name"
  echo "added  $name"
done
[ "$mode" = "--list" ] && exit 0

if [ ! -e "$cfg_dir/config.json" ]; then
  mkdir -p "$cfg_dir"
  cp "$here/config.example.json" "$cfg_dir/config.json"
  echo "config $cfg_dir/config.json (edit the names and paths)"
fi
echo "done. Start a new Claude Code session so the skills load."
