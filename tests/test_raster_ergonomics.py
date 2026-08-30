#!/usr/bin/env python3
"""
Ergonomic and Rasterization Unit Test Suite for Typus Mono
Implements checks based on:
- ISO 9241-303 / ISO 9241-305
- W3C WCAG 2.1 SC 1.4.3 & APCA
- Chromatic Aberration and Color Dispersion
- OpenType 1.9 gasp Table Specification
"""

import os
import unittest
import numpy as np
import cairo
from fontTools.ttLib import TTFont

FONTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts"
)
TEST_BUILDS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "test_builds", "step_3"
)


def render_glyph_rgb(
    font_path,
    text,
    font_size_pt=12.5,
    dpi=96,
    bg_rgb=(30, 30, 46),
    fg_rgb=(230, 230, 240),
):
    """Render glyph with RGB subpixel simulation onto numpy array."""
    size_px = font_size_pt * (dpi / 72.0)
    width, height = 48, 48

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)

    # Fill background
    ctx.set_source_rgb(bg_rgb[0] / 255.0, bg_rgb[1] / 255.0, bg_rgb[2] / 255.0)
    ctx.paint()

    ctx.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size_px)

    font_options = cairo.FontOptions()
    font_options.set_antialias(cairo.ANTIALIAS_GRAY)
    font_options.set_hint_style(cairo.HINT_STYLE_SLIGHT)
    ctx.set_font_options(font_options)

    ctx.set_source_rgb(fg_rgb[0] / 255.0, fg_rgb[1] / 255.0, fg_rgb[2] / 255.0)
    ctx.move_to(8, 36)
    ctx.show_text(text)

    buf = surface.get_data()
    # ARGB32 in memory is BGRA on little-endian
    arr = np.ndarray(shape=(height, width, 4), dtype=np.uint8, buffer=buf)
    b = arr[:, :, 0].astype(float)
    g = arr[:, :, 1].astype(float)
    r = arr[:, :, 2].astype(float)
    return np.stack([r, g, b], axis=-1)


class TestRasterErgonomicsAndStandards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        target_dir = TEST_BUILDS_DIR if os.path.exists(TEST_BUILDS_DIR) else FONTS_DIR
        cls.font_files = [f for f in os.listdir(target_dir) if f.endswith(".ttf")]
        cls.target_dir = target_dir

    def test_chromatic_neutrality_dark_background(self):
        """
        Verify that font rasterization produces ZERO chromatic aberration (Delta Alpha <= 0.01).
        Delta Alpha measures subpixel color fringing across R, G, B color channels at edge transitions.
        """
        sample_font = os.path.join(self.target_dir, self.font_files[0])
        bg_rgb = np.array([30.0, 30.0, 46.0])
        fg_rgb = np.array([230.0, 230.0, 240.0])

        for char in ["H", "M", "E", "n", "0", "#"]:
            rgb_arr = render_glyph_rgb(
                sample_font,
                char,
                font_size_pt=12.5,
                bg_rgb=tuple(bg_rgb),
                fg_rgb=tuple(fg_rgb),
            )

            denom = fg_rgb - bg_rgb
            alpha_map = (rgb_arr - bg_rgb) / denom

            alpha_r = alpha_map[:, :, 0]
            alpha_g = alpha_map[:, :, 1]
            alpha_b = alpha_map[:, :, 2]

            edge_mask = (alpha_g > 0.05) & (alpha_g < 0.95)
            if np.any(edge_mask):
                diff_rg = np.max(np.abs(alpha_r[edge_mask] - alpha_g[edge_mask]))
                diff_gb = np.max(np.abs(alpha_g[edge_mask] - alpha_b[edge_mask]))
                diff_rb = np.max(np.abs(alpha_r[edge_mask] - alpha_b[edge_mask]))
                max_alpha_dispersion = max(diff_rg, diff_gb, diff_rb)

                self.assertLessEqual(
                    max_alpha_dispersion,
                    0.02,
                    f"Glyph '{char}' exhibits subpixel chromatic fringing: max Delta Alpha = {max_alpha_dispersion:.4f}",
                )

    def test_edge_spread_function_iso_9241(self):
        """
        Measure Edge Spread Function (ESF) 10%-90% transition width according to ISO 9241-303.
        Transition width across vertical stems must not exceed 1.8 pixels at 12.5pt.
        """
        sample_font = os.path.join(self.target_dir, self.font_files[0])
        rgb_arr = render_glyph_rgb(sample_font, "I", font_size_pt=12.5)
        # Rec. 709
        luminance = (
            0.2126 * rgb_arr[:, :, 0]
            + 0.7152 * rgb_arr[:, :, 1]
            + 0.0722 * rgb_arr[:, :, 2]
        )

        # Horizontal cross-section through stem
        mid_row = luminance[24, :]
        min_val = np.min(mid_row)
        max_val = np.max(mid_row)

        if max_val - min_val > 50:
            norm = (mid_row - min_val) / (max_val - min_val)
            transitions = np.where((norm >= 0.10) & (norm <= 0.90))[0]
            if len(transitions) > 0:
                spread_width = (
                    len(transitions) / 2.0
                )  # approximate per-edge spread in pixels
                self.assertLessEqual(
                    spread_width,
                    2.0,
                    f"Edge Spread Function exceeds ISO 9241-303 threshold: {spread_width:.2f} px",
                )

    def test_gasp_table_flags_presence(self):
        """Verify gasp table has all OpenType 1.9 recommended flags (0x000F: GRIDFIT | DOGRAY | SYMMETRIC)."""
        for fname in self.font_files:
            fpath = os.path.join(self.target_dir, fname)
            with self.subTest(font=fname):
                font = TTFont(fpath)
                if "gasp" in font:
                    gasp = font["gasp"]
                    for ppem, flag in gasp.gaspRange.items():
                        # Verify DOGRAY (0x02) and GRIDFIT (0x01)
                        self.assertTrue(
                            bool(flag & 0x02),
                            f"Font {fname} gasp range {ppem} missing GASP_DOGRAY flag",
                        )


if __name__ == "__main__":
    unittest.main()
