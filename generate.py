import argparse
import os
import sys

from fontTools.ttLib import TTFont


def rename_font(font, new_family_name, new_style_name):
    print(
        f"Renaming font metadata to Family: '{new_family_name}', Style: '{new_style_name}'..."
    )
    name_table = font["name"]

    family_compat = new_family_name.replace(" ", "")
    style_compat = new_style_name.replace(" ", "")
    full_name = f"{new_family_name} {new_style_name}"
    postscript_name = f"{family_compat}-{style_compat}"
    unique_id = f"{postscript_name};unknown"

    for record in name_table.names:
        # 1: Family Name
        # 2: Subfamily Name (Style)
        # 3: Unique ID
        # 4: Full Name
        # 6: PostScript Name
        # 16: Typographic Family Name
        # 17: Typographic Subfamily Name
        try:
            if record.nameID == 1:
                record.string = new_family_name.encode(record.getEncoding())
            elif record.nameID == 2:
                record.string = new_style_name.encode(record.getEncoding())
            elif record.nameID == 3:
                record.string = unique_id.encode(record.getEncoding())
            elif record.nameID == 4:
                record.string = full_name.encode(record.getEncoding())
            elif record.nameID == 6:
                record.string = postscript_name.encode(record.getEncoding())
            elif record.nameID == 16:
                record.string = new_family_name.encode(record.getEncoding())
            elif record.nameID == 17:
                record.string = new_style_name.encode(record.getEncoding())
        except Exception as e:
            print(f"Warning: could not encode nameID {record.nameID}: {e}")


def scale_horizontal_metrics(font, width_scale, no_scale_outlines=False):
    if no_scale_outlines:
        print(f"Scaling advance widths only (spacing adjustment) by {width_scale}...")
    else:
        print(f"Scaling advance widths and glyph outlines by {width_scale}...")

    # scale coordinates of TrueType glyph outlines in-place (if not disabled)
    if "glyf" in font and not no_scale_outlines:
        glyf_table = font["glyf"]
        for glyph_name in font.getGlyphOrder():
            glyph = glyf_table[glyph_name]

            # scale bounding box limits directly
            if hasattr(glyph, "xMin") and glyph.xMin is not None:
                glyph.xMin = int(round(glyph.xMin * width_scale))
            if hasattr(glyph, "xMax") and glyph.xMax is not None:
                glyph.xMax = int(round(glyph.xMax * width_scale))

            if glyph.numberOfContours > 0:
                # simple glyph: scale coordinates in-place
                if hasattr(glyph, "coordinates") and glyph.coordinates:
                    glyph.coordinates.scale((width_scale, 1.0))
            elif glyph.numberOfContours < 0:
                # composite glyph: scale component x offsets
                if hasattr(glyph, "components"):
                    for component in glyph.components:
                        component.x = int(round(component.x * width_scale))

    # scale advance width and left side bearing in the hmtx table
    # NOTE: this must always be scaled to ensure character spacing matches the grid
    if "hmtx" in font:
        hmtx = font["hmtx"]
        for glyph_name in hmtx.metrics.keys():
            width, lsb = hmtx[glyph_name]
            hmtx[glyph_name] = (
                int(round(width * width_scale)),
                int(round(lsb * width_scale)),
            )


def adjust_vertical_metrics(font, height_scale):
    print(f"Adjusting vertical metrics by factor {height_scale}...")

    if "hhea" in font:
        hhea = font["hhea"]
        hhea.ascent = int(round(hhea.ascent * height_scale))
        hhea.descent = int(round(hhea.descent * height_scale))
        hhea.lineGap = int(round(hhea.lineGap * height_scale))

    if "OS/2" in font:
        os2 = font["OS/2"]
        os2.sTypoAscender = int(round(os2.sTypoAscender * height_scale))
        os2.sTypoDescender = int(round(os2.sTypoDescender * height_scale))
        os2.sTypoLineGap = int(round(os2.sTypoLineGap * height_scale))
        os2.usWinAscent = int(round(os2.usWinAscent * height_scale))
        os2.usWinDescent = int(round(os2.usWinDescent * height_scale))


def strip_ligatures(font):
    print("Stripping GSUB ligatures (calt, liga, dlig, clig)...")
    if "GSUB" in font:
        gsub = font["GSUB"].table
        if hasattr(gsub, "FeatureList") and gsub.FeatureList is not None:
            for record in gsub.FeatureList.FeatureRecord:
                tag = record.FeatureTag
                if tag in ("calt", "liga", "dlig", "clig"):
                    print(f"Disabling GSUB feature lookup: {tag}")
                    feature = record.Feature
                    feature.LookupCount = 0
                    feature.LookupListIndex = []


def main():
    parser = argparse.ArgumentParser(
        description="Create a custom condensed, ligature-free font."
    )
    parser.add_argument("--input", required=True, help="Path to input TTF font file")
    parser.add_argument(
        "--output", required=True, help="Path to save output TTF font file"
    )
    parser.add_argument("--name", default="Typus Mono", help="New font family name")
    parser.add_argument(
        "--style",
        required=True,
        help="New font style name (e.g. Regular, SemiBold, Bold, etc.)",
    )
    parser.add_argument(
        "--width-scale",
        type=float,
        default=0.9,
        help="Horizontal scale factor (0.0 to 1.0)",
    )
    parser.add_argument(
        "--height-scale",
        type=float,
        default=1.05,
        help="Line height metrics scale factor",
    )
    parser.add_argument(
        "--no-scale-outlines",
        action="store_true",
        help="Do not scale glyph outlines horizontally (spacing adjustment only)",
    )
    parser.add_argument(
        "--no-strip-ligatures", action="store_true", help="Do not strip ligatures"
    )
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found.")
        sys.exit(1)

    print(f"Loading font: {args.input}")
    font = TTFont(args.input)

    rename_font(font, args.name, args.style)
    scale_horizontal_metrics(font, args.width_scale, args.no_scale_outlines)
    adjust_vertical_metrics(font, args.height_scale)

    if not args.no_strip_ligatures:
        strip_ligatures(font)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    print(f"Saving modified font to: {args.output}")
    font.save(args.output)
    print("Generation complete!")


if __name__ == "__main__":
    main()
