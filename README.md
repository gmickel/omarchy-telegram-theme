# Omarchy Telegram Theme

Automatically maps the active Omarchy color palette onto the native Linux
Telegram Desktop app. A supported Omarchy `theme-set` hook regenerates one
stable Telegram theme package containing the palette and a matching solid chat
wallpaper; Telegram watches that file and reloads it live.

The project does not edit Telegram's encrypted `tdata`, restart Telegram, or
depend on a third-party Telegram client.

## Requirements

- Omarchy 4.x
- Native Telegram Desktop (tested with Arch package `telegram-desktop` 7.0.9+)
- Python 3.11+

## Install

```bash
./install.sh
```

Telegram requires a one-time activation because it does not expose a public
theme-apply command or D-Bus method. Prefer the normal Chat settings UI:

1. Open Telegram → **Settings** → **Chat settings**.
2. Open the **⋮** menu (top-right) → **Create new theme** → **Import existing theme**.
3. Choose the generated file printed by `install.sh` (by default  
   `<checkout>/generated/omarchy.tdesktop-theme`).
4. Click **Keep changes** / Apply.

After that, `omarchy theme set <name>` regenerates the **same** file in place.
Telegram's file watcher reloads colors while the app is running.

> Tip: avoid copying the theme into Downloads. Telegram watches the exact path
> you import; keep using the stable generated path from this checkout.

### Legacy `loadcolors` activation

The hidden Settings code `loadcolors` still works if you prefer it: focus
Settings (not the search box), type `loadcolors`, then pick the sibling
`.tdesktop-palette` hard-link next to the `.tdesktop-theme` file. Do not use
desktop lock shortcuts while picking the file.

To regenerate or inspect the palette manually:

```bash
omarchy-telegram-theme
omarchy-telegram-theme --check
omarchy-telegram-theme --stdout | less
```

To remove the hook and installed generator:

```bash
./uninstall.sh
```

The generated theme package is deliberately retained during uninstall, since
Telegram may still have its path saved. Select another Telegram theme before
deleting it.

## How it works

Omarchy 4 builds a staged theme, atomically moves it to
`~/.local/state/omarchy/current/theme`, then runs every script in
`~/.config/omarchy/hooks/theme-set.d/` with the new theme slug. The hook in this
project reads the resulting `colors.toml`, not the source theme folder, so stock
themes, user overlays, and generated legacy themes all behave the same way. It
uses the same semantic fallbacks as Omarchy itself, including legacy short-name
and ANSI `color0` through `color15` palettes, derived background shades, and
automatic dark/light mode detection.

Telegram's small secondary labels and inactive icons are contrast-checked
against their surfaces. Theme colors that already meet the readability floor
are preserved; lower-contrast colors are moved toward the theme foreground just
far enough to reach 4.5:1 for text or 3:1 for icons. Chat chrome that sits
**on** message bubbles (reply author names, read-receipt ticks, links, mono
text, reply bars) is contrast-checked against the actual bubble fill — not only
against the window background — so accent-tinted outgoing bubbles stay readable.

Incoming and outgoing bubbles are picked from the Omarchy palette with enough
RGB separation that “my messages” and “their messages” stay easy to tell apart,
while message body text remains contrast-safe on both fills.

The generator starts with Telegram Desktop's official custom-theme palette,
recolors every literal (which prevents obscure dialogs from falling back to the
blue/white day palette), and applies explicit mappings for primary surfaces,
text, active states, chat bubbles, semantic colors, calls, and the filter
sidebar. It also packages a `background.png` filled with Omarchy's `background`
color, so applying the generated theme sets the chat wallpaper too. It supports
explicit Omarchy `mode = "dark"` and `mode = "light"` values, the legacy
`theme_type` key and `light.mode` marker, and luminance-based mode detection.

The theme package is a ZIP that includes both `colors.tdesktop-theme` and
`colors.tdesktop-palette` plus `background.png`. The installer writes
`generated/omarchy.tdesktop-theme` and a same-inode `.tdesktop-palette` sibling
so either Import-theme or `loadcolors` can watch one file.

Updates overwrite that file **in place** (same inode) and are skipped when
content is unchanged. Atomic replace is avoided on purpose: Telegram's
`QFileSystemWatcher` drops watches when the inode changes, which silently
breaks live Omarchy theme sync. With in-place writes, Telegram reapplies the
palette after `fileChanged` without poking its settings database.

## Verification

```bash
python -m unittest discover -s tests -v
bash -n install.sh uninstall.sh hooks/omarchy-telegram-theme
python bin/omarchy-telegram-theme --check
```

## Research sources

- [Omarchy theming and activation flow](https://github.com/basecamp/omarchy/blob/quattro/docs/theming.md)
- [Installed Omarchy `theme-set` implementation](https://github.com/basecamp/omarchy/blob/quattro/bin/omarchy-theme-set)
- [Telegram custom-theme format reference](https://github-wiki-see.page/m/telegramdesktop/tdesktop/wiki/Theme-Reference)
- [Telegram theme loader and live file watcher](https://github.com/telegramdesktop/tdesktop/blob/dev/Telegram/SourceFiles/window/themes/window_theme.cpp)
- [Telegram's `loadcolors` Settings code](https://github.com/telegramdesktop/tdesktop/blob/dev/Telegram/SourceFiles/settings/settings_codes.cpp)

The bundled palette snapshot comes from Telegram Desktop commit
[`0266739`](https://github.com/telegramdesktop/tdesktop/commit/02667395ee9ed120fb95bcd75fa7cb869238d6d3),
file `Telegram/Resources/day-custom-base.tdesktop-theme`. Its extracted palette
SHA-256 is `7ba0c1f51af0fb1b7cc115f4a8ce1467caf0013ff5081614d620440d63e1b865`.

## License

GPL-3.0-only. The bundled base palette is derived from Telegram Desktop, which
is GPLv3 with Telegram's documented OpenSSL exception. See [NOTICE.md](NOTICE.md).

## CI

Pull requests and main pushes run the deterministic checks in
`.github/workflows/ci.yml`. Superseded PR runs are cancelled.
Desktop, theme and live-account acceptance remain local; CI uses no workstation credentials.
