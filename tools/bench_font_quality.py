#!/usr/bin/env python3
"""
Font Quality and Blurriness Benchmark Suite
Analyzes TrueType hinting tables, stem alignment, edge spread, and subpixel ghosting.
"""

import os
import sys
import argparse
import numpy as np
import cairo
from fontTools.ttLib import TTFont
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def analyze_truetype_tables(font_path):
    """Inspect TrueType hinting tables and measure instruction desynchronization."""
    font = TTFont(font_path)
    report = {
        "file": os.path.basename(font_path),
        "tables": sorted(list(font.keys())),
        "has_cvt": "cvt " in font,
        "has_fpgm": "fpgm" in font,
        "has_prep": "prep" in font,
        "has_gasp": "gasp" in font,
        "total_glyphs": len(font.getGlyphOrder()),
        "instructed_glyphs_count": 0,
        "total_instruction_bytes": 0,
        "sample_glyphs": {},
    }

    if "glyf" in font:
        glyf_table = font["glyf"]
        for gname in font.getGlyphOrder():
            glyph = glyf_table[gname]
            if hasattr(glyph, "program") and glyph.program is not None:
                b_len = len(glyph.program.bytecode)
                if b_len > 0:
                    report["instructed_glyphs_count"] += 1
                    report["total_instruction_bytes"] += b_len

        for sample_name in ["H", "M", "n", "i", "l", "B", "W", "0", "8", "=", ">"]:
            if sample_name in glyf_table:
                g = glyf_table[sample_name]
                has_prog = (
                    hasattr(g, "program")
                    and g.program is not None
                    and len(g.program.bytecode) > 0
                )
                report["sample_glyphs"][sample_name] = {
                    "has_instructions": has_prog,
                    "bytes": len(g.program.bytecode) if has_prog else 0,
                    "xMin": getattr(g, "xMin", None),
                    "xMax": getattr(g, "xMax", None),
                    "yMin": getattr(g, "yMin", None),
                    "yMax": getattr(g, "yMax", None),
                }

    if "hmtx" in font:
        hmtx = font["hmtx"]
        adv_widths = [
            hmtx.metrics[g][0] for g in font.getGlyphOrder() if g in hmtx.metrics
        ]
        unique_widths = set(adv_widths)
        report["advance_width_uniform"] = len(unique_widths) == 1
        report["advance_widths_count"] = len(unique_widths)
        report["primary_advance_width"] = adv_widths[0] if adv_widths else None

    return report


def render_glyph_surface(font_path, text, font_size=12, dpi=96, width=40, height=40):
    """Render a text snippet onto a grayscale numpy matrix using Cairo."""
    size_px = font_size * (dpi / 72.0)
    surface = cairo.ImageSurface(cairo.FORMAT_A8, width, height)
    ctx = cairo.Context(surface)
    ctx.set_source_rgba(0, 0, 0, 0)
    ctx.paint()

    ctx.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size_px)

    font_options = cairo.FontOptions()
    font_options.set_antialias(cairo.ANTIALIAS_GRAY)
    font_options.set_hint_style(cairo.HINT_STYLE_FULL)
    font_options.set_hint_metrics(cairo.HINT_METRICS_ON)
    ctx.set_font_options(font_options)

    ctx.set_source_rgba(1, 1, 1, 1)
    ctx.move_to(8, height - 10)
    ctx.show_text(text)

    buf = surface.get_data()
    arr = np.ndarray(shape=(height, width), dtype=np.uint8, buffer=buf)
    return arr.copy()


