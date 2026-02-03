"""
Code Generator Module

Translates Gemini's physics analysis JSON into executable Isaac Sim Python scripts
using USD and PhysX APIs.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from config import USD_SCENES_DIR, DEFAULT_SCENE_PARAMS, LLM_PROVIDER
from llm_provider import get_provider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IsaacCodeGenerator:
    """
    Generates Isaac Sim Python scripts from physics analysis data.
    """
    
    def __init__(self):
        """Initialize the code generator."""
        self.provider = get_provider(LLM_PROVIDER)
        self.script_template = self._load_template()
        logger.info(f"✓ IsaacCodeGenerator initialized with provider: {LLM_PROVIDER}")
    
    def generate_scene(
        self,
        analysis_data: Dict[str, Any],
        output_path: str | Path,
        headless: bool = True
    ) -> Path:
        """
        Generate a complete Isaac Sim script from analysis data.
        
        Args:
            analysis_data: Physics analysis dictionary from Gemini
            output_path: Where to save the generated script
            headless: Whether to run in headless mode
            
        Returns:
            Path to the generated script
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"🔧 Generating Isaac Sim scene script...")
        
        # Extract components
        scene_comp = analysis_data.get("scene_composition", {})
        physics = analysis_data.get("physics_estimation", {})
        lighting = analysis_data.get("lighting_conditions", {})
        camera = analysis_data.get("camera_estimation", DEFAULT_SCENE_PARAMS["camera"])
        
        if headless:
             logger.info(f"🔧 Generating Isaac Sim scene script using Gemini (AI)...")
             try:
                 full_script = self._generate_script_with_gemini(analysis_data, headless, output_path)
             except Exception as e:
                 logger.error("Failed to generate with AI, falling back or erroring out.")
                 raise
        else:
             # Fallback or strict mode logic could go here, but for now we default to AI
             full_script = self._generate_script_with_gemini(analysis_data, headless, output_path)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_script)
        
        logger.info(f"✅ Script generated: {output_path}")
        
        return output_path
    
    def _load_template(self) -> str:
        """Load script template."""
        # For now, we build dynamically
        return ""
    
    def _generate_script_with_gemini(
        self,
        analysis_data: Dict[str, Any],
        headless: bool,
        output_path: Path
    ) -> str:
        """
        Generate the full Isaac Sim script using Gemini API.
        
        Args:
            analysis_data: The physics analysis JSON
            headless: Whether to run in headless mode
            output_path: Path where script will be saved
            
        Returns:
            Review of the generated code
        """
        system_instruction="""You are an expert Python Developer specializing in Nvidia Isaac Sim, USD (Universal Scene Description), and PhysX.
            
            Your task is to write a COMPLETE, EXECUTABLE Python script for Isaac Sim based on a physics analysis JSON.
            
            CRITICAL RULES:
            1.  **NO Markdown**: Return ONLY valid Python code. Do not wrap in ```python blocks.
            2.  **Imports**: standard imports + `from pxr import Usd, UsdGeom, UsdPhysics, Gf, UsdLux, PhysxSchema`.
            3.  **Headless Support**: Use `SimulationApp({"headless": HEADLESS})`.
            4.  **USD Stage**: Create a new stage at `USD_OUTPUT_PATH`.
            5.  **Ground Plane**: Always create a ground plane with physics.
            6.  **Physics**: Apply RigidBodyAPI, CollisionAPI, MassAPI, and MaterialAPI (friction/restitution) as specified in JSON.
            7.  **Units**: Isaac Sim uses meters.
            8.  **Structure**:
                -   Imports
                -   Configuration (headless, paths)
                -   Main function setup_scene(stage)
                -   Simulation loop
                -   Cleanup
            """
        
        # Prepare Prompt (Re-added)
        prompt = f"""
        Generate an Isaac Sim Python script for the following scene analysis:
        
        CONTEXT:
        - Headless Mode: {headless}
        - Output USD Path: {str(output_path).replace('.py', '.usd').replace('\\', '/')}
        
        ANALYSIS DATA:
        {json.dumps(analysis_data, indent=2)}
        
        REQUIREMENTS:
        1. Initialize `SimulationApp` FIRST.
        2. Create a USD stage.
        3. Create all objects specified in `scene_composition` with correct transforms.
        4. Apply physics properties from `physics_estimation` (mass, friction, restitution, velocity).
        5. Setup lighting and camera.
        6. Run a simulation loop for 300 frames.
        7. Save the USD file before closing.
        """
        
        logger.info(f"🤖 sending request to {LLM_PROVIDER}...")
        
        try:
            code = self.provider.generate_text(prompt, system_instruction)
            
            # Cleanup markdown if present (safety net)
            code = code.replace("```python", "").replace("```", "")
            
            return code
            
        except Exception as e:
            logger.error(f"❌ Code Generation failed: {e}")
            raise

    def _generate_imports(self) -> str:
        """Imports handled by full prompt generation."""
        return ""

    def _generate_initialization(self, headless: bool) -> str:
        """Init handled by full prompt generation."""
        return ""

    def _generate_physics_scene(self, physics: Dict[str, Any]) -> str:
        """Physics handled by full prompt generation."""
        return ""

    def _generate_environment(self, env_data: Dict[str, Any]) -> str:
        """Environment handled by full prompt generation."""
        return ""

    def _generate_objects(self, scene_objects: List[Dict[str, Any]], physics_objects: List[Dict[str, Any]]) -> str:
        """Objects handled by full prompt generation."""
        return ""

    def _generate_lighting(self, lighting: Dict[str, Any]) -> str:
        """Lighting handled by full prompt generation."""
        return ""

    def _generate_camera(self, camera: Dict[str, Any]) -> str:
        """Camera handled by full prompt generation."""
        return ""

    def _generate_simulation_loop(self) -> str:
        """Loop handled by full prompt generation."""
        return ""

    def _generate_cleanup(self) -> str:
        """Cleanup handled by full prompt generation."""
        return ""


def generate_scene_from_json(json_path: str | Path, output_script: str | Path) -> Path:
    """
    Command-line helper to generate scene from JSON file.
    
    Args:
        json_path: Path to analysis JSON
        output_script: Path for output Python script
        
    Returns:
        Path to generated script
    """
    with open(json_path, 'r') as f:
        analysis_data = json.load(f)
    
    generator = IsaacCodeGenerator()
    return generator.generate_scene(analysis_data, output_script)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python code_generator.py <analysis_json>")
        print("\\nExample:")
        print("  python code_generator.py output/ball_cup_analysis.json")
        sys.exit(1)
    
    json_file = sys.argv[1]
    output_file = USD_SCENES_DIR / "generated_scene.py"
    
    try:
        script_path = generate_scene_from_json(json_file, output_file)
        print(f"\\n✅ Script generated: {script_path}")
        print(f"\\n🚀 Run with Isaac Sim:")
        print(f"   ~/.local/share/ov/pkg/isaac_sim-*/python.sh {script_path}")
    except Exception as e:
        print(f"\\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
