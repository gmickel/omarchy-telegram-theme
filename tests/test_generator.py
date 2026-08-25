# SPDX-License-Identifier: GPL-3.0-only
from __future__ import annotations

import importlib.machinery
import importlib.util
import hashlib
import io
from pathlib import Path
import re
import struct
import tempfile
import unittest
import zipfile
import zlib


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "bin/omarchy-telegram-theme"
loader = importlib.machinery.SourceFileLoader("generator", str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
generator = importlib.util.module_from_spec(spec)
loader.exec_module(generator)


DARK = """\
mode = "dark"
accent = "#7aa2f7"
selection = "#292e42"
muted = "#414868"
background = "#1a1b26"
dark_background = "#13141c"
darker_background = "#0e0e14"
lighter_background = "#24283b"
foreground = "#a9b1d6"
dark_foreground = "#565f89"
light_foreground = "#b4bee6"
bright_foreground = "#c0caf5"
red = "#f7768e"
yellow = "#e0af68"
green = "#9ece6a"
cyan = "#7dcfff"
blue = "#7aa2f7"
magenta = "#bb9af7"
"""

LIGHT = DARK.replace('mode = "dark"', 'mode = "light"').replace(
    'background = "#1a1b26"', 'background = "#eff1f5"'
).replace('foreground = "#a9b1d6"', 'foreground = "#4c4f69"')


class GeneratorTest(unittest.TestCase):
    def generate(self, document: str):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "colors.toml"
            path.write_text(document)
            colors = generator.read_omarchy_colors(path)
            base = generator.read_base_palette(
                ROOT / "assets/day-custom-base.palette.gz.b64"
            )
            return colors, generator.render_palette(base, colors, "fixture")

    def test_dark_root_roles_and_complete_palette(self):
        colors, output = self.generate(DARK)
        self.assertIn("windowBg: #1a1b26;", output)
        self.assertIn("windowFg: #a9b1d6;", output)
        self.assertIn("windowBgActive: #7aa2f7;", output)
        self.assertIn("imageBg: #000000;", output)
        self.assertIn("slideFadeOutBg: #0000003c;", output)
        self.assertIn("groupCallBg: #0e0e14;", output)
        self.assertGreater(len(output.splitlines()), 500)
        self.assertNotRegex(output, r"#[0-9a-fA-F]{6}[^0-9a-fA-F;\n]")
        self.assertEqual(colors["mode"], "dark")

    def test_light_mode_uses_light_surface_and_dark_text(self):
        _, output = self.generate(LIGHT)
        self.assertIn("windowBg: #eff1f5;", output)
        self.assertIn("windowFg: #4c4f69;", output)
        self.assertIn("Omarchy theme: fixture (light)", output)

    def test_generated_palette_has_no_duplicate_keys(self):
        _, output = self.generate(DARK)
        entries = re.findall(
            r"^([A-Za-z_][A-Za-z0-9_]*):\s*([^;]+);", output, re.MULTILINE
        )
        keys = [key for key, _ in entries]
        self.assertEqual(len(keys), len(set(keys)))

        for key, value in entries:
            value = value.strip()
            self.assertTrue(
                re.fullmatch(r"#[0-9a-fA-F]{6}(?:[0-9a-fA-F]{2})?", value)
                or re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value),
                f"invalid palette value: {key}: {value}",
            )

    def test_bundled_upstream_palette_checksum(self):
        content = generator.read_base_palette(
            ROOT / "assets/day-custom-base.palette.gz.b64"
        ).encode()
        self.assertEqual(
            hashlib.sha256(content).hexdigest(),
            "7ba0c1f51af0fb1b7cc115f4a8ce1467caf0013ff5081614d620440d63e1b865",
        )

    def test_theme_package_contains_palette_and_chat_wallpaper(self):
        colors, palette = self.generate(DARK)
        package = generator.build_theme_package(palette, colors["background"])

        with zipfile.ZipFile(io.BytesIO(package)) as archive:
            self.assertEqual(
                archive.namelist(),
                ["colors.tdesktop-palette", "background.png"],
            )
            self.assertEqual(
                archive.read("colors.tdesktop-palette").decode(), palette
            )
            png = archive.read("background.png")

        self.assertEqual(png[:8], b"\x89PNG\r\n\x1a\n")
        offset = 8
        chunks = {}
        while offset < len(png):
            length = struct.unpack(">I", png[offset : offset + 4])[0]
            kind = png[offset + 4 : offset + 8]
            chunks[kind] = png[offset + 8 : offset + 8 + length]
            offset += 12 + length
        self.assertEqual(struct.unpack(">II", chunks[b"IHDR"][:8]), (1, 1))
        self.assertEqual(
            zlib.decompress(chunks[b"IDAT"]),
            b"\x00" + bytes((0x1A, 0x1B, 0x26)),
        )

    def test_theme_package_is_deterministic(self):
        colors, palette = self.generate(DARK)
        first = generator.build_theme_package(palette, colors["background"])
        second = generator.build_theme_package(palette, colors["background"])
        self.assertEqual(first, second)

    def test_rejects_missing_color(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "colors.toml"
            path.write_text(DARK.replace('accent = "#7aa2f7"\n', ""))
            with self.assertRaisesRegex(generator.ThemeError, "accent"):
                generator.read_omarchy_colors(path)

    def test_atomic_writer_is_idempotent(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "theme.tdesktop-palette"
            self.assertTrue(generator.write_if_changed(output, "first\n"))
            self.assertFalse(generator.write_if_changed(output, "first\n"))
            self.assertTrue(generator.write_if_changed(output, "second\n"))
            self.assertEqual(output.read_text(), "second\n")

    def test_atomic_writer_supports_binary_theme_packages(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "theme.tdesktop-palette"
            self.assertTrue(generator.write_if_changed(output, b"PK\x03\x04first"))
            self.assertFalse(generator.write_if_changed(output, b"PK\x03\x04first"))
            self.assertEqual(output.read_bytes(), b"PK\x03\x04first")


if __name__ == "__main__":
    unittest.main()
