"""
Video Analyzer Module

Uses Gemini API to analyze real-world videos and extract physics parameters
for recreation in Isaac Sim.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import time

try:
    import google.generativeai as genai
except ImportError:
    print("⚠️  google-generativeai not installed. Run: pip install google-generativeai")
    genai = None

from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GEMINI_TEMPERATURE,
    PHYSICS_ANALYSIS_PROMPT,
    OUTPUT_DIR
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VideoAnalyzer:
    """
    Analyzes videos using Gemini to extract physics parameters.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the VideoAnalyzer.
        
        Args:
            api_key: Gemini API key (uses config default if not provided)
        """
        self.api_key = api_key or GEMINI_API_KEY
        
        if not self.api_key:
            raise ValueError(
                "Gemini API key not found. Set GEMINI_API_KEY environment variable "
                "or pass it to VideoAnalyzer constructor."
            )
        
        if genai is None:
            raise ImportError("google-generativeai package required")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize model
        self.model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            generation_config={
                "temperature": GEMINI_TEMPERATURE,
                "response_mime_type": "application/json"
            }
        )
        
        logger.info(f"✓ Initialized VideoAnalyzer with model: {GEMINI_MODEL}")
    
    def analyze_video(
        self,
        video_path: str | Path,
        save_json: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze a video file and extract physics parameters.
        
        Args:
            video_path: Path to the video file
            save_json: Whether to save the analysis as JSON
            
        Returns:
            Dictionary containing scene composition, physics parameters, etc.
        """
        video_path = Path(video_path)
        
        if not video_path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")
        
        logger.info(f"📹 Analyzing video: {video_path.name}")
        logger.info("⏳ Uploading to Gemini API...")
        
        try:
            # Upload video file
            video_file = genai.upload_file(str(video_path))
            logger.info(f"✓ Video uploaded: {video_file.name}")
            
            # Wait for processing
            while video_file.state.name == "PROCESSING":
                logger.info("   Processing video...")
                time.sleep(2)
                video_file = genai.get_file(video_file.name)
            
            if video_file.state.name == "FAILED":
                raise RuntimeError(f"Video processing failed: {video_file.state}")
            
            logger.info("✓ Video ready for analysis")
            logger.info("🤖 Running Gemini 4D physics analysis...")
            
            # Generate analysis
            response = self.model.generate_content(
                [PHYSICS_ANALYSIS_PROMPT, video_file],
                request_options={"timeout": 120}
            )
            
            # Parse JSON response
            analysis_data = json.loads(response.text)
            
            logger.info("✓ Analysis complete!")
            
            # Validate required fields
            self._validate_analysis(analysis_data)
            
            # Save to file
            if save_json:
                output_path = OUTPUT_DIR / f"{video_path.stem}_analysis.json"
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(analysis_data, f, indent=2)
                logger.info(f"💾 Saved analysis: {output_path}")
            
            # Print summary
            self._print_summary(analysis_data)
            
            return analysis_data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse JSON response: {e}")
            logger.error(f"Raw response: {response.text}")
            raise
        except Exception as e:
            logger.error(f"❌ Analysis failed: {e}")
            raise
    
    def _validate_analysis(self, data: Dict[str, Any]) -> None:
        """
        Validate the analysis output has required fields.
        
        Args:
            data: Analysis dictionary
            
        Raises:
            ValueError: If required fields are missing
        """
        required_keys = ["scene_composition", "physics_estimation"]
        
        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required field: {key}")
        
        # Check objects exist
        if not data["scene_composition"].get("objects"):
            raise ValueError("No objects found in scene_composition")
        
        if not data["physics_estimation"].get("objects"):
            raise ValueError("No physics objects found")
            
        # Motion Estimation validation (Warning only)
        if "motion_estimation" not in data:
            logger.warning("⚠️  'motion_estimation' field missing from analysis")
        else:
            motion = data["motion_estimation"]
            if not motion.get("static_background"):
                logger.warning("⚠️  No static_background description found")
            if not motion.get("dynamic_agents"):
                logger.warning("⚠️  No dynamic_agents found")
        
        logger.info("✓ Analysis validation passed")
    
    def _print_summary(self, data: Dict[str, Any]) -> None:
        """
        Print a human-readable summary of the analysis.
        
        Args:
            data: Analysis dictionary
        """
        print("\n" + "=" * 60)
        print("📊 PHYSICS ANALYSIS SUMMARY")
        print("=" * 60)
        
        # Scene composition
        objects = data["scene_composition"]["objects"]
        print(f"\n🎬 Scene Objects: {len(objects)}")
        for i, obj in enumerate(objects, 1):
            obj_type = obj.get("type", "unknown")
            obj_id = obj.get("id", f"object_{i}")
            print(f"   {i}. {obj_id} ({obj_type})")
        
        # Physics parameters
        physics_objects = data["physics_estimation"]["objects"]
        print(f"\n⚛️  Physics Objects: {len(physics_objects)}")
        for obj in physics_objects:
            obj_id = obj.get("id", "unknown")
            mass = obj.get("mass", 0)
            restitution = obj.get("restitution", 0)
            print(f"   • {obj_id}: mass={mass}kg, bounce={restitution}")
        
        # Timeline
        if "event_timeline" in data:
            timeline = data["event_timeline"]
            print(f"\n⏱️  Events: {len(timeline)}")
            for event in timeline[:3]:  # Show first 3 events
                frame = event.get("frame", 0)
                event_type = event.get("event", "unknown")
                print(f"   Frame {frame}: {event_type}")
        
        # Lighting
        if "lighting_conditions" in data:
            lighting = data["lighting_conditions"]
            if "dome_light" in lighting:
                dome_intensity = lighting["dome_light"].get("intensity", 0)
                print(f"\n💡 Dome Light Intensity: {dome_intensity}")
                # Motion Estimation
        if "motion_estimation" in data:
            motion = data["motion_estimation"]
            print(f"\n🎥 Motion Analysis:")
            if "static_background" in motion:
                bg = motion["static_background"]
                print(f"   • Static Background: {bg.get('description', 'unknown')} (Stability: {bg.get('stability_score', 0)})")
            
            if "dynamic_agents" in motion:
                agents = motion["dynamic_agents"]
                print(f"   • Dynamic Agents: {len(agents)}")
                for agent in agents:
                    print(f"     - {agent.get('id', 'unknown')}: {agent.get('movement_type', 'unknown')}")

        # Physics Reasoning (New)
        if "physics_reasoning" in data:
            reasoning = data["physics_reasoning"]
            print(f"\n🧠 Physics Reasoning (Confidence: {reasoning.get('confidence_score', 'N/A')}):")
            print(f"   \"{reasoning.get('observation_summary', 'No summary provided.')}\"")
            
            if "object_analysis" in reasoning:
                for obj in reasoning["object_analysis"]:
                    print(f"   • {obj.get('id', 'unknown')}: {obj.get('material_inference', '')}")
                    print(f"     - Mass: {obj.get('mass_reasoning', '')}")
                    print(f"     - Friction: {obj.get('friction_reasoning', '')}")

        print("\n" + "=" * 60 + "\n")


def analyze_video_cli(video_path: str) -> Dict[str, Any]:
    """
    Command-line interface for video analysis.
    
    Args:
        video_path: Path to video file
        
    Returns:
        Analysis data dictionary
    """
    analyzer = VideoAnalyzer()
    return analyzer.analyze_video(video_path)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python video_analyzer.py <video_path>")
        print("\nExample:")
        print("  python video_analyzer.py examples/ball_cup.mp4")
        sys.exit(1)
    
    video_file = sys.argv[1]
    
    try:
        result = analyze_video_cli(video_file)
        print(f"\n✅ Analysis saved to: output/{Path(video_file).stem}_analysis.json")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
