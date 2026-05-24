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


def interpolate_fonts(font1, font2, factor=0.5):
    print(f"Interpolating outlines and metrics with factor {factor}...")
    # interpolate glyf coordinate points
    if "glyf" in font1 and "glyf" in font2:
        glyf1 = font1["glyf"]
        glyf2 = font2["glyf"]
        for glyph_name in font1.getGlyphOrder():
            if glyph_name in glyf2:
                g1 = glyf1[glyph_name]
                g2 = glyf2[glyph_name]

                # bounding boxes
                if (
                    hasattr(g1, "xMin")
                    and hasattr(g2, "xMin")
                    and g1.xMin is not None
                    and g2.xMin is not None
                ):
                    g1.xMin = int(round(g1.xMin * (1 - factor) + g2.xMin * factor))
                    g1.xMax = int(round(g1.xMax * (1 - factor) + g2.xMax * factor))
                    g1.yMin = int(round(g1.yMin * (1 - factor) + g2.yMin * factor))
                    g1.yMax = int(round(g1.yMax * (1 - factor) + g2.yMax * factor))

                # simple glyph coordinates
                if g1.numberOfContours > 0 and g2.numberOfContours > 0:
                    if (
                        hasattr(g1, "coordinates")
                        and hasattr(g2, "coordinates")
                        and g1.coordinates
                        and g2.coordinates
                    ):
                        c1 = g1.coordinates
                        c2 = g2.coordinates
                        if len(c1) == len(c2):
                            for i in range(len(c1)):
                                x = c1[i][0] * (1 - factor) + c2[i][0] * factor
                                y = c1[i][1] * (1 - factor) + c2[i][1] * factor
                                c1[i] = (x, y)

                # composite glyph offsets
                elif g1.numberOfContours < 0 and g2.numberOfContours < 0:
                    if hasattr(g1, "components") and hasattr(g2, "components"):
                        for comp1, comp2 in zip(g1.components, g2.components):
                            comp1.x = int(
                                round(comp1.x * (1 - factor) + comp2.x * factor)
                            )
                            comp1.y = int(
                                round(comp1.y * (1 - factor) + comp2.y * factor)
                            )

    # interpolate hmtx advance widths & LSBs
    if "hmtx" in font1 and "hmtx" in font2:
        hmtx1 = font1["hmtx"]
        hmtx2 = font2["hmtx"]
        for glyph_name in hmtx1.metrics.keys():
            if glyph_name in hmtx2.metrics:
                w1, lsb1 = hmtx1[glyph_name]
                w2, lsb2 = hmtx2[glyph_name]
                hmtx1[glyph_name] = (
                    int(round(w1 * (1 - factor) + w2 * factor)),
                    int(round(lsb1 * (1 - factor) + lsb2 * factor)),
                )
    return font1


def set_weight_class(font, style_name):
    if "OS/2" in font:
        os2 = font["OS/2"]
        style_lower = style_name.lower()
        print(f"Setting OS/2 usWeightClass for style '{style_name}'...")
        if "thin" in style_lower:
            os2.usWeightClass = 100
        elif "extralight" in style_lower or "extra light" in style_lower:
            os2.usWeightClass = 200
        elif "light" in style_lower:
            os2.usWeightClass = 300
        elif (
            "demibold" in style_lower
            or "demi bold" in style_lower
            or "demi" in style_lower
        ):
            os2.usWeightClass = 650
        elif "semibold" in style_lower or "semi bold" in style_lower:
            os2.usWeightClass = 600
        elif "bold" in style_lower:
            os2.usWeightClass = 700
        elif "extrabold" in style_lower or "extra bold" in style_lower:
            os2.usWeightClass = 800
        elif "black" in style_lower or "heavy" in style_lower:
            os2.usWeightClass = 900
        else:
            os2.usWeightClass = 400  # Regular


def main():
    parser = argparse.ArgumentParser(
        description="Create a custom condensed, ligature-free font."
    )
    parser.add_argument("--input", required=True, help="Path to input TTF font file")
    parser.add_argument(
        "--input2", help="Optional second input TTF font file for weight interpolation"
    )
    parser.add_argument(
        "--factor",
        type=float,
        default=0.5,
        help="Interpolation factor between input and input2 (0.0 to 1.0, default 0.5)",
    )
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

    if args.input2:
        if not os.path.exists(args.input2):
            print(f"Error: Second input file '{args.input2}' not found.")
            sys.exit(1)
        print(f"Loading first font: {args.input}")
        font1 = TTFont(args.input)
        print(f"Loading second font: {args.input2}")
        font2 = TTFont(args.input2)
        font = interpolate_fonts(font1, font2, args.factor)
    else:
        print(f"Loading font: {args.input}")
        font = TTFont(args.input)

    rename_font(font, args.name, args.style)
    set_weight_class(font, args.style)
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
