"""
Main Pipeline - 4D-SynthForge

End-to-end orchestration: Video → Gemini Analysis → Code Generation → Rendering → Synthetic Data
"""

import argparse
import json
import logging
from pathlib import Path
import subprocess
import sys
from typing import List, Dict, Any
from tqdm import tqdm

from config import (
    ISAAC_SIM_PYTHON,
    OUTPUT_DIR,
    USD_SCENES_DIR,
    RENDERS_DIR
)
from video_analyzer import VideoAnalyzer
from code_generator import IsaacCodeGenerator
from domain_randomizer import DomainRandomizer
from usd_variant_generator import USDVariantGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SynthForgePipeline:
    """
    Main pipeline orchestrator for 4D-SynthForge.
    """
    
    def __init__(self):
        """Initialize the pipeline."""
        self.analyzer = None  # Lazy init (requires API key)
        self.code_generator = IsaacCodeGenerator()
        logger.info("✓ Pipeline initialized")
    
    def run_full_pipeline(
        self,
        video_path: str | Path,
        output_dir: str | Path = OUTPUT_DIR,
        num_variations: int = 9,
        should_render: bool = False
    ):
        """
        Run the complete pipeline from video to synthetic data.
        
        Args:
            video_path: Path to input video
            output_dir: Where to save outputs
            num_variations: Number of synthetic variations to generate
            should_render: Whether to actually render (requires Isaac Sim)
        """
        video_path = Path(video_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("=" * 70)
        logger.info("🚀 4D-SYNTHFORGE PIPELINE")
        logger.info("=" * 70)
        logger.info(f"Input: {video_path}")
        logger.info(f"Output: {output_dir}")
        logger.info(f"Variations: {num_variations}")
        logger.info("=" * 70 + "\n")
        
        # Step 1: Analyze video with Gemini
        logger.info("STEP 1/5: Video Analysis with Gemini")
        logger.info("-" * 70)
        
        analysis_json = self.step1_analyze_video(video_path)
        
        # Step 2: Generate base scene code
        logger.info("\nSTEP 2/5: Code Generation")
        logger.info("-" * 70)
        
        base_script = self.step2_generate_code(analysis_json)
        
        # Step 3: Create variations
        logger.info("\nSTEP 3/5: Domain Randomization")
        logger.info("-" * 70)
        
        variations = self.step3_create_variations(analysis_json, num_variations)
        
        # Step 4: Generate scripts for all variations
        logger.info("\nSTEP 4/5: Generating Variation Scripts")
        logger.info("-" * 70)
        
        variation_output = self.step4_generate_variation_scripts(variations, analysis_json)
        
        # Step 5: Render (optional)
        if should_render:
            logger.info("\nSTEP 5/5: Batch Rendering")
            logger.info("-" * 70)
            
            self.step5_batch_render(variation_scripts)
        else:
            logger.info("\nSTEP 5/5: Skipping Rendering")
            logger.info("-" * 70)
            logger.info("⏭️  Rendering skipped. Run with --render to execute in Isaac Sim")
            logger.info(f"   Scripts ready at: {USD_SCENES_DIR}")
        
        # Summary
        self.print_summary(video_path, analysis_json, num_variations, should_render)
    
    def step1_analyze_video(self, video_path: Path) -> Path:
        """
        Step 1: Analyze video with Gemini.
        
        Returns:
            Path to analysis JSON
        """
        try:
            self.analyzer = VideoAnalyzer()
            analysis_data = self.analyzer.analyze_video(video_path)
            
            # Save JSON
            json_path = OUTPUT_DIR / f"{video_path.stem}_analysis.json"
            with open(json_path, 'w') as f:
                json.dump(analysis_data, f, indent=2)
            
            logger.info(f"✅ Analysis saved: {json_path}")
            return json_path
            
        except Exception as e:
            logger.error(f"❌ Video analysis failed: {e}")
            raise
    
    def step2_generate_code(self, analysis_json: Path) -> Path:
        """
        Step 2: Generate base Isaac Sim script.
        
        Returns:
            Path to generated script
        """
        try:
            with open(analysis_json, 'r') as f:
                analysis_data = json.load(f)
            
            script_path = USD_SCENES_DIR / "base_scene.py"
            self.code_generator.generate_scene(
                analysis_data,
                script_path,
                headless=True
            )
            
            logger.info(f"✅ Base script generated: {script_path}")
            return script_path
            
        except Exception as e:
            logger.error(f"❌ Code generation failed: {e}")
            raise
    
    def step3_create_variations(self, analysis_json: Path, count: int) -> List[Dict]:
        """
        Step 3: Create randomized variations.
        
        Returns:
            List of variation dictionaries
        """
        try:
            with open(analysis_json, 'r') as f:
                base_analysis = json.load(f)
            
            randomizer = DomainRandomizer(base_analysis)
            variations = randomizer.generate_variations(count)
            
            # Save variations
            var_dir = OUTPUT_DIR / "variations"
            var_dir.mkdir(exist_ok=True)
            
            for i, var in enumerate(variations):
                var_path = var_dir / f"variation_{i:03d}.json"
                with open(var_path, 'w') as f:
                    json.dump(var, f, indent=2)
            
            logger.info(f"✅ {len(variations)} variations created")
            return variations
            
        except Exception as e:
            logger.error(f"❌ Variation generation failed: {e}")
            raise
    
    def step4_generate_variation_scripts(self, variations: List[Dict], analysis_json: Path = None) -> Path:
        """
        Step 4: Generate a SINGLE USD file with VariantSets for all variations.
        
        Returns:
            Path to the master USD file
        """
        try:
            logger.info(f"Generating master scene with {len(variations)} variants...")
            
            # Load base analysis if not provided (needed for static topology)
            if not analysis_json:
                # Fallback: recreate base analysis from first variation but stripped
                base_analysis = variations[0] 
            else:
                 with open(analysis_json, 'r') as f:
                    base_analysis = json.load(f)

            # Define output path
            output_usd = USD_SCENES_DIR / "master_scene_variants.usd"
            
            # Use the new Variant Generator
            generator = USDVariantGenerator()
            
            # Check if USD libraries are available (we might not be in isaac python)
            # If not, we cannot generate the USD directly.
            # In that case, we generate a python script that GENERATES the USD.
            
            try:
                from pxr import Usd
                # If we are here, we have USD libraries
                generator.create_variant_stage(base_analysis, variations, output_usd)
                return output_usd
                
            except ImportError:
                logger.warning("⚠️  USD libraries not found in current environment.")
                logger.warning("   Generating a Python script to build the variant stage in Isaac Sim.")
                
                # Generate a python script that imports USDVariantGenerator
                # We need to save the variations list to a file so the script can load it
                variations_file = OUTPUT_DIR / "all_variations.json"
                with open(variations_file, 'w') as f:
                    json.dump(variations, f, indent=2)
                
                # Create the builder script
                builder_script = USD_SCENES_DIR / "build_variants.py"
                
                script_content = f'''"""
Auto-generated script to build USD variants inside Isaac Sim
"""
import json
import sys
import os

# Add project root to path to find modules
sys.path.append(r"{str(Path(__file__).parent)}")

from usd_variant_generator import USDVariantGenerator

def main():
    print("🚀 Starting USD Variant Generation inside Isaac Sim...")
    
    # Paths
    base_json = r"{str(analysis_json)}"
    variations_json = r"{str(variations_file)}"
    output_usd = r"{str(output_usd)}"
    
    # Load data
    with open(base_json, 'r') as f:
        base_data = json.load(f)
        
    with open(variations_json, 'r') as f:
        variations = json.load(f)
        
    # Generate
    generator = USDVariantGenerator()
    generator.create_variant_stage(base_data, variations, output_usd)
    print("✅ Done!")

if __name__ == "__main__":
    main()
'''
                with open(builder_script, 'w', encoding='utf-8') as f:
                    f.write(script_content)
                    
                logger.info(f"✅ Builder script created: {builder_script}")
                return builder_script

        except Exception as e:
            logger.error(f"❌ Variant generation failed: {e}")
            raise
    
    def step5_batch_render(self, scripts: List[Path]) -> None:
        """
        Step 5: Batch render all variations in Isaac Sim.
        
        Note: This requires Isaac Sim to be installed.
        """
        if not ISAAC_SIM_PYTHON or not ISAAC_SIM_PYTHON.exists():
            logger.error("❌ Isaac Sim Python not found!")
            logger.error(f"   Expected at: {ISAAC_SIM_PYTHON}")
            logger.error("   Please install Isaac Sim or set ISAAC_SIM_PATH in config.py")
            return
        
        try:
            logger.info(f"Rendering {len(scripts)} variations...")
            logger.info(f"Using Isaac Sim: {ISAAC_SIM_PYTHON}")
            
            for i, script in enumerate(tqdm(scripts, desc="Rendering")):
                # Run Isaac Sim in headless mode
                cmd = [str(ISAAC_SIM_PYTHON), str(script)]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout per render
                )
                
                if result.returncode != 0:
                    logger.warning(f"⚠️  Variation {i} failed:")
                    logger.warning(result.stderr[:200])
            
            logger.info(f"✅ Rendering complete")
            
        except subprocess.TimeoutExpired:
            logger.error("❌ Rendering timeout exceeded")
        except Exception as e:
            logger.error(f"❌ Rendering failed: {e}")
    
    def print_summary(
        self,
        video_path: Path,
        analysis_json: Path,
        num_variations: int,
        rendered: bool
    ) -> None:
        """Print final summary."""
        print("\n" + "=" * 70)
        print("✅ PIPELINE COMPLETE!")
        print("=" * 70)
        print(f"\n📹 Original Video: {video_path}")
        print(f"📊 Analysis JSON: {analysis_json}")
        print(f"🎲 Variations Generated: {num_variations}")
        print(f"📁 Output Directory: {OUTPUT_DIR}")
        print(f"\n📂 Key Outputs:")
        print(f"   • Analysis: {analysis_json}")
        print(f"   • Scripts: {USD_SCENES_DIR}/base_scene.py")
        print(f"   • Master USD: {USD_SCENES_DIR}/master_scene_variants.usd")
        print(f"   • Variations: {OUTPUT_DIR}/variations/")
        
        if rendered:
            print(f"   • Renders: {RENDERS_DIR}/")
        else:
            print(f"\n🚀 Next Steps:")
            print(f"   1. Install Nvidia Isaac Sim")
            print(f"   2. Run scripts with: ~/.local/share/ov/pkg/isaac_sim-*/python.sh <script.py>")
            print(f"   3. Or re-run with --render flag")
        
        print("\n" + "=" * 70 + "\n")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="4D-SynthForge: Video → Physics Analysis → Synthetic Data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze video and generate 9 variations (no rendering)
  python main.py input.mp4
  
  # Generate 100 variations
  python main.py input.mp4 --count 100
  
  # Full pipeline with rendering (requires Isaac Sim)
  python main.py input.mp4 --count 9 --render
        """
    )
    
    parser.add_argument(
        "video",
        type=str,
        help="Path to input video file"
    )
    
    parser.add_argument(
        "--count",
        type=int,
        default=9,
        help="Number of variations to generate (default: 9)"
    )
    
    parser.add_argument(
        "--render",
        action="store_true",
        help="Render variations in Isaac Sim (requires installation)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default=str(OUTPUT_DIR),
        help=f"Output directory (default: {OUTPUT_DIR})"
    )
    
    args = parser.parse_args()
    
    # Validate input
    video_path = Path(args.video)
    if not video_path.exists():
        print(f"❌ Error: Video file not found: {video_path}")
        sys.exit(1)
    
    # Run pipeline
    try:
        pipeline = SynthForgePipeline()
        pipeline.run_full_pipeline(
            video_path=video_path,
            output_dir=args.output,
            num_variations=args.count,
            should_render=args.render
        )
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
