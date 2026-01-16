"""
Domain Randomization Module

Generates multiple variations of a scene using Omniverse Replicator for synthetic data.
"""

import logging
import random
from pathlib import Path
from typing import Dict, Any, List
import colorsys

from config import RANDOMIZATION_CONFIG, RENDERS_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DomainRandomizer:
    """
    Creates scene variations using domain randomization techniques.
    """
    
    def __init__(self, base_analysis: Dict[str, Any]):
        """
        Initialize randomizer with base scene analysis.
        
        Args:
            base_analysis: Original physics analysis from Gemini
        """
        self.base_analysis = base_analysis
        self.config = RANDOMIZATION_CONFIG
        logger.info("✓ DomainRandomizer initialized")
    
    def generate_variations(self, count: int = 100) -> List[Dict[str, Any]]:
        """
        Generate N randomized variations of the base scene.
        
        Args:
            count: Number of variations to generate
            
        Returns:
            List of modified analysis dictionaries
        """
        logger.info(f"🎲 Generating {count} scene variations...")
        
        variations = []
        
        for i in range(count):
            variation = self._create_variation(i)
            variations.append(variation)
        
        logger.info(f"✅ Generated {len(variations)} variations")
        return variations
    
    def _create_variation(self, index: int) -> Dict[str, Any]:
        """
        Create a single randomized variation.
        
        Args:
            index: Variation index
            
        Returns:
            Modified analysis dictionary
        """
        import copy
        variation = copy.deepcopy(self.base_analysis)
        
        # Add variation metadata
        variation["variation_id"] = index
        variation["randomization_seed"] = index + 1000
        
        # Randomize different aspects
        self._randomize_materials(variation)
        self._randomize_lighting(variation)
        self._randomize_physics(variation)
        self._randomize_camera(variation)
        
        return variation
    
    def _randomize_materials(self, variation: Dict[str, Any]) -> None:
        """
        Randomize material properties (colors, roughness, metallic).
        """
        objects = variation.get("scene_composition", {}).get("objects", [])
        
        for obj in objects:
            # Generate random color in HSV then convert to RGB
            hue = random.uniform(*self.config["material"]["base_color_hue"])
            saturation = random.uniform(*self.config["material"]["base_color_saturation"])
            value = random.uniform(*self.config["material"]["base_color_value"])
            
            r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
            
            # Add material properties to object
            obj["material"] = {
                "base_color": {"r": r, "g": g, "b": b},
                "roughness": random.uniform(*self.config["material"]["roughness"]),
                "metallic": random.uniform(*self.config["material"]["metallic"])
            }
    
    def _randomize_lighting(self, variation: Dict[str, Any]) -> None:
        """
        Randomize lighting conditions.
        """
        lighting = variation.setdefault("lighting_conditions", {})
        
        # Randomize dome light
        dome = lighting.setdefault("dome_light", {})
        dome["intensity"] = random.uniform(*self.config["lighting"]["dome_intensity"])
        dome["rotation"] = random.uniform(*self.config["lighting"]["dome_rotation"])
        
        # Randomize key light
        key_light = lighting.setdefault("key_light", {})
        key_light["intensity"] = random.uniform(*self.config["lighting"]["key_light_intensity"])
        
        # Randomize position
        key_light_pos = key_light.setdefault("position", {})
        key_light_pos["x"] = random.uniform(*self.config["lighting"]["key_light_position"]["x"])
        key_light_pos["y"] = random.uniform(*self.config["lighting"]["key_light_position"]["y"])
        key_light_pos["z"] = random.uniform(*self.config["lighting"]["key_light_position"]["z"])
        
        # Color temperature
        key_light["color_temperature"] = random.uniform(*self.config["lighting"]["color_temperature"])
    
    def _randomize_physics(self, variation: Dict[str, Any]) -> None:
        """
        Randomize physics parameters.
        """
        physics_objects = variation.get("physics_estimation", {}).get("objects", [])
        
        for obj in physics_objects:
            # Randomize friction
            obj["static_friction"] = random.uniform(*self.config["physics"]["static_friction"])
            obj["dynamic_friction"] = random.uniform(*self.config["physics"]["dynamic_friction"])
            
            # Randomize restitution (bounciness)
            obj["restitution"] = random.uniform(*self.config["physics"]["restitution"])
            
            # Randomize mass
            base_mass = obj.get("mass", 1.0)
            mass_mult = random.uniform(*self.config["physics"]["mass_multiplier"])
            obj["mass"] = base_mass * mass_mult
            
            # Randomize initial velocity
            velocity = obj.get("initial_velocity", {"x": 0, "y": 0, "z": 0})
            vel_scale = random.uniform(*self.config["physics"]["initial_velocity_scale"])
            obj["initial_velocity"] = {
                "x": velocity.get("x", 0) * vel_scale,
                "y": velocity.get("y", 0) * vel_scale,
                "z": velocity.get("z", 0) * vel_scale
            }
    
    def _randomize_camera(self, variation: Dict[str, Any]) -> None:
        """
        Randomize camera position and settings.
        """
        camera = variation.setdefault("camera_estimation", {})
        base_pos = camera.get("position", {"x": 0, "y": 1.5, "z": 3})
        
        # Add random offset
        camera["position"] = {
            "x": base_pos.get("x", 0) + random.uniform(*self.config["camera"]["position_offset_x"]),
            "y": base_pos.get("y", 1.5) + random.uniform(*self.config["camera"]["position_offset_y"]),
            "z": base_pos.get("z", 3) + random.uniform(*self.config["camera"]["position_offset_z"])
        }
        
        # Randomize focal length
        camera["focal_length"] = random.uniform(*self.config["camera"]["focal_length"])
    
    def get_variation_summary(self, variation: Dict[str, Any]) -> str:
        """
        Get a human-readable summary of a variation.
        
        Args:
            variation: Variation dictionary
            
        Returns:
            Summary string
        """
        var_id = variation.get("variation_id", 0)
        
        # Extract key differences
        objects = variation.get("scene_composition", {}).get("objects", [])
        colors = []
        for obj in objects:
            if "material" in obj:
                color = obj["material"]["base_color"]
                colors.append(f"RGB({color['r']:.2f},{color['g']:.2f},{color['b']:.2f})")
        
        lighting = variation.get("lighting_conditions", {})
        dome_intensity = lighting.get("dome_light", {}).get("intensity", 0)
        
        physics_obj = variation.get("physics_estimation", {}).get("objects", [{}])[0]
        friction = physics_obj.get("static_friction", 0)
        
        return f"Variation {var_id}: Colors={colors}, Light={dome_intensity:.0f}, Friction={friction:.2f}"


