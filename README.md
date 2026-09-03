# Omarchy Telegram Theme

Automatically maps the active Omarchy color palette onto the native Linux
Telegram Desktop app. A supported Omarchy `theme-set` hook regenerates one
stable Telegram theme package containing the palette and a matching solid chat
wallpaper; Telegram watches that file and reloads it live.

The project does not edit Telegram's encrypted `tdata`, restart Telegram, or
depend on a third-party Telegram client.

## Requirements

- Omarchy 4.x
- Native Telegram Desktop (tested with Arch package `telegram-desktop` 7.0.9)
- Python 3.11+

## Install

```bash
./install.sh
```

Telegram requires a one-time activation because it does not expose a public
theme-apply command or D-Bus method:

1. Open Telegram **Settings**.
2. Type `loadcolors` while the Settings screen is focused.
3. Choose
   `~/.local/state/omarchy-telegram-theme/omarchy.tdesktop-palette`.
4. Click **Keep changes**.

Because `.local` is hidden, press `Ctrl+L` in the file picker and paste the
full path, or press `Ctrl+H` to show hidden folders.

After that, `omarchy theme set <name>` automatically regenerates the same file.
Telegram reloads it while running and reads it again on later launches.

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
far enough to reach 4.5:1 for text or 3:1 for icons.

The generator starts with Telegram Desktop's official custom-theme palette,
recolors every literal (which prevents obscure dialogs from falling back to the
blue/white day palette), and applies explicit mappings for primary surfaces,
text, active states, chat bubbles, semantic colors, calls, and the filter
sidebar. It also packages a `background.png` filled with Omarchy's `background`
color, so applying the generated theme sets the chat wallpaper too. It supports
explicit Omarchy `mode = "dark"` and `mode = "light"` values, the legacy
`theme_type` key and `light.mode` marker, and luminance-based mode detection.

The outer file keeps the `.tdesktop-palette` extension because Telegram's
hidden `loadcolors` picker only shows that suffix. Telegram detects the ZIP
theme package by its contents and loads the embedded palette and wallpaper.

Writes are atomic and skipped when content is unchanged. Telegram Desktop's
theme implementation attaches a `QFileSystemWatcher` to a native custom theme
path and reapplies it after `fileChanged`, which is why the stable-file approach
updates a running instance without poking its settings database.

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
