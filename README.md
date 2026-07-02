# SVG Icon Generator Skills

**Turn any screenshot into pixel-perfect SVG icons — no design tools required.**

Your agent crops icons from a reference image using an interactive browser tool, then traces them into clean, scalable SVG paths using an automated image processing pipeline. No Figma. No Illustrator. No manual path editing. Just point at a screenshot and get production-ready SVGs.

**Mathematically smooth vectors. Browser-based precision cropping. Fully automated tracing.**

Works with Claude Code, OpenCode, OpenClaw, Cursor, and any agent that supports the [Agent Skills spec](https://agentskills.io).

## How It Works

```
Without this skill                        With this skill
──────────────────                        ───────────────
Agent needs an SVG icon                   Agent runs the skill
  → Asks user to export from Figma          → Generates a browser crop tool
  → Or uses a bad AI-generated SVG          → User crops precisely in browser
  → Or hardcodes a placeholder              → Script traces to clean SVG
  → Artifacts look amateur                  → Production-ready vector paths
```

Your agent doesn't just *request* icons — it **extracts** them. Provide a reference screenshot, and the skill generates an interactive HTML cropping tool, processes the crops through a multi-stage image pipeline (grayscale → threshold → 5x upscale → Gaussian blur → re-threshold → potrace), and outputs optimized SVG path data ready to embed in your components.

## Available Skills

| Skill | Description |
|-------|-------------|
| [svg-icon-generator](skills/svg-icon-generator/) | Extract SVG icons from raster screenshots via browser-based cropping and automated vector tracing. |

## Prerequisites

### Install potrace

```bash
# macOS
brew install potrace

# Ubuntu/Debian
sudo apt-get install potrace

# Fedora
sudo dnf install potrace
```

### Install Python dependencies

```bash
pip install Pillow
```

## Installation

### Option 1: CLI Install (Recommended)

Use [npx skills](https://github.com/vercel-labs/skills) to install skills directly:

```bash
# Install all skills
npx skills add arterialist/svg-icon-skills

# Install a specific skill
npx skills add arterialist/svg-icon-skills --skill svg-icon-generator

# List available skills
npx skills add arterialist/svg-icon-skills --list

# Install globally
npx skills add arterialist/svg-icon-skills -g
```

### Option 2: Claude Code Plugin

```bash
/plugin marketplace add arterialist/svg-icon-skills
/plugin install svg-icon-skills
```

### Option 3: Manual Copy

```bash
git clone git@github.com:arterialist/svg-icon-skills.git
cp -r svg-icon-skills/skills/* ~/.claude/skills/
```

## Usage

### svg-icon-generator

Ask your agent to extract icons from a screenshot:

```
"Extract the icons from this app screenshot as SVGs"
"I need SVG versions of these UI icons — here's a screenshot"
"Generate React SVG icon components from this design mockup"
```

The agent walks through the pipeline: generate a browser-based cropper → you crop each icon precisely → the script processes and traces each crop into a clean SVG path. The output is production-ready SVG path data you can drop directly into React components, HTML, or any vector format.

## License

MIT