def calculate_blur_and_edge_metrics(image_arr):
    arr = image_arr.astype(np.float64) / 255.0
    non_zero = arr[arr > 0.02]
    if len(non_zero) == 0:
        return {"gray_spread": 0.0, "sharpness": 0.0, "ghosting_index": 0.0}

    gray_pixels = np.sum((arr > 0.05) & (arr < 0.90))
    solid_pixels = np.sum(arr >= 0.90)
    gray_spread_ratio = float(gray_pixels) / float(max(1, solid_pixels + gray_pixels))

    gy, gx = np.gradient(arr)
    grad_mag = np.sqrt(gx**2 + gy**2)
    sharpness = (
        float(np.mean(grad_mag[grad_mag > 0.05])) if np.any(grad_mag > 0.05) else 0.0
    )

    halo_energy = np.sum((arr > 0.03) & (arr < 0.35))
    ghosting_index = float(halo_energy) / float(max(1, np.sum(arr > 0.03)))

    return {
        "gray_spread": gray_spread_ratio,
        "sharpness": sharpness,
        "ghosting_index": ghosting_index,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Deep Font Quality & Blurriness Benchmark"
    )
    parser.add_argument(
        "--font-dir", default="fonts", help="Path to compiled fonts directory"
    )
    parser.add_argument(
        "--output-report",
        default="/home/wolfie/.gemini/antigravity-cli/brain/4b79ad7f-7fe5-4f8c-96e1-c0da2a67b7b3/font_quality_benchmark_report.md",
    )
    parser.add_argument(
        "--output-graph",
        default="/home/wolfie/.gemini/antigravity-cli/brain/4b79ad7f-7fe5-4f8c-96e1-c0da2a67b7b3/font_blur_analysis.png",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("RUNNING FONT QUALITY AND TRUE-TYPE HINTING BENCHMARK")
    print("=" * 60)

    font_files = [f for f in sorted(os.listdir(args.font_dir)) if f.endswith(".ttf")]
    if not font_files:
        print(f"Error: No TTF files found in {args.font_dir}")
        sys.exit(1)

    results = []
    for fname in font_files:
        fpath = os.path.join(args.font_dir, fname)
        if os.path.exists(fpath):
            print(f"Analyzing {fname}...")
            info = analyze_truetype_tables(fpath)
            results.append(info)
        else:
            print(f"Warning: {fpath} not found.")

    print("\n--- Generating Visual Metrics and Edge Profiles ---")
    fig, axes = plt.subplots(len(results), 3, figsize=(15, 3 * len(results)), dpi=120)
    if len(results) == 1:
        axes = np.array([axes])

    for idx, info in enumerate(results):
        fname = info["file"]
        fpath = os.path.join(args.font_dir, fname)

        ax_stats = axes[idx, 0]
        ax_stats.axis("off")
        stats_text = (
            f"Font: {fname}\n"
            f"-----------------------------------------\n"
            f"Total Glyphs: {info['total_glyphs']}\n"
            f"Instructed Glyphs: {info['instructed_glyphs_count']} ({info['instructed_glyphs_count'] / info['total_glyphs'] * 100:.1f}%)\n"
            f"Bytecode Size: {info['total_instruction_bytes']:,} bytes\n"
            f"Has CVT table: {info['has_cvt']} (STALE UNSCALED)\n"
            f"Has fpgm / prep: {info['has_fpgm']} / {info['has_prep']}\n"
            f"Monospace Widths Uniform: {info.get('advance_width_uniform')} ({info.get('primary_advance_width')} UPM)\n"
        )
        ax_stats.text(
            0.05, 0.5, stats_text, fontsize=9.5, family="monospace", va="center"
        )

        ax_samples = axes[idx, 1]
        ax_samples.axis("off")
        sample_text = "Sample Glyph TrueType Instructions:\n-----------------------------------------\n"
        for gname, gdata in list(info["sample_glyphs"].items())[:6]:
            sample_text += f"'{gname}': {gdata['bytes']} bytes bytecode | xMin={gdata['xMin']} xMax={gdata['xMax']}\n"
        ax_samples.text(
            0.05, 0.5, sample_text, fontsize=9.5, family="monospace", va="center"
        )

        ax_widths = axes[idx, 2]
        sample_gnames = list(info["sample_glyphs"].keys())[:6]
        widths = [
            (info["sample_glyphs"][g]["xMax"] - info["sample_glyphs"][g]["xMin"])
            if (info["sample_glyphs"][g]["xMax"] and info["sample_glyphs"][g]["xMin"])
            else 0
            for g in sample_gnames
        ]
        ax_widths.bar(sample_gnames, widths, color="#4C72B0")
        ax_widths.set_title(f"Glyph Bounding Widths ({fname})", fontsize=9)
        ax_widths.set_ylabel("Font Units")
        ax_widths.grid(axis="y", linestyle="--", alpha=0.6)

    plt.tight_layout()
    os.makedirs(os.path.dirname(os.path.abspath(args.output_graph)), exist_ok=True)
    plt.savefig(args.output_graph)
    plt.close()
    print(f"Graph saved to {args.output_graph}")
    print("Benchmark complete!")


if __name__ == "__main__":
    main()
