# Typus Mono

**Typus Mono** is a custom-compiled, condensed, and strictly ligature-free programming font family based on **JetBrains Mono Nerd Font**. 

It was designed to bridge the gap between GPU-accelerated terminal emulators (like Ghostty) and classic desktop GUI applications (like Emacs), delivering an exact pixel-perfect match for cell spacing and visual weight.

---

## Key Features

1. **Pixel-Perfect Spacing (95% Width)**
   - The horizontal advance metrics (`hmtx`) are scaled down to **95%**, providing a 1:1 match for Ghostty's cell compression (`adjust-cell-width = -1` at `font-size = 12`).
   
2. **Spacing-Only Compression (No Outline Distortion)**
   - Unlike basic scale operations that stretch or squeeze character vectors, Typus Mono leaves glyph geometries **100% untouched**. Letters retain their original shapes, maintaining optimal readability and pixel-perfect rasterization.

3. **Academic Office Line Height (105% Height)**
   - Vertical line metrics are scaled to **105%** to supply clean vertical cell padding, matching Ghostty's `adjust-cell-height = 1` and ensuring a relaxed reading rhythm.

4. **Shifted Weight Mapping**
   - Emacs GUI (via standard FreeType rasterization) renders fonts slightly thinner than GPU-accelerated terminals. To compensate and achieve exact visual weight parity, the font mappings have been shifted up:
     - **Typus Mono `Regular`** uses source **`SemiBold`**
     - **Typus Mono `SemiBold`** uses source **`Bold`**
     - **Typus Mono `Bold`** uses source **`ExtraBold`**
     - **Typus Mono `Light`** uses source **`Regular`**
     - **Typus Mono `Thin`** uses source **`Light`**

5. **Strictly Ligature-Free**
   - GSUB substitution features (`calt`, `liga`, `dlig`, `clig`) are disabled directly inside the font tables, ensuring that programming ligatures are disabled globally across all software.

---

## Included Styles

- `TypusMono-Thin.ttf` / `TypusMono-ThinItalic.ttf`
- `TypusMono-Light.ttf` / `TypusMono-LightItalic.ttf`
- `TypusMono-Regular.ttf` / `TypusMono-Italic.ttf`
- `TypusMono-SemiBold.ttf` / `TypusMono-SemiBoldItalic.ttf`
- `TypusMono-Bold.ttf` / `TypusMono-BoldItalic.ttf`

---

## Building from Source

To compile Typus Mono yourself (requires Python and `fonttools` installed):

```bash
# Clone the repository
git clone https://github.com/szymonwilczek/typus-fonts.git
cd typus-fonts

# Build the fonts (searches for source JetBrainsMono Nerd Font files in standard locations)
./build.sh
```

You can pass a custom source font directory path as an argument if yours is in a non-standard location:
```bash
./build.sh /path/to/source/jetbrains-mono-nerd-font/directory
```

---

## Installation

Copy the compiled files inside the `fonts/` directory to your local font path:

```bash
mkdir -p ~/.local/share/fonts/TypusMono
cp fonts/*.ttf ~/.local/share/fonts/TypusMono/
fc-cache -fv
```

---

## License

This Font Software is licensed under the **SIL Open Font License, Version 1.1** (OFL). See the [LICENSE](LICENSE) file for the full text.

**Attribution**: 
- Based on [JetBrains Mono](https://www.jetbrains.com/lp/mono/) (Copyright (c) 2020, JetBrains).
- Nerd Font glyphs integrated from [Nerd Fonts](https://github.com/ryanoasis/nerd-fonts).
