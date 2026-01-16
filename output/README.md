# Output Directory

This directory contains all generated files from the 4D-SynthForge pipeline.

## Directory Structure

```
output/
├── *_analysis.json              # Gemini analysis results
├── variations/                  # Randomized scene parameters
│   ├── variation_000.json
│   ├── variation_001.json
│   └── ...
├── usd_scenes/                  # Isaac Sim Python scripts
│   ├── base_scene.py
│   ├── variation_000.py
│   └── ...
└── renders/                     # Final rendered videos (if --render used)
    ├── variation_000.mp4
    └── ...
```

## File Descriptions

### Analysis JSON
**Example**: `ball_cup_analysis.json`

Contains Gemini's physics analysis:
- Scene composition (objects, positions, scales)
- Physics parameters (mass, velocity, friction, restitution)
- Lighting conditions (dome light, key lights)
- Event timeline (collisions, key frames)
- Camera estimation

### Variations
**Example**: `variations/variation_001.json`

Randomized version of the base analysis:
- Modified material colors (HSV randomization)
- Varied lighting (intensity, position, color temperature)
- Altered physics (friction, restitution, mass)
- Camera angle variations

### USD Scenes
**Example**: `usd_scenes/variation_001.py`

Executable Isaac Sim scripts:
- USD stage creation
- PhysX scene setup
- Object geometry and physics
- Lighting and camera configuration
- Simulation loop

**Run with:**
```bash
# Linux/Mac
~/.local/share/ov/pkg/isaac_sim-*/python.sh usd_scenes/variation_001.py

# Windows
%USERPROFILE%\.local\share\ov\pkg\isaac_sim-*\python.bat usd_scenes\variation_001.py
```

### Renders
**Example**: `renders/variation_001.mp4`

Final rendered videos (requires Isaac Sim):
- 1920x1080 resolution
- 60 FPS
- 5 seconds duration
- RTX ray-traced rendering

## Cleaning Up

To reset and start fresh:

```bash
# PowerShell (Windows)
Remove-Item -Recurse -Force output/*

# Bash (Linux/Mac)
rm -rf output/*
```

## File Sizes

Typical file sizes for 100 variations:

| File Type | Size per File | Total (100x) |
|-----------|---------------|--------------|
| Analysis JSON | ~5 KB | ~500 KB |
| Variation JSON | ~8 KB | ~800 KB |
| USD Script | ~15 KB | ~1.5 MB |
| Rendered Video | ~2-5 MB | ~200-500 MB |

**Total**: ~200-500 MB for complete dataset

## Git Ignore

The `.gitignore` file excludes:
- All `output/` contents (except this README)
- Large video files
- Temporary USD files

This keeps your repository clean while preserving generated data locally.
