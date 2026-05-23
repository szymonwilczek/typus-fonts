# Typus Mono

**Typus Mono** is a custom-compiled, condensed, and strictly ligature-free programming font family derived from **JetBrains Mono Nerd Font**. 

It serves as my personal daily driver. I maintain this repository as a central, easily accessible storage for my setups, though others who share my exact aesthetic preferences and layout constraints may find it useful.

![Typus Mono Specimen and Spacing Comparison](preview.png)

---

## The Motivation

My journey with terminal aesthetics reached its peak with a highly tuned configuration in the Ghostty terminal emulator. By utilizing cell compression (`adjust-cell-width = -1` and `adjust-cell-height = 1` at a size of `12pt`), I achieved a compact, high-information-density monospace grid that felt incredibly crisp to my eyes.

However, when transitioning to GUI-native applications - specifically **GNU Emacs** - I faced a major obstacle. While terminal emulators can dynamically pack cells tighter by shifting rendering coordinates, Emacs GUI relies on the font's native metrics. It has no built-in mechanism for sub-pixel character width compression.

To dissolve this mismatch and bring the exact, beloved Ghostty text layout into Emacs GUI, the modifications had to be baked directly into the font files. Thus, **Typus Mono** was born.

---

## The Engineering Details

To achieve a pixel-perfect layout duplicate without ruining legibility, the customization relies on two key modifications:

### 1. Spacing-Only Metrics Compression (95% Width)
A naive approach would simply scale the font coordinates horizontally. However, horizontal scaling distorts the glyph vectors, turning round shapes into ugly ovals and breaking subpixel hints. 

Typus Mono preserves the glyph outlines **100% untouched**. Instead, it scales only the horizontal advance metrics (`hmtx` table) down to **95%**. The characters keep their original, beautifully designed proportions but are packed closer together—exactly mirroring Ghostty's cell width adjustment.

### 2. Shifted Weight Mapping (Compensating for FreeType)
When comparing GUI Emacs with Ghostty, my eyes immediately noticed a weight discrepancy. GPU-accelerated terminal renderers (such as Ghostty's custom shaders) naturally draw text with slightly more visual weight ("density"). Emacs GUI, using standard FreeType rasterization on Linux, renders the exact same font files noticeably thinner.

To correct this and restore visual parity, the font files were shifted up by weight classes:
- **Typus Mono `Regular`** is built from original **`SemiBold`**.
- **Typus Mono `SemiBold`** is built from original **`Bold`**.
- **Typus Mono `Bold`** is built from original **`ExtraBold`**.
- **Typus Mono `Light`** is built from original **`Regular`**.
- **Typus Mono `Thin`** is built from original **`Light`**.

This weight compensation, combined with the metrics scaling, yields a **1:1 pixel-perfect match** between Ghostty and Emacs GUI (measuring exactly **574 pixels for 64 characters** at size 12).

### 3. Strict Ligature Stripping
Contextual alternates (`calt`), standard ligatures (`liga`), discretionary ligatures (`dlig`), and contextual ligatures (`clig`) are disabled directly inside the OpenType `GSUB` table. This guarantees a clean, distraction-free environment without programming ligatures across all applications.

---

## Included Styles

- `TypusMono-Thin.ttf` / `TypusMono-ThinItalic.ttf`
- `TypusMono-Light.ttf` / `TypusMono-LightItalic.ttf`
- `TypusMono-Regular.ttf` / `TypusMono-Italic.ttf`
- `TypusMono-SemiBold.ttf` / `TypusMono-SemiBoldItalic.ttf`
- `TypusMono-Bold.ttf` / `TypusMono-BoldItalic.ttf`

---

## Building from Source

The repository contains the exact tools used to build this font family. If you have Python and `fonttools` installed, you can re-run the build:

```bash
# Searches standard paths for source JetBrainsMono Nerd Font files and builds the family
./build.sh
```

You can pass a custom source directory path if needed:
```bash
./build.sh /path/to/source/jetbrains-mono-nerd-font/directory
```

---

## Installation

```bash
mkdir -p ~/.local/share/fonts/TypusMono
cp fonts/*.ttf ~/.local/share/fonts/TypusMono/
fc-cache -fv
```

To load it in Emacs GUI:
```elisp
(set-frame-font "Typus Mono-12:weight=normal" nil t)
```

---

## License & Credits

Typus Mono is licensed under the **SIL Open Font License, Version 1.1** (OFL). 

- Derived from [JetBrains Mono](https://www.jetbrains.com/lp/mono/) (Copyright (c) 2020, JetBrains).
- Nerd Font glyphs integrated from [Nerd Fonts](https://github.com/ryanoasis/nerd-fonts).
