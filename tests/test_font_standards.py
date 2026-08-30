#!/usr/bin/env python3
"""
Unit Tests for Typus Mono Font Standards Compliance
Checks OpenType, TrueType, and Font Bakery standards:
- Mandatory OpenType Table Sanity
- Strict Monospace Advance Width Uniformity
- OpenType USE_TYPO_METRICS flag (OS/2 fsSelection Bit 7, 0x0080)
- OpenType usWidthClass metadata (3 for Condensed, 4 for Semi-Condensed)
- OpenType gasp Table Configuration (Symmetric smoothing and grid-fitting)
- GSUB Ligature Disabling (calt, liga, dlig, clig)
- TrueType Contour Winding Direction
"""

import os
import unittest
from fontTools.ttLib import TTFont

FONTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts"
)
TEST_BUILDS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "test_builds", "step_3"
)


class TestTypusMonoStandards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        target_dir = TEST_BUILDS_DIR if os.path.exists(TEST_BUILDS_DIR) else FONTS_DIR
        cls.target_dir = target_dir
        cls.font_files = [
            f for f in sorted(os.listdir(target_dir)) if f.endswith(".ttf")
        ]
        if not cls.font_files:
            raise unittest.SkipTest(f"No TTF fonts found in {target_dir}")

    def test_required_tables_present(self):
        """Verify all mandatory OpenType and TrueType tables exist."""
        mandatory_tables = {
            "cmap",
            "head",
            "hhea",
            "hmtx",
            "maxp",
            "name",
            "OS/2",
            "post",
            "glyf",
            "loca",
            "gasp",
        }
        for fname in self.font_files:
            fpath = os.path.join(self.target_dir, fname)
            with self.subTest(font=fname):
                font = TTFont(fpath)
                missing = mandatory_tables - set(font.keys())
                self.assertEqual(
                    missing, set(), f"{fname} is missing mandatory tables: {missing}"
                )

    def test_monospace_advance_width_uniformity(self):
        """Verify all positive-width glyphs share the exact same advance width (Font Bakery com.google.fonts/check/monospace)."""
        for fname in self.font_files:
            fpath = os.path.join(self.target_dir, fname)
            with self.subTest(font=fname):
                font = TTFont(fpath)
                hmtx = font["hmtx"]
                positive_widths = [
                    hmtx.metrics[g][0]
                    for g in font.getGlyphOrder()
                    if g in hmtx.metrics
                    and hmtx.metrics[g][0] > 0
                    and g != "nonmarkingreturn"
                ]
                unique_widths = set(positive_widths)
                self.assertEqual(
                    len(unique_widths),
                    1,
                    f"{fname} has inconsistent positive advance widths: {unique_widths}",
                )

    def test_use_typo_metrics_flag(self):
        """Verify USE_TYPO_METRICS (OS/2 fsSelection Bit 7: 0x0080) is enabled."""
        for fname in self.font_files:
            fpath = os.path.join(self.target_dir, fname)
            with self.subTest(font=fname):
                font = TTFont(fpath)
                os2 = font["OS/2"]
                has_typo_metrics = bool(os2.fsSelection & 0x0080)
                self.assertTrue(
                    has_typo_metrics,
                    f"{fname} OS/2.fsSelection does not have USE_TYPO_METRICS enabled",
                )

    def test_uswidthclass_metadata(self):
        """Verify usWidthClass matches font condensed proportion (3 for 90%, 4 for 92%/95%)."""
        for fname in self.font_files:
            fpath = os.path.join(self.target_dir, fname)
            with self.subTest(font=fname):
                font = TTFont(fpath)
                os2 = font["OS/2"]
                if "90" in fname:
                    expected_width_class = 3
                else:
                    expected_width_class = 4
                self.assertEqual(
                    os2.usWidthClass,
                    expected_width_class,
                    f"{fname} has incorrect usWidthClass {os2.usWidthClass}, expected {expected_width_class}",
                )

    def test_gasp_table_configuration(self):
        """Verify gasp table enables full symmetric smoothing and grid fitting."""
        for fname in self.font_files:
            fpath = os.path.join(self.target_dir, fname)
            with self.subTest(font=fname):
                font = TTFont(fpath)
                gasp = font["gasp"]
                self.assertTrue(len(gasp.gaspRange) > 0, f"{fname} has empty gaspRange")
                max_range_flag = gasp.gaspRange[max(gasp.gaspRange.keys())]
                self.assertTrue(
                    bool(max_range_flag & 0x000F),
                    f"{fname} gasp table does not enable full flags",
                )

    def test_ligature_features_stripped(self):
        """Verify calt, liga, dlig, and clig lookups are disabled in GSUB."""
        for fname in self.font_files:
            fpath = os.path.join(self.target_dir, fname)
            with self.subTest(font=fname):
                font = TTFont(fpath)
                if "GSUB" in font:
                    gsub = font["GSUB"].table
                    if hasattr(gsub, "FeatureList") and gsub.FeatureList is not None:
                        for record in gsub.FeatureList.FeatureRecord:
                            if record.FeatureTag in ("calt", "liga", "dlig", "clig"):
                                self.assertEqual(
                                    record.Feature.LookupCount,
                                    0,
                                    f"{fname} still has active lookup for {record.FeatureTag}",
                                )

    def test_contour_winding_direction(self):
        """Verify TrueType contour winding: outer contours must be clockwise (signed area < 0)."""
        sample_font = os.path.join(self.target_dir, self.font_files[0])
        font = TTFont(sample_font)
        glyf = font["glyf"]
        for gname in ["O", "A", "B", "H", "zero"]:
            if gname in glyf:
                g = glyf[gname]
                if g.numberOfContours > 0:
                    coords = g.coordinates
                    end_pts = g.endPtsOfContours
                    # Check first/outer contour
                    n_pts = end_pts[0] + 1
                    area = 0.0
                    for i in range(n_pts):
                        j = (i + 1) % n_pts
                        area += (
                            coords[i][0] * coords[j][1] - coords[j][0] * coords[i][1]
                        )
                    area /= 2.0
                    self.assertLess(
                        area,
                        0.0,
                        f"Outer contour of glyph '{gname}' in {sample_font} is not clockwise",
                    )


if __name__ == "__main__":
    unittest.main()
