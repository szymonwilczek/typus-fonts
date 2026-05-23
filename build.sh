#!/bin/bash
set -e

FONT_DIR="${1:-~/.local/share/fonts/JetBrainsMono}"
OUTPUT_DIR="fonts"
GEN_SCRIPT="generate.py"

if [ ! -d "$FONT_DIR" ]; then
  echo "Error: Source font directory not found: $FONT_DIR"
  echo "Usage: ./build.sh [path/to/JetBrainsMono/source/dir]"
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

declare -A styles
styles=(
  ["Thin"]="JetBrainsMonoNerdFont-Light.ttf"
  ["ThinItalic"]="JetBrainsMonoNerdFont-LightItalic.ttf"
  ["Light"]="JetBrainsMonoNerdFont-Regular.ttf"
  ["LightItalic"]="JetBrainsMonoNerdFont-Italic.ttf"
  ["Regular"]="JetBrainsMonoNerdFont-SemiBold.ttf"
  ["Italic"]="JetBrainsMonoNerdFont-SemiBoldItalic.ttf"
  ["SemiBold"]="JetBrainsMonoNerdFont-Bold.ttf"
  ["SemiBoldItalic"]="JetBrainsMonoNerdFont-BoldItalic.ttf"
  ["Bold"]="JetBrainsMonoNerdFont-ExtraBold.ttf"
  ["BoldItalic"]="JetBrainsMonoNerdFont-ExtraBoldItalic.ttf"
)

# Compile 90%, 92%, and 95% families
for scale in 90 92 95; do
  if [ "$scale" = "90" ]; then width_scale="0.90"; fi
  if [ "$scale" = "92" ]; then width_scale="0.92"; fi
  if [ "$scale" = "95" ]; then width_scale="0.95"; fi

  echo "=== Generating Typus Mono $scale (Width scale: $width_scale, Height scale: 1.05) ==="

  for style_name in "Thin" "ThinItalic" "Light" "LightItalic" "Regular" "Italic" "SemiBold" "SemiBoldItalic" "Bold" "BoldItalic"; do
    input_file="${styles[$style_name]}"
    output_file="TypusMono${scale}-${style_name}.ttf"

    if [ "$style_name" = "Regular" ]; then style_param="Regular"; fi
    if [ "$style_name" = "Italic" ]; then style_param="Italic"; fi
    if [ "$style_name" = "SemiBold" ]; then style_param="SemiBold"; fi
    if [ "$style_name" = "SemiBoldItalic" ]; then style_param="SemiBold Italic"; fi
    if [ "$style_name" = "Bold" ]; then style_param="Bold"; fi
    if [ "$style_name" = "BoldItalic" ]; then style_param="Bold Italic"; fi
    if [ "$style_name" = "Thin" ]; then style_param="Thin"; fi
    if [ "$style_name" = "ThinItalic" ]; then style_param="Thin Italic"; fi
    if [ "$style_name" = "Light" ]; then style_param="Light"; fi
    if [ "$style_name" = "LightItalic" ]; then style_param="Light Italic"; fi

    python3 "$GEN_SCRIPT" \
      --input "$FONT_DIR/$input_file" \
      --output "$OUTPUT_DIR/$output_file" \
      --name "Typus Mono $scale" \
      --style "$style_param" \
      --width-scale "$width_scale" \
      --height-scale 1.05 \
      --no-scale-outlines
  done
done

echo "---- Build complete! Fonts saved to $OUTPUT_DIR ----"
