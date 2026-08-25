#!/bin/bash
# SPDX-License-Identifier: GPL-3.0-only
set -euo pipefail

project_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
bin_dir="$HOME/.local/bin"
data_dir="${XDG_DATA_HOME:-$HOME/.local/share}/omarchy-telegram-theme"
hook_source="$project_dir/hooks/omarchy-telegram-theme"

command -v omarchy >/dev/null 2>&1 || {
  echo "Omarchy is required but was not found." >&2
  exit 1
}
command -v python >/dev/null 2>&1 || {
  echo "Python 3.11 or newer is required but was not found." >&2
  exit 1
}

python -c 'import sys; raise SystemExit(sys.version_info < (3, 11))' || {
  echo "Python 3.11 or newer is required." >&2
  exit 1
}

install -Dm755 "$project_dir/bin/omarchy-telegram-theme" \
  "$bin_dir/omarchy-telegram-theme"
install -Dm644 "$project_dir/assets/day-custom-base.palette.gz.b64" \
  "$data_dir/assets/day-custom-base.palette.gz.b64"

omarchy hook install theme-set "$hook_source"

theme_name=$(omarchy theme current 2>/dev/null || true)
theme_slug=$(printf '%s' "$theme_name" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')
"$bin_dir/omarchy-telegram-theme" --theme "${theme_slug:-unknown}"

theme_file="${XDG_STATE_HOME:-$HOME/.local/state}/omarchy-telegram-theme/omarchy.tdesktop-palette"
cat <<EOF

Installed Omarchy Telegram Theme.

One-time Telegram activation:
  1. Open Telegram Settings.
  2. Type: loadcolors
  3. Choose: $theme_file
  4. Click "Keep changes".

Tip: the path is hidden under .local. In the file picker, press Ctrl+L and
paste the full path above (or press Ctrl+H to show hidden folders).

Telegram will now reload that same file whenever the Omarchy theme changes.
EOF
