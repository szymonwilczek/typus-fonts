#!/usr/bin/env python3
"""
Generate a 3x3 close-up monospace cell grid specimen for Typus Mono.
Showcases character anatomy, baseline alignment, and cell proportions
across 'T', 'y', 'p', 'u', 's', 'M', 'o', 'n', 'o' in a 1000x1100 layout.
"""

import os
from PIL import Image, ImageDraw, ImageFont


def main():
    repo_dir = os.path.expanduser("~/Dokumenty/GitHub/typus-fonts")
    font_path = os.path.join(repo_dir, "fonts/TypusMono92-Regular.ttf")
    font_bold_path = os.path.join(repo_dir, "fonts/TypusMono92-Bold.ttf")
    output_path = os.path.join(repo_dir, "grid_specimen.png")

    S = 3
    BASE_W, BASE_H = 1000, 1100
    W, H = BASE_W * S, BASE_H * S

    img = Image.new("RGB", (W, H), color="#0f0e06")
    draw = ImageDraw.Draw(img)

    header_font = ImageFont.truetype(font_bold_path, 40 * S)
    sub_font = ImageFont.truetype(font_path, 16 * S)
    guide_font = ImageFont.truetype(font_path, 11 * S)

    draw.text(
        (50 * S, 45 * S),
        "Typus Mono 92",
        fill="#c48702",
        font=header_font,
    )
    draw.text(
        (50 * S, 95 * S),
        'Close-up monospace cell anatomy across "T y p u s M o n o" (Semi-Condensed)',
        fill="#cf9f7f",
        font=sub_font,
    )
    draw.line(
        [(50 * S, 130 * S), (950 * S, 130 * S)], fill="#26211d", width=1 * S
    )

    grid_x0 = 50 * S
    grid_y0 = 160 * S
    grid_w = 900 * S
    grid_h = 820 * S

    cols, rows = 3, 3
    gap = 14 * S
    cell_w = (grid_w - (cols - 1) * gap) // cols
    cell_h = (grid_h - (rows - 1) * gap) // rows

    letters = [["T", "y", "p"], ["u", "s", "M"], ["o", "n", "o"]]

    font_size = 175 * S
    letter_font = ImageFont.truetype(font_path, font_size)

    cell_bg = "#14120a"
    cell_border = "#26211d"
    guide_color = "#383028"
    baseline_guide = "#284d38"
    text_color = "#f5efe0"

    for r in range(rows):
        for c in range(cols):
            char = letters[r][c]
            x0 = grid_x0 + c * (cell_w + gap)
            y0 = grid_y0 + r * (cell_h + gap)
            x1 = x0 + cell_w
            y1 = y0 + cell_h

            draw.rectangle(
                [x0, y0, x1, y1], fill=cell_bg, outline=cell_border, width=1 * S
            )

            baseline_y = y0 + round(cell_h * 0.74)
            cap_y = baseline_y - round(font_size * 0.70)

            draw.line(
                [(x0 + 6 * S, cap_y), (x1 - 6 * S, cap_y)],
                fill=guide_color,
                width=1 * S,
            )
            draw.line(
                [(x0 + 6 * S, baseline_y), (x1 - 6 * S, baseline_y)],
                fill=baseline_guide,
                width=1 * S,
            )

            char_w = draw.textlength(char, font=letter_font)
            char_x = x0 + (cell_w - char_w) / 2.0

            draw.text(
                (char_x, baseline_y),
                char,
                fill=text_color,
                font=letter_font,
                anchor="ls",
            )

            draw.text(
                (x0 + 10 * S, y0 + 8 * S),
                f"U+{ord(char):04X}",
                fill="#c48702",
                font=guide_font,
            )
            draw.text(
                (x1 - 60 * S, y0 + 8 * S),
                "552 UPM",
                fill="#3dbbb0",
                font=guide_font,
            )
            draw.text(
                (x0 + 10 * S, baseline_y + 4 * S),
                "baseline",
                fill="#3d7350",
                font=guide_font,
            )

    final_img = img.resize((BASE_W, BASE_H), Image.Resampling.LANCZOS)
    final_img.save(output_path, quality=95)
    print(f"Grid specimen ({BASE_W}x{BASE_H}) generated successfully!")


if __name__ == "__main__":
    main()
