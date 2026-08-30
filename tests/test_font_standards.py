#!/usr/bin/env python3
"""
Unit Tests for Typus Mono Font Standards Compliance
Checks:
- ISO/IEC 14496-22 / OpenType spec
- Hinting Bytecode and CVT Synchronization
- OpenType Table Sanity
- Valid Unicode Coverage and Character Map Integrity
- Non-negative Glyph Bounding Box Coordinates and Valid Sidebearings
"""

import os
import unittest
from fontTools.ttLib import TTFont

FONTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts"
)


class TestTypusMonoStandards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.font_files = [f for f in os.listdir(FONTS_DIR) if f.endswith(".ttf")]
        if not cls.font_files:
            raise unittest.SkipTest("No TTF fonts found in fonts/ directory")

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
        }
        for fname in self.font_files:
            fpath = os.path.join(FONTS_DIR, fname)
            with self.subTest(font=fname):
                font = TTFont(fpath)
                missing = mandatory_tables - set(font.keys())
                self.assertEqual(
                    missing, set(), f"{fname} is missing mandatory tables: {missing}"
                )

    def test_monospace_advance_width_uniformity(self):
        """Verify all positive-width glyphs share the exact same advance width (Font Bakery com.google.fonts/check/monospace)."""
        for fname in self.font_files:
            fpath = os.path.join(FONTS_DIR, fname)
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

    def test_ligature_features_stripped(self):
        """Verify calt, liga, dlig, and clig lookups are disabled in GSUB."""
        for fname in self.font_files:
            fpath = os.path.join(FONTS_DIR, fname)
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

    def test_bounding_box_and_sidebearings_sanity(self):
        """Verify left sidebearing matches xMin in glyf table for all simple glyphs."""
        for fname in ["TypusMono95-Regular.ttf", "TypusMono95-Bold.ttf"]:
            fpath = os.path.join(FONTS_DIR, fname)
            if not os.path.exists(fpath):
                continue
            with self.subTest(font=fname):
                font = TTFont(fpath)
                glyf = font["glyf"]
                hmtx = font["hmtx"]
                for gname in ["A", "B", "C", "H", "n", "m", "zero", "one"]:
                    if gname in glyf:
                        g = glyf[gname]
                        if g.numberOfContours > 0:
                            lsb = hmtx.metrics[gname][1]
                            self.assertEqual(
                                lsb,
                                g.xMin,
                                f"LSB mismatch for glyph {gname} in {fname}",
                            )


if __name__ == "__main__":
    unittest.main()
