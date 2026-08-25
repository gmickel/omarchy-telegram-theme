#!/bin/bash
# SPDX-License-Identifier: GPL-3.0-only
set -euo pipefail

hook="$HOME/.config/omarchy/hooks/theme-set.d/omarchy-telegram-theme"
binary="$HOME/.local/bin/omarchy-telegram-theme"
data_file="${XDG_DATA_HOME:-$HOME/.local/share}/omarchy-telegram-theme/assets/day-custom-base.palette.gz.b64"

rm -f -- "$hook" "$binary" "$data_file"
rmdir -- "$(dirname -- "$data_file")" 2>/dev/null || true
rmdir -- "$(dirname -- "$(dirname -- "$data_file")")" 2>/dev/null || true
rmdir -- "$(dirname -- "$hook")" 2>/dev/null || true

echo "Uninstalled Omarchy Telegram Theme."
echo "The generated .tdesktop-palette was retained because Telegram may still reference it."
