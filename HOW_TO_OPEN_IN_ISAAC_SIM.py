# Simple Isaac Sim Scene - Compatible with standalone execution
# Place this in your IsaacLab folder and run with Isaac Sim

# To run: From Isaac Sim Python environment
# Example: ./python.sh C:/path/to/this/script.py

print("=" * 60)
print("4D-SynthForge - Simple Scene")  
print("=" * 60)

# Instructions to manually load in Isaac Sim
INSTRUCTIONS = """
🎬 HOW TO USE THIS IN ISAAC SIM:

1. Open Isaac Sim (NOT IsaacLab)

2. Create a new scene or use the default

3. Add objects manually:
   - Add → Physics → Rigid Body → Sphere (for ball)
   - Add → Physics → Rigid Body → Cylinder (for cup)
   - Add → Create → Plane (for ground)

4. Set physics properties:
   
   BALL:
   - Mass: 0.1 kg
   - Restitution (bounce): 0.7
   - Friction: 0.3
   - Initial Velocity: X=2.0 m/s
   - Position: Y=2.0 meters

   CUP:
   - Mass: 0.15 kg
   - Restitution: 0.3
   - Friction: 0.5
   - Position: X=1.5, Y=0.5

   GROUND:
   - Static body
   - Friction: 0.5

5. Press PLAY ▶️ to see the simulation!

📊 FROM GEMINI ANALYSIS (output/ball_cup_analysis.json):
   - Scene has 2 objects (ball, cup)
   - Collision expected at frame ~45
   - Gravity: 9.81 m/s²
"""

print(INSTRUCTIONS)

# Export the analysis data for reference
import json
from pathlib import Path

analysis_path = Path("C:/Users/Marlon/Desktop/4D-SynthForge/output/ball_cup_analysis.json")

if analysis_path.exists():
    with open(analysis_path, 'r') as f:
        data = json.load(f)
    
    print("\n" + "=" * 60)
    print("SCENE DATA FROM GEMINI:")
    print("=" * 60)
    print(json.dumps(data, indent=2))
else:
    print("\n⚠️  Analysis file not found")
    print(f"   Expected: {analysis_path}")
