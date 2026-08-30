import os

from PIL import Image, ImageDraw, ImageFont


def draw_ruler(
    draw, x, y, width, label, color_line="#4a5568", color_text="#a0aec0", font=None
):
    # horizontal line
    draw.line([(x, y), (x + width, y)], fill=color_line, width=1)

    # vertical caps
    draw.line([(x, y - 5), (x, y + 5)], fill=color_line, width=1)
    draw.line([(x + width, y - 5), (x + width, y + 5)], fill=color_line, width=1)

    # text label in the middle
    text_w = draw.textlength(label, font=font)
    draw.rectangle(
        [
            (x + width / 2 - text_w / 2 - 6, y - 8),
            (x + width / 2 + text_w / 2 + 6, y + 8),
        ],
        fill="#0f0e06",
    )  # ef-autumn background
    draw.text((x + width / 2 - text_w / 2, y - 6), label, fill=color_text, font=font)


def main():
    repo_dir = os.path.expanduser("~/Dokumenty/GitHub/typus-fonts")
    orig_path = os.path.expanduser(
        "~/.local/share/fonts/JetBrainsMono/JetBrainsMonoNerdFont-SemiBold.ttf"
    )
    output_path = os.path.join(repo_dir, "preview.png")

    font_thin_path = os.path.join(repo_dir, "fonts/TypusMono95-Thin.ttf")
    font_light_path = os.path.join(repo_dir, "fonts/TypusMono95-Light.ttf")
    font_reg_path = os.path.join(repo_dir, "fonts/TypusMono95-Regular.ttf")
    font_sb_path = os.path.join(repo_dir, "fonts/TypusMono95-SemiBold.ttf")
    font_db_path = os.path.join(repo_dir, "fonts/TypusMono95-Demibold.ttf")
    font_bold_path = os.path.join(repo_dir, "fonts/TypusMono95-Bold.ttf")

    font_sb_95_path = os.path.join(repo_dir, "fonts/TypusMono95-SemiBold.ttf")
    font_sb_92_path = os.path.join(repo_dir, "fonts/TypusMono92-SemiBold.ttf")
    font_sb_90_path = os.path.join(repo_dir, "fonts/TypusMono90-SemiBold.ttf")

    S = 3  # 3x supersampling
    base_w, base_h = 1000, 1100
    w, h = base_w * S, base_h * S

    def draw_ruler_scaled(
        draw, x, y, width, label, color_line="#4a5568", color_text="#a0aec0", font=None
    ):
        draw.line([(x, y), (x + width, y)], fill=color_line, width=1 * S)
        draw.line([(x, y - 5 * S), (x, y + 5 * S)], fill=color_line, width=1 * S)
        draw.line(
            [(x + width, y - 5 * S), (x + width, y + 5 * S)],
            fill=color_line,
            width=1 * S,
        )
        text_w = draw.textlength(label, font=font)
        draw.rectangle(
            [
                (x + width / 2 - text_w / 2 - 6 * S, y - 8 * S),
                (x + width / 2 + text_w / 2 + 6 * S, y + 8 * S),
            ],
            fill="#0f0e06",
        )
        draw.text(
            (x + width / 2 - text_w / 2, y - 6 * S),
            label,
            fill=color_text,
            font=font,
        )

    title_font = ImageFont.truetype(font_sb_path, 40 * S)
    tagline_font = ImageFont.truetype(font_reg_path, 16 * S)
    section_title_font = ImageFont.truetype(font_sb_path, 18 * S)
    char_font = ImageFont.truetype(font_sb_path, 20 * S)

    code_font_orig = ImageFont.truetype(orig_path, 15 * S)
    code_font_typus_95 = ImageFont.truetype(font_sb_95_path, 15 * S)
    code_font_typus_92 = ImageFont.truetype(font_sb_92_path, 15 * S)
    code_font_typus_90 = ImageFont.truetype(font_sb_90_path, 15 * S)

    ruler_font = ImageFont.truetype(font_light_path, 11 * S)

    bg_color = "#0f0e06"
    fg_color = "#cfbcba"
    keyword_color = "#c48702"
    comment_color = "#cf9f7f"
    string_color = "#f06a3f"
    teal_color = "#3dbbb0"
    blue_accent = "#6fafff"
    red_accent = "#ef656a"
    green_accent = "#2fa526"
    border_color = "#26211d"

    img = Image.new("RGB", (w, h), color=bg_color)
    draw = ImageDraw.Draw(img)

    # header
    draw.text((50 * S, 45 * S), "Typus Mono", fill=keyword_color, font=title_font)
    draw.text(
        (50 * S, 95 * S),
        "A custom condensed, ligature-free monospace family with full Nerd Font symbols",
        fill=comment_color,
        font=tagline_font,
    )
    draw.line([(50 * S, 130 * S), (950 * S, 130 * S)], fill=border_color, width=1 * S)

    # character set
    draw.text(
        (50 * S, 155 * S),
        "/* Character Set & Symbols (Typus Mono 95 SemiBold) */",
        fill=comment_color,
        font=section_title_font,
    )
    chars_line1 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    chars_line2 = "abcdefghijklmnopqrstuvwxyz"
    chars_line3 = "0123456789  !=  ->  ==  <=  >="
    chars_line4 = "!@#$%^&*()_+-=[]{}|;':\",./<>?  (Stripped Ligatures)"
    chars_line5 = "󰣛                              "

    draw.text((50 * S, 185 * S), chars_line1, fill=fg_color, font=char_font)
    draw.text((50 * S, 218 * S), chars_line2, fill=fg_color, font=char_font)
    draw.text((50 * S, 251 * S), chars_line3, fill=string_color, font=char_font)
    draw.text((50 * S, 284 * S), chars_line4, fill=fg_color, font=char_font)
    draw.text((50 * S, 317 * S), chars_line5, fill=teal_color, font=char_font)

    draw.line([(50 * S, 360 * S), (950 * S, 360 * S)], fill=border_color, width=1 * S)

    # spacing comparision
    draw.text(
        (50 * S, 380 * S),
        "/* Spacing Comparison (Cell Width Compression - SemiBold) */",
        fill=comment_color,
        font=section_title_font,
    )

    code_line = "static int wait_for_socket(int fd, int events, int timeout_ms) {"

    # JetBrains Mono
    draw.text(
        (50 * S, 415 * S),
        "// Original JetBrains Mono (SemiBold)",
        fill=comment_color,
        font=ruler_font,
    )
    draw.text((50 * S, 435 * S), code_line, fill=fg_color, font=code_font_orig)
    orig_w = int(draw.textlength(code_line, font=code_font_orig))
    draw_ruler_scaled(
        draw,
        50 * S,
        463 * S,
        orig_w,
        f"{orig_w // S}px (Original JetBrains Mono)",
        color_line=red_accent,
        color_text=red_accent,
        font=ruler_font,
    )

    # Typus Mono 95
    draw.text(
        (50 * S, 505 * S),
        "// Typus Mono 95 (SemiBold)",
        fill=comment_color,
        font=ruler_font,
    )
    draw.text((50 * S, 525 * S), code_line, fill=fg_color, font=code_font_typus_95)
    w_95 = int(draw.textlength(code_line, font=code_font_typus_95))
    draw_ruler_scaled(
        draw,
        50 * S,
        553 * S,
        w_95,
        f"{w_95 // S}px (Typus Mono 95)",
        color_line=green_accent,
        color_text=green_accent,
        font=ruler_font,
    )

    # Typus Mono 92
    draw.text(
        (50 * S, 595 * S),
        "// Typus Mono 92 (SemiBold)",
        fill=comment_color,
        font=ruler_font,
    )
    draw.text((50 * S, 615 * S), code_line, fill=fg_color, font=code_font_typus_92)
    w_92 = int(draw.textlength(code_line, font=code_font_typus_92))
    draw_ruler_scaled(
        draw,
        50 * S,
        643 * S,
        w_92,
        f"{w_92 // S}px (Typus Mono 92)",
        color_line=teal_color,
        color_text=teal_color,
        font=ruler_font,
    )

    # Typus Mono 90
    draw.text(
        (50 * S, 685 * S),
        "// Typus Mono 90 (SemiBold)",
        fill=comment_color,
        font=ruler_font,
    )
    draw.text((50 * S, 705 * S), code_line, fill=fg_color, font=code_font_typus_90)
    w_90 = int(draw.textlength(code_line, font=code_font_typus_90))
    draw_ruler_scaled(
        draw,
        50 * S,
        733 * S,
        w_90,
        f"{w_90 // S}px (Typus Mono 90)",
        color_line=blue_accent,
        color_text=blue_accent,
        font=ruler_font,
    )

    draw.line([(50 * S, 775 * S), (950 * S, 775 * S)], fill=border_color, width=1 * S)

    # weight showcase
    draw.text(
        (50 * S, 795 * S),
        "/* Typus Mono 95 Weights (Compensated for FreeType) */",
        fill=comment_color,
        font=section_title_font,
    )

    weights_info = [
        ("Thin", font_thin_path, fg_color),
        ("Light", font_light_path, fg_color),
        ("Regular", font_reg_path, fg_color),
        ("SemiBold", font_sb_path, fg_color),
        ("DemiBold", font_db_path, fg_color),
        ("Bold", font_bold_path, fg_color),
    ]

    y_offset = 830 * S
    for w_name, w_path, w_color in weights_info:
        w_font = ImageFont.truetype(w_path, 16 * S)
        draw.text((50 * S, y_offset), w_name, fill=teal_color, font=ruler_font)
        sample_text = "The quick brown fox jumps over the lazy dog."
        draw.text((200 * S, y_offset - 3 * S), sample_text, fill=w_color, font=w_font)
        y_offset += 32 * S

    final_img = img.resize((base_w, base_h), Image.Resampling.LANCZOS)
    final_img.save(output_path, quality=95)
    print("Preview generated successfully!")


if __name__ == "__main__":
    main()
