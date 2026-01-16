"""
4D-SynthForge Configuration Module

Central configuration for Gemini API, Isaac Sim paths, and simulation parameters.
"""

import os
from pathlib import Path
from typing import Dict, Any

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# ============================================================================
# PROJECT PATHS
# ============================================================================

PROJECT_ROOT = Path(__file__).parent
OUTPUT_DIR = PROJECT_ROOT / "output"
EXAMPLES_DIR = PROJECT_ROOT / "examples"
RENDERS_DIR = OUTPUT_DIR / "renders"
USD_SCENES_DIR = OUTPUT_DIR / "usd_scenes"

# Create directories
for directory in [OUTPUT_DIR, EXAMPLES_DIR, RENDERS_DIR, USD_SCENES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ============================================================================
# GEMINI API CONFIGURATION
# ============================================================================

# Get API key from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

if not GEMINI_API_KEY:
    print("⚠️  WARNING: GEMINI_API_KEY not found in environment variables!")
    print("   Set it with: export GEMINI_API_KEY='your-api-key'")

# Gemini model configuration
GEMINI_MODEL = "gemini-2.0-flash-exp"  # Supports video analysis
GEMINI_TEMPERATURE = 0.1  # Low temperature for consistent structured output
GEMINI_MAX_TOKENS = 4096

# ============================================================================
# ISAAC SIM CONFIGURATION
# ============================================================================

# Isaac Sim installation path (auto-detect or set manually)
ISAAC_SIM_PATH = Path.home() / ".local/share/ov/pkg"
ISAAC_SIM_PYTHON = None

# Try to find Isaac Sim Python executable
if ISAAC_SIM_PATH.exists():
    isaac_versions = sorted(ISAAC_SIM_PATH.glob("isaac_sim-*"))
    if isaac_versions:
        latest_isaac = isaac_versions[-1]
        ISAAC_SIM_PYTHON = latest_isaac / "python.sh"
        print(f"✓ Found Isaac Sim: {latest_isaac}")
    else:
        print("⚠️  Isaac Sim not found in default location")
else:
    print("⚠️  Isaac Sim path does not exist. Please install Isaac Sim.")

# Isaac Sim headless rendering settings
ISAAC_HEADLESS = True
ISAAC_WIDTH = 1920
ISAAC_HEIGHT = 1080
ISAAC_FPS = 60
ISAAC_SIMULATION_DURATION = 5.0  # seconds

# ============================================================================
# PHYSICS ANALYSIS SYSTEM PROMPT
# ============================================================================

PHYSICS_ANALYSIS_PROMPT = """
You are a Physics Simulation Engineer specializing in 4D analysis and Nvidia PhysX simulation.

Analyze this video frame-by-frame and extract ONLY numerical/categorical data in strict JSON format optimized for Nvidia Omniverse Isaac Sim.

Required output structure:
{
  "scene_composition": {
    "objects": [
      {
        "id": "unique_object_id",
        "type": "sphere/cylinder/cube/mesh",
        "position": {"x": 0.0, "y": 0.0, "z": 0.0},
        "rotation": {"x": 0.0, "y": 0.0, "z": 0.0},
        "scale": {"x": 1.0, "y": 1.0, "z": 1.0}
      }
    ],
    "environment": {
      "surface_type": "table/floor/ground",
      "material": "wood/plastic/metal",
      "dimensions": {"length": 2.0, "width": 2.0, "height": 0.1}
    }
  },
  "physics_estimation": {
    "gravity": {"x": 0.0, "y": -9.81, "z": 0.0},
    "objects": [
      {
        "id": "object_1",
        "mass": 1.0,
        "initial_velocity": {"x": 2.0, "y": 0.0, "z": 0.0},
        "initial_angular_velocity": {"x": 0.0, "y": 0.0, "z": 0.0},
        "restitution": 0.5,
        "static_friction": 0.3,
        "dynamic_friction": 0.25,
        "collision_shape": "convex_hull/sphere/box"
      }
    ]
  },
  "lighting_conditions": {
    "dome_light": {"intensity": 1000.0, "texture": "sky/studio"},
    "key_light": {
      "type": "distant/sphere",
      "position": {"x": 5.0, "y": 5.0, "z": 5.0},
      "intensity": 5000.0,
      "color": {"r": 1.0, "g": 1.0, "b": 1.0}
    }
  },
  "event_timeline": [
    {"frame": 0, "event": "simulation_start", "object_id": "ball"},
    {"frame": 45, "event": "collision", "objects": ["ball", "cup"]},
    {"frame": 60, "event": "object_rest", "object_id": "cup"}
  ],
  "camera_estimation": {
    "position": {"x": 0.0, "y": 1.5, "z": 3.0},
    "look_at": {"x": 0.0, "y": 0.5, "z": 0.0},
    "focal_length": 50.0
  }
}

CRITICAL RULES:
1. NO prose or descriptions - ONLY structured JSON
2. Use numerical values, not categories (e.g., mass: 1.0, not "heavy")
3. All positions in meters, all angles in degrees
4. Estimate realistic PhysX parameters
5. Identify collision events with frame numbers
"""

# ============================================================================
# DOMAIN RANDOMIZATION CONFIGURATION
# ============================================================================

RANDOMIZATION_CONFIG: Dict[str, Any] = {
    "material": {
        "base_color_hue": (0.0, 1.0),
        "base_color_saturation": (0.5, 1.0),
        "base_color_value": (0.4, 1.0),
        "roughness": (0.1, 0.9),
        "metallic": (0.0, 0.8)
    },
    "lighting": {
        "dome_rotation": (0, 360),  # degrees
        "dome_intensity": (500, 3000),
        "key_light_intensity": (3000, 10000),
        "key_light_position": {
            "x": (-10, 10),
            "y": (3, 10),
            "z": (-10, 10)
        },
        "color_temperature": (2700, 6500)  # Kelvin
    },
    "physics": {
        "static_friction": (0.1, 0.8),
        "dynamic_friction": (0.05, 0.7),
        "restitution": (0.2, 0.95),
        "mass_multiplier": (0.5, 2.0),
        "initial_velocity_scale": (0.8, 1.2)
    },
    "camera": {
        "position_offset_x": (-2, 2),
        "position_offset_y": (-1, 1),
        "position_offset_z": (-2, 2),
        "focal_length": (24, 85)  # mm
    }
}

# ============================================================================
# DEFAULT SCENE PARAMETERS
# ============================================================================

DEFAULT_SCENE_PARAMS = {
    "ground": {
        "size": 10.0,
        "position": {"x": 0.0, "y": 0.0, "z": 0.0},
        "material": {
            "static_friction": 0.5,
            "dynamic_friction": 0.4,
            "restitution": 0.3
        }
    },
    "camera": {
        "position": {"x": 0.0, "y": 1.5, "z": 3.0},
        "look_at": {"x": 0.0, "y": 0.5, "z": 0.0},
        "focal_length": 50.0
    },
    "lighting": {
        "dome_intensity": 1000.0,
        "key_light_intensity": 5000.0,
        "key_light_position": {"x": 5.0, "y": 5.0, "z": 5.0}
    }
}

# ============================================================================
# RENDERING CONFIGURATION
# ============================================================================

RENDER_CONFIG = {
    "resolution": {
        "width": ISAAC_WIDTH,
        "height": ISAAC_HEIGHT
    },
    "frame_rate": ISAAC_FPS,
    "output_format": "mp4",
    "samples_per_pixel": 32,  # Ray tracing quality
    "enable_rtx": True,
    "max_bounces": 4
}

# ============================================================================
# VALIDATION SCHEMA
# ============================================================================

# JSON schema for validating Gemini output
PHYSICS_JSON_SCHEMA = {
    "type": "object",
    "required": ["scene_composition", "physics_estimation"],
    "properties": {
        "scene_composition": {
            "type": "object",
            "required": ["objects"],
            "properties": {
                "objects": {
                    "type": "array",
                    "minItems": 1
                }
            }
        },
        "physics_estimation": {
            "type": "object",
            "required": ["gravity", "objects"],
            "properties": {
                "gravity": {"type": "object"},
                "objects": {"type": "array", "minItems": 1}
            }
        }
    }
}

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = OUTPUT_DIR / "4d_synthforge.log"
