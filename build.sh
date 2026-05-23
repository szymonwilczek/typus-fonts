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

echo "---- Generating Typus Mono (Width scale: 0.95, Height scale: 1.05) ----"

for style_name in "Thin" "ThinItalic" "Light" "LightItalic" "Regular" "Italic" "SemiBold" "SemiBoldItalic" "Bold" "BoldItalic"; do
  input_file="${styles[$style_name]}"
  output_file="TypusMono-${style_name}.ttf"

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

  echo "Processing: $style_name (Subfamily: $style_param)"
  python3 "$GEN_SCRIPT" \
    --input "$FONT_DIR/$input_file" \
    --output "$OUTPUT_DIR/$output_file" \
    --name "Typus Mono" \
    --style "$style_param" \
    --width-scale 0.95 \
    --height-scale 1.05 \
    --no-scale-outlines
done

echo "---- Build complete! Fonts saved to $OUTPUT_DIR ----"
