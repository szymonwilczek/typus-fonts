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
        fill="#0f1419",
    )
    draw.text((x + width / 2 - text_w / 2, y - 6), label, fill=color_text, font=font)


def main():
    repo_dir = "~/Dokumenty/GitHub/typus-fonts"
    orig_path = "~/.local/share/fonts/JetBrainsMono/JetBrainsMonoNerdFont-SemiBold.ttf"
    output_path = os.path.join(repo_dir, "preview.png")

    font_reg_path = os.path.join(repo_dir, "fonts/TypusMono-Regular.ttf")
    font_sb_path = os.path.join(repo_dir, "fonts/TypusMono-SemiBold.ttf")
    font_bold_path = os.path.join(repo_dir, "fonts/TypusMono-Bold.ttf")
    font_light_path = os.path.join(repo_dir, "fonts/TypusMono-Light.ttf")
    font_thin_path = os.path.join(repo_dir, "fonts/TypusMono-Thin.ttf")

    title_font = ImageFont.truetype(font_sb_path, 40)
    tagline_font = ImageFont.truetype(font_reg_path, 16)
    section_title_font = ImageFont.truetype(font_sb_path, 18)
    char_font = ImageFont.truetype(font_reg_path, 20)
    code_font_orig = ImageFont.truetype(orig_path, 15)
    code_font_typus = ImageFont.truetype(font_reg_path, 15)
    ruler_font = ImageFont.truetype(font_light_path, 11)

    bg_color = "#0f1419"
    img = Image.new("RGB", (1000, 750), color=bg_color)
    draw = ImageDraw.Draw(img)

    # header
    draw.text((50, 45), "Typus Mono", fill="#ffb454", font=title_font)
    draw.text(
        (50, 95),
        "A custom spacing-only condensed variant of JetBrains Mono",
        fill="#a0a0a0",
        font=tagline_font,
    )
    draw.line([(50, 130), (950, 130)], fill="#243347", width=1)

    # character set
    draw.text((50, 155), "/* Character Set */", fill="#5c6773", font=section_title_font)
    chars_line1 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    chars_line2 = "abcdefghijklmnopqrstuvwxyz"
    chars_line3 = "0123456789  !=  ->  ==  <=  >="
    chars_line4 = "!@#$%^&*()_+-=[]{}|;':\",./<>?  (Stripped Ligatures)"

    draw.text((50, 190), chars_line1, fill="#e6e6e6", font=char_font)
    draw.text((50, 225), chars_line2, fill="#e6e6e6", font=char_font)
    draw.text((50, 260), chars_line3, fill="#ff7733", font=char_font)
    draw.text((50, 295), chars_line4, fill="#b3b1ad", font=char_font)

    draw.line([(50, 345), (950, 345)], fill="#243347", width=1)

    # spacing comparision
    draw.text(
        (50, 370),
        "/* Spacing Comparison (Cell Width Compression) */",
        fill="#5c6773",
        font=section_title_font,
    )

    code_line = "static int wait_for_socket(int fd, int events, int timeout_ms) {"

    # Original JetBrains Mono
    draw.text(
        (50, 410),
        "// Original JetBrains Mono (SemiBold)",
        fill="#707a8c",
        font=ruler_font,
    )
    draw.text((50, 430), code_line, fill="#e6e6e6", font=code_font_orig)
    orig_w = int(draw.textlength(code_line, font=code_font_orig))
    draw_ruler(
        draw,
        50,
        458,
        orig_w,
        f"{orig_w}px (Original)",
        color_line="#e28481",
        color_text="#e28481",
        font=ruler_font,
    )

    # Typus Mono
    draw.text(
        (50, 490),
        "// Typus Mono (Regular - spaced at 95%)",
        fill="#707a8c",
        font=ruler_font,
    )
    draw.text((50, 510), code_line, fill="#e6e6e6", font=code_font_typus)
    typus_w = int(draw.textlength(code_line, font=code_font_typus))
    draw_ruler(
        draw,
        50,
        538,
        typus_w,
        f"{typus_w}px (95% Spacing)",
        color_line="#7fd962",
        color_text="#7fd962",
        font=ruler_font,
    )

    draw.line([(50, 585), (950, 585)], fill="#243347", width=1)

    # weight showcase
    draw.text(
        (50, 605),
        "/* Weights (Compensated for FreeType rendering) */",
        fill="#5c6773",
        font=section_title_font,
    )

    weights_info = [
        ("Thin", font_thin_path, "#a0a0a0"),
        ("Light", font_light_path, "#b0b0b0"),
        ("Regular", font_reg_path, "#c8c8c8"),
        ("SemiBold", font_sb_path, "#e6e6e6"),
        ("Bold", font_bold_path, "#ffffff"),
    ]

    x_offset = 50
    for w_name, w_path, w_color in weights_info:
        w_font = ImageFont.truetype(w_path, 16)
        draw.text((x_offset, 640), w_name, fill="#39bae6", font=ruler_font)
        sample_text = "The quick brown fox"
        draw.text((x_offset, 660), sample_text, fill=w_color, font=w_font)
        x_offset += 185

    img.save(output_path)
    print("Preview generated successfully!")


if __name__ == "__main__":
    main()
