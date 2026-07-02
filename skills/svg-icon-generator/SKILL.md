---
name: svg-icon-generator
description: |
  Extract production-ready SVG icons from raster images (screenshots, UI mockups, design comps) using browser-based precision cropping and automated vector tracing. Use this skill when the user wants to convert screenshot icons to SVG, trace raster icons to vector paths, extract UI elements as scalable graphics, or generate React/HTML-ready SVG components from images.
---

# Extract SVG Icons from Raster Images

This skill converts raster icons (from screenshots, mockups, or design files) into clean, mathematically smooth SVG vector paths. It solves the common problem where naive `potrace` tracing produces jagged or artifact-filled results on real-world UI images.

The pipeline works in two phases:
1. **Interactive cropping** — generates a browser-based tool for pixel-precise icon selection
2. **Automated tracing** — processes crops through a multi-stage image pipeline before vectorizing

---

## Prerequisites

Before running this skill, verify the following are installed:

```bash
# Check potrace (required for vector tracing)
which potrace || echo "MISSING: Install with 'brew install potrace' (macOS) or 'apt-get install potrace' (Linux)"

# Check Python Pillow (required for image processing)
python3 -c "from PIL import Image; print('Pillow OK')" || echo "MISSING: Install with 'pip install Pillow'"
```

If either is missing, install them before proceeding. Do not skip this step.

---

## Step-by-Step Workflow

In all commands below, `$SKILL_DIR` refers to the directory containing this `SKILL.md` file.

### Step 1: Generate the Cropper UI

Run `generate-cropper` with the source image and a list of icon names to extract:

```bash
python3 "$SKILL_DIR/scripts/svg-tools.py" generate-cropper /path/to/image.png icon_name_1 icon_name_2
```

**What this does:**
- Generates a self-contained `crop.html` file in the current directory
- The HTML includes the source image embedded as base64 and uses Cropper.js (loaded via CDN)

**What to tell the user:**
1. Open `crop.html` in a browser
2. For each icon tab, drag the crop box to tightly frame the icon
3. Click the download button for each — files save as `<icon_name>_precise.png`
4. Confirm when all crops are downloaded

**Do not proceed to Step 2 until the user confirms all crops are saved.**

### Step 2: Trace Crops to SVG

Once the user has all `_precise.png` files, run `trace`:

```bash
python3 "$SKILL_DIR/scripts/svg-tools.py" trace ~/Downloads/icon_name_1_precise.png ~/Downloads/icon_name_2_precise.png
```

**What this does:**
- Converts each crop to grayscale
- Applies initial threshold at 150 (separates dark UI elements from light backgrounds)
- Upscales 5× with bicubic interpolation (provides sub-pixel precision for smoothing)
- Applies Gaussian blur at radius 5 (smooths jagged pixel edges)
- Re-thresholds at 128 (re-hardens edges into clean black/white)
- Runs `potrace` to produce optimized SVG output

**Output:** `<icon_name>.svg` files in the same directory as the inputs.

### Step 3: Integrate the SVG Paths

Read each generated `.svg` file, extract the `<path d="...">` data, and inject it into the target codebase (React components, HTML templates, etc.).

---

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| SVG has jagged edges | Crop was too loose, included background noise | Re-crop more tightly around the icon |
| SVG is blank or all-black | Icon was too light or too colorful for the threshold | The image needs a dark-on-light icon; adjust source |
| `potrace: command not found` | potrace not installed | `brew install potrace` or `apt-get install potrace` |
| `ModuleNotFoundError: PIL` | Pillow not installed | `pip install Pillow` |