def create_variation_grid(variations: List[Dict[str, Any]], grid_size: int = 3) -> List[int]:
    """
    Select a subset of variations for grid display.
    
    Args:
        variations: All variations
        grid_size: Size of grid (e.g., 3 = 3x3 grid)
        
    Returns:
        List of indices to use
    """
    total_needed = grid_size * grid_size
    if len(variations) <= total_needed:
        return list(range(len(variations)))
    
    # Select evenly distributed samples
    step = len(variations) // total_needed
    return [i * step for i in range(total_needed)]


if __name__ == "__main__":
    # Test randomization
    import json
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python domain_randomizer.py <analysis_json> [count]")
        print("\nExample:")
        print("  python domain_randomizer.py output/ball_cup_analysis.json 9")
        sys.exit(1)
    
    json_path = sys.argv[1]
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 9
    
    # Load base analysis
    with open(json_path, 'r') as f:
        base_analysis = json.load(f)
    
    # Generate variations
    randomizer = DomainRandomizer(base_analysis)
    variations = randomizer.generate_variations(count)
    
    # Print summaries
    print(f"\n{'='*60}")
    print(f"GENERATED {len(variations)} VARIATIONS")
    print(f"{'='*60}\n")
    
    for var in variations[:9]:  # Show first 9
        print(randomizer.get_variation_summary(var))
    
    # Save variations
    output_dir = Path("output/variations")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for i, var in enumerate(variations):
        output_file = output_dir / f"variation_{i:03d}.json"
        with open(output_file, 'w') as f:
            json.dump(var, f, indent=2)
    
    print(f"\n✅ Variations saved to: {output_dir}")
