# 🚀 Getting Started with 4D-SynthForge

## Prerequisites

- ✅ Python 3.10 or higher
- ✅ pip (Python package manager)
- ✅ Gemini API key from https://aistudio.google.com
- ⚠️ Nvidia Isaac Sim (optional, for rendering)

## Installation (5 minutes)

### Step 1: Install Dependencies

Open PowerShell in the project directory and run:

```powershell
pip install -r requirements.txt
```

This installs:
- `google-generativeai` - Gemini API client
- `opencv-python` - Video processing
- `pillow` - Image handling
- `numpy` - Numerical operations
- `pydantic` - Data validation
- `tqdm` - Progress bars

### Step 2: Configure Gemini API Key

Get your API key from https://aistudio.google.com/app/apikey

Then set it as an environment variable:

```powershell
# For current session
$env:GEMINI_API_KEY = "AIzaSy..."

# To make it permanent (optional)
[System.Environment]::SetEnvironmentVariable('GEMINI_API_KEY', 'AIzaSy...', 'User')
```

### Step 3: Create Demo Video

```powershell
python demo_video_creator.py
```

This creates `examples/ball_cup.mp4` (5 seconds, 1.5 MB)

## First Run (2 minutes)

### Option A: Full Pipeline (Recommended)

```powershell
python main.py examples/ball_cup.mp4 --count 9
```

**What happens:**
1. ⏳ Uploads video to Gemini (~10s)
2. 🤖 Analyzes physics (~20s)
3. 💾 Saves analysis JSON
4. 🔧 Generates base Isaac Sim script
5. 🎲 Creates 9 randomized variations
6. 📝 Generates 9 Python scripts

**Output:**
```
output/
├── ball_cup_analysis.json          # Gemini's physics analysis
├── variations/
│   ├── variation_000.json          # Blue ball, bright light
│   ├── variation_001.json          # Red ball, normal light
│   └── ...
└── usd_scenes/
    ├── base_scene.py               # Original scene
    ├── variation_000.py            # Variation scripts
    └── ...
```

### Option B: Step-by-Step

```powershell
# Step 1: Analyze video
python video_analyzer.py examples/ball_cup.mp4

# Step 2: Generate code
python code_generator.py output/ball_cup_analysis.json

# Step 3: Create variations
python domain_randomizer.py output/ball_cup_analysis.json 100
```

## Understanding the Output

### Analysis JSON
Open `output/ball_cup_analysis.json` to see what Gemini extracted:

```json
{
  "scene_composition": {
    "objects": [
      {"id": "ball", "type": "sphere", "position": {"x": 0, "y": 2, "z": 0}}
    ]
  },
  "physics_estimation": {
    "objects": [
      {
        "id": "ball",
        "mass": 0.5,
        "initial_velocity": {"x": 2.0, "y": 0.0, "z": 0.0},
        "restitution": 0.7
      }
    ]
  }
}
```

### Generated Scripts
Open `output/usd_scenes/base_scene.py` to see the Isaac Sim code:

```python
# Create sphere (ball)
ball = UsdGeom.Sphere.Define(stage, "/World/Ball")
ball.CreateRadiusAttr(0.5)

# Add physics
rigid_body = UsdPhysics.RigidBodyAPI.Apply(...)
rigid_body.CreateVelocityAttr(Gf.Vec3f(2.0, 0.0, 0.0))
```

## Running with Isaac Sim (Optional)

If you have Isaac Sim installed:

### Find Isaac Sim Python

```powershell
# Windows
$isaacPath = "$env:USERPROFILE\.local\share\ov\pkg"
Get-ChildItem $isaacPath -Filter "isaac_sim-*"

# Linux/Mac
ls ~/.local/share/ov/pkg/isaac_sim-*
```

### Run a Script

```bash
# Linux/Mac
~/.local/share/ov/pkg/isaac_sim-2023.1.1/python.sh output/usd_scenes/base_scene.py

# Windows
%USERPROFILE%\.local\share\ov\pkg\isaac_sim-2023.1.1\python.bat output\usd_scenes\base_scene.py
```

### Batch Render All Variations

```powershell
python main.py examples/ball_cup.mp4 --count 9 --render
```

This will:
1. Generate 9 variations
2. Launch Isaac Sim for each (headless)
3. Render videos to `output/renders/`

**Time**: ~5-10 minutes for 9 variations (depends on GPU)

## Using Your Own Videos

### Record a Video

Best practices:
- 📹 **Duration**: 3-10 seconds
- 📐 **Resolution**: 720p or higher
- 🎥 **Content**: Simple physics (ball rolling, object falling)
- 💡 **Lighting**: Bright, even lighting
- 🎬 **Camera**: Stable (use tripod)

### Run Pipeline

```powershell
python main.py your_video.mp4 --count 100
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'google'"

```powershell
pip install google-generativeai
```

### "GEMINI_API_KEY not found"

```powershell
# Check if set
echo $env:GEMINI_API_KEY

# Set it
$env:GEMINI_API_KEY = "your-key-here"
```

### "Video processing failed"

Make sure OpenCV is installed:

```powershell
pip install opencv-python
```

### "Isaac Sim not found"

Isaac Sim is optional. You can:
- Use the system without rendering (just generates scripts)
- Download Isaac Sim from https://developer.nvidia.com/isaac-sim
- Or skip the `--render` flag

## Quick Reference

### All Commands

```powershell
# Setup
.\setup.ps1                                          # Automated setup

# Demo video
python demo_video_creator.py                         # Create demo

# Analysis only
python video_analyzer.py examples/ball_cup.mp4       # Analyze video

# Code generation
python code_generator.py output/analysis.json        # Generate script

# Variations
python domain_randomizer.py output/analysis.json 100 # Create 100 variations

# Full pipeline
python main.py examples/ball_cup.mp4 --count 9       # Without rendering
python main.py examples/ball_cup.mp4 --count 9 --render  # With rendering
```

### File Locations

| What | Where |
|------|-------|
| Demo video | `examples/ball_cup.mp4` |
| Analysis | `output/*_analysis.json` |
| Variations | `output/variations/` |
| Scripts | `output/usd_scenes/` |
| Renders | `output/renders/` |

## Next Steps

1. **Read the docs**: Check `README.md` for full documentation
2. **Try variations**: Experiment with different `--count` values
3. **Custom videos**: Record your own physics videos
4. **Adjust randomization**: Edit `config.py` to customize parameters
5. **Hackathon prep**: Review `PRESENTATION_SCRIPT.md`

## Getting Help

- 📖 **README.md** - Complete documentation
- 🎓 **walkthrough.md** - Technical deep-dive
- 💬 **QUICKSTART_ES.md** - Spanish quick start
- 🎤 **PRESENTATION_SCRIPT.md** - Hackathon pitch

## Success!

You're all set! Run this to verify everything works:

```powershell
python main.py examples/ball_cup.mp4 --count 9
```

If you see output files generated in `output/`, you're ready to go! 🎉

---

**Questions?** Check the documentation or review the code - it's all well-commented!
