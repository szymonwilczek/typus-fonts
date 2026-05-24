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

    title_font = ImageFont.truetype(font_sb_path, 40)
    tagline_font = ImageFont.truetype(font_reg_path, 16)
    section_title_font = ImageFont.truetype(font_sb_path, 18)
    char_font = ImageFont.truetype(
        font_sb_path, 20
    )  # SemiBold for character set preview

    code_font_orig = ImageFont.truetype(orig_path, 15)
    code_font_typus_95 = ImageFont.truetype(font_sb_95_path, 15)
    code_font_typus_92 = ImageFont.truetype(font_sb_92_path, 15)
    code_font_typus_90 = ImageFont.truetype(font_sb_90_path, 15)

    ruler_font = ImageFont.truetype(font_light_path, 11)

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

    img = Image.new("RGB", (1000, 920), color=bg_color)
    draw = ImageDraw.Draw(img)

    # header
    draw.text((50, 45), "Typus Mono", fill=keyword_color, font=title_font)
    draw.text(
        (50, 95),
        "A custom spacing-only condensed family derived from JetBrains Mono",
        fill=comment_color,
        font=tagline_font,
    )
    draw.line([(50, 130), (950, 130)], fill=border_color, width=1)

    # character set
    draw.text(
        (50, 155),
        "/* Character Set (Typus Mono 95 SemiBold) */",
        fill=comment_color,
        font=section_title_font,
    )
    chars_line1 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    chars_line2 = "abcdefghijklmnopqrstuvwxyz"
    chars_line3 = "0123456789  !=  ->  ==  <=  >="
    chars_line4 = "!@#$%^&*()_+-=[]{}|;':\",./<>?  (Stripped Ligatures)"

    draw.text((50, 190), chars_line1, fill=fg_color, font=char_font)
    draw.text((50, 225), chars_line2, fill=fg_color, font=char_font)
    draw.text((50, 260), chars_line3, fill=string_color, font=char_font)
    draw.text((50, 295), chars_line4, fill=fg_color, font=char_font)

    draw.line([(50, 345), (950, 345)], fill=border_color, width=1)

    # spacing comparision
    draw.text(
        (50, 370),
        "/* Spacing Comparison (Cell Width Compression - SemiBold) */",
        fill=comment_color,
        font=section_title_font,
    )

    code_line = "static int wait_for_socket(int fd, int events, int timeout_ms) {"

    # JetBrains Mono
    draw.text(
        (50, 410),
        "// Original JetBrains Mono (SemiBold)",
        fill=comment_color,
        font=ruler_font,
    )
    draw.text((50, 430), code_line, fill=fg_color, font=code_font_orig)
    orig_w = int(draw.textlength(code_line, font=code_font_orig))
    draw_ruler(
        draw,
        50,
        458,
        orig_w,
        f"{orig_w}px (Original JetBrains Mono)",
        color_line=red_accent,
        color_text=red_accent,
        font=ruler_font,
    )

    # Typus Mono 95
    draw.text(
        (50, 505), "// Typus Mono 95 (SemiBold)", fill=comment_color, font=ruler_font
    )
    draw.text((50, 525), code_line, fill=fg_color, font=code_font_typus_95)
    w_95 = int(draw.textlength(code_line, font=code_font_typus_95))
    draw_ruler(
        draw,
        50,
        553,
        w_95,
        f"{w_95}px (Typus Mono 95)",
        color_line=green_accent,
        color_text=green_accent,
        font=ruler_font,
    )

    # Typus Mono 92
    draw.text(
        (50, 600), "// Typus Mono 92 (SemiBold)", fill=comment_color, font=ruler_font
    )
    draw.text((50, 620), code_line, fill=fg_color, font=code_font_typus_92)
    w_92 = int(draw.textlength(code_line, font=code_font_typus_92))
    draw_ruler(
        draw,
        50,
        648,
        w_92,
        f"{w_92}px (Typus Mono 92)",
        color_line=teal_color,
        color_text=teal_color,
        font=ruler_font,
    )

    # Typus Mono 90
    draw.text(
        (50, 695), "// Typus Mono 90 (SemiBold)", fill=comment_color, font=ruler_font
    )
    draw.text((50, 715), code_line, fill=fg_color, font=code_font_typus_90)
    w_90 = int(draw.textlength(code_line, font=code_font_typus_90))
    draw_ruler(
        draw,
        50,
        743,
        w_90,
        f"{w_90}px (Typus Mono 90)",
        color_line=blue_accent,
        color_text=blue_accent,
        font=ruler_font,
    )

    draw.line([(50, 785), (950, 785)], fill=border_color, width=1)

    # weight showcase
    draw.text(
        (50, 805),
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

    x_offset = 50
    for w_name, w_path, w_color in weights_info:
        w_font = ImageFont.truetype(w_path, 16)
        draw.text((x_offset, 840), w_name, fill=teal_color, font=ruler_font)
        sample_text = "The quick brown fox"
        draw.text((x_offset, 860), sample_text, fill=w_color, font=w_font)
        x_offset += 153

    img.save(output_path)
    print("Preview generated successfully!")


if __name__ == "__main__":
    main()
