"""
Example: Complete Pipeline Walkthrough

This script demonstrates how to use each component of 4D-SynthForge step by step.
"""

import json
from pathlib import Path

print("=" * 70)
print("4D-SYNTHFORGE - EXAMPLE WALKTHROUGH")
print("=" * 70)
print()

# ============================================================================
# STEP 1: Video Analysis with Gemini
# ============================================================================
print("STEP 1: Analyzing video with Gemini AI")
print("-" * 70)

video_path = "examples/ball_cup.mp4"

# Check if video exists
if not Path(video_path).exists():
    print(f"❌ Video not found: {video_path}")
    print("   Run: python demo_video_creator.py")
    exit(1)

# Import and run analyzer
try:
    from video_analyzer import VideoAnalyzer
    
    print(f"📹 Input video: {video_path}")
    print("⏳ This will take ~30 seconds...")
    print()
    
    # Note: This requires GEMINI_API_KEY environment variable
    analyzer = VideoAnalyzer()
    analysis_data = analyzer.analyze_video(video_path, save_json=True)
    
    analysis_json = Path("output") / f"{Path(video_path).stem}_analysis.json"
    print(f"✅ Analysis complete: {analysis_json}")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("   Make sure dependencies are installed: pip install -r requirements.txt")
    exit(1)
except Exception as e:
    print(f"❌ Analysis failed: {e}")
    print("   Make sure GEMINI_API_KEY is set in environment variables")
    print("   Example: $env:GEMINI_API_KEY = 'your-key'")
    exit(1)

print()

# ============================================================================
# STEP 2: Generate Isaac Sim Code
# ============================================================================
print("STEP 2: Generating Isaac Sim Python script")
print("-" * 70)

from code_generator import IsaacCodeGenerator

generator = IsaacCodeGenerator()

base_script = Path("output/usd_scenes/base_scene.py")
generator.generate_scene(analysis_data, base_script, headless=True)

print(f"✅ Base script generated: {base_script}")
print()

# ============================================================================
# STEP 3: Create Randomized Variations
# ============================================================================
print("STEP 3: Creating randomized variations")
print("-" * 70)

from domain_randomizer import DomainRandomizer

num_variations = 9
randomizer = DomainRandomizer(analysis_data)
variations = randomizer.generate_variations(num_variations)

# Save variations
var_dir = Path("output/variations")
var_dir.mkdir(parents=True, exist_ok=True)

for i, var in enumerate(variations):
    var_path = var_dir / f"variation_{i:03d}.json"
    with open(var_path, 'w') as f:
        json.dump(var, f, indent=2)

print(f"✅ {len(variations)} variations created in: {var_dir}")
print()

# Show summary of first 3 variations
print("Sample variations:")
for i, var in enumerate(variations[:3]):
    summary = randomizer.get_variation_summary(var)
    print(f"  {summary}")

print()

# ============================================================================
# STEP 4: Generate Scripts for All Variations
# ============================================================================
print("STEP 4: Generating scripts for all variations")
print("-" * 70)

from tqdm import tqdm

variation_scripts = []

for i, variation in enumerate(tqdm(variations, desc="Generating")):
    script_path = Path("output/usd_scenes") / f"variation_{i:03d}.py"
    generator.generate_scene(variation, script_path, headless=True)
    variation_scripts.append(script_path)

print(f"✅ {len(variation_scripts)} scripts generated")
print()

# ============================================================================
# STEP 5: Summary
# ============================================================================
print("=" * 70)
print("✅ PIPELINE COMPLETE!")
print("=" * 70)
print()
print(f"📁 Output Directory: output/")
print()
print("Generated files:")
print(f"  • Analysis JSON: {analysis_json}")
print(f"  • Base script: {base_script}")
print(f"  • Variations: {num_variations} files in {var_dir}")
print(f"  • Isaac Sim scripts: {len(variation_scripts)} files")
print()
print("Next steps:")
print("  1. Review the generated scripts")
print("  2. If you have Isaac Sim installed, run:")
print(f"     ~/.local/share/ov/pkg/isaac_sim-*/python.sh {variation_scripts[0]}")
print()
print("  3. Or batch render all variations:")
print(f"     python main.py {video_path} --count {num_variations} --render")
print()
print("=" * 70)
