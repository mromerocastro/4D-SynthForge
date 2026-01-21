"""
USD Variant Scene Generator

Generates a SINGLE USD file containing multiple scene variations using USD VariantSets.
This allows switching between simulation scenarios (lighting, physics, materials) 
instantly within one file.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List
import copy

# USD Imports
try:
    from pxr import Usd, UsdGeom, UsdPhysics, Gf, UsdLux, PhysxSchema, Sdf
except ImportError:
    print("⚠️  USD libraries not found. This script must be run within Isaac Sim python.sh or an environment with USD installed.")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class USDVariantGenerator:
    """Generates a single USD stage with VariantSets for multiple variations."""
    
    def __init__(self):
        self.stage = None
        self.root_prim = None
        self.variant_set = None
        
    def create_variant_stage(self, base_analysis: Dict[str, Any], variations: List[Dict[str, Any]], output_path: str | Path):
        """
        Main function to author the USD stage with variants.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"⚡ Creating USD Stage with {len(variations)} variants at: {output_path}")
        
        # 1. Create Stage
        # CRITICAL FIX: Handle Isaac Sim's persistent memory
        # If the layer exists in Sdf memory, we must forcefully clear and expire it to avoid conflicts.
        force_reload = True
        existing_layer = Sdf.Layer.Find(str(output_path))
        
        if existing_layer:
            logger.info(f"   ♻️  Recycling existing layer in memory: {output_path}")
            # If we want a fresh start, we should clear it.
            existing_layer.Clear()
            
            # Using Open() on a cleared valid layer is safer than CreateNew() which fails if identifier exists
            self.stage = Usd.Stage.Open(existing_layer)
        else:
            # Clean slate
            self.stage = Usd.Stage.CreateNew(str(output_path))
            
        if not self.stage:
            raise RuntimeError(f"Failed to create or open USD stage at {output_path}")

        UsdGeom.SetStageUpAxis(self.stage, UsdGeom.Tokens.y)
        UsdGeom.SetStageMetersPerUnit(self.stage, 1.0)
        
        # 2. Define Root
        # Ensure we define the root properly
        self.root_prim = UsdGeom.Xform.Define(self.stage, "/World").GetPrim()
        self.stage.SetDefaultPrim(self.root_prim)
        
        # 3. Author STATIC Topology (Geometry that exists in all variations)
        # We use the base_analysis to define WHAT exists.
        self._author_static_topology(base_analysis)
        
        # 4. Create VariantSet
        # This tells USD that this prim has a set of variants called "SimulationVariant"
        self.variant_set = self.root_prim.GetVariantSets().AddVariantSet("SimulationVariant")
        
        # 5. Author Variations
        for i, variation_data in enumerate(variations):
            variant_name = f"Variation_{i:03d}"
            logger.info(f"   Authoring variant: {variant_name}")
            
            # Create the variant option
            self.variant_set.AddVariant(variant_name)
            
            # Context Switch: Everything done inside this block belongs ONLY to this variant
            self.variant_set.SetVariantSelection(variant_name)
            
            with self.variant_set.GetVariantEditContext():
                self._author_variation_overrides(variation_data)
                
        # 6. Select first variant by default
        if variations:
            self.variant_set.SetVariantSelection("Variation_000")
            
        # 7. Save
        self.stage.Save()
        logger.info(f"✅ Successfully saved USD Variant file: {output_path}")
        return output_path

    def _author_static_topology(self, data: Dict[str, Any]):
        """Creates the objects, lights, and cameras (without their variable properties)."""
        scene_comp = data.get("scene_composition", {})
        
        # -- Ground --
        ground_path = "/World/Ground"
        ground = UsdGeom.Mesh.Define(self.stage, ground_path)
        points = [Gf.Vec3f(-5,0,-5), Gf.Vec3f(5,0,-5), Gf.Vec3f(5,0,5), Gf.Vec3f(-5,0,5)]
        ground.CreatePointsAttr(points)
        ground.CreateFaceVertexCountsAttr([4])
        ground.CreateFaceVertexIndicesAttr([0,1,2,3])
        ground.CreateNormalsAttr([Gf.Vec3f(0,1,0)]*4)
        UsdPhysics.CollisionAPI.Apply(ground.GetPrim())
        
        # -- Objects --
        for obj in scene_comp.get("objects", []):
            obj_id = obj.get("id")
            obj_type = obj.get("type", "sphere")
            path = f"/World/{obj_id}"
            
            # Improved Shape Approximation Logic
            if obj_type == "sphere":
                UsdGeom.Sphere.Define(self.stage, path)
            elif obj_type == "cube":
                UsdGeom.Cube.Define(self.stage, path)
            elif obj_type == "cylinder":
                UsdGeom.Cylinder.Define(self.stage, path)
            else:
                # Heuristic mapping for unknown types (e.g. "mesh")
                name_lower = obj_id.lower()
                if any(x in name_lower for x in ["cup", "mug", "cylinder", "bottle", "can", "saucer", "plate", "disk"]):
                    UsdGeom.Cylinder.Define(self.stage, path)
                elif any(x in name_lower for x in ["box", "cube", "table", "block", "brick", "monitor", "screen"]):
                    UsdGeom.Cube.Define(self.stage, path)
                else:
                    # Default fallback
                    logger.warning(f"Unknown object type '{obj_type}' for {obj_id}. Defaulting to Sphere.")
                    UsdGeom.Sphere.Define(self.stage, path)
            
            # Apply API schemas on the base topology so they exist
            prim = self.stage.GetPrimAtPath(path)
            if prim.IsValid():
                UsdPhysics.RigidBodyAPI.Apply(prim)
                UsdPhysics.CollisionAPI.Apply(prim)
                UsdPhysics.MassAPI.Apply(prim)
            else:
                logger.error(f"Failed to create prim at {path}")
            
        # -- Lights --
        UsdLux.DomeLight.Define(self.stage, "/World/DomeLight")
        UsdLux.SphereLight.Define(self.stage, "/World/KeyLight")
        
        # -- Physics Scene --
        scene = UsdPhysics.Scene.Define(self.stage, "/World/PhysicsScene")
        scene.CreateGravityDirectionAttr().Set(Gf.Vec3f(0.0, -1.0, 0.0))

    def _author_variation_overrides(self, data: Dict[str, Any]):
        """Sets the specific values for the current variant context."""
        physics = data.get("physics_estimation", {})
        lighting = data.get("lighting_conditions", {})
        scene_comp = data.get("scene_composition", {})
        
        # -- 1. Update Physics Constants --
        gravity = physics.get("gravity", {"x": 0, "y": -9.81, "z": 0})
        scene_prim = self.stage.GetPrimAtPath("/World/PhysicsScene")
        # Note: Usually gravity doesn't change per variant, but it can!
        scene_prim.GetAttribute("physics:gravityMagnitude").Set(abs(gravity.get('y', -9.81)))

        # -- 2. Update Objects (Position, Scale, Physics, Material) --
        physics_map = {obj.get("id"): obj for obj in physics.get("objects", [])}
        object_map = {obj.get("id"): obj for obj in scene_comp.get("objects", [])}
        
        for obj_id, obj_data in object_map.items():
            prim_path = f"/World/{obj_id}"
            prim = self.stage.GetPrimAtPath(prim_path)
            if not prim.IsValid(): continue
            
            # Transform
            pos = obj_data.get("position", {})
            rot = obj_data.get("rotation", {})
            scale = obj_data.get("scale", {})
            
            # Application Order: Scale -> Rotate -> Translate (Standard)
            xform = UsdGeom.Xformable(prim)
            xform.ClearXformOpOrder()
            
            # 1. Translate
            xform.AddTranslateOp().Set(Gf.Vec3d(pos.get('x',0), pos.get('y',0), pos.get('z',0)))
            
            # 2. Rotate (XYZ)
            xform.AddRotateXYZOp().Set(Gf.Vec3f(rot.get('x',0), rot.get('y',0), rot.get('z',0)))
            
            # 3. Scale
            # Use 'x' as uniform scale if others missing, or default to 1.0
            sx = scale.get('x', 1.0)
            sy = scale.get('y', sx)
            sz = scale.get('z', sx)
            xform.AddScaleOp().Set(Gf.Vec3f(sx, sy, sz))
            
            # Physics Props
            phy_props = physics_map.get(obj_id, {})
            
            mass_api = UsdPhysics.MassAPI(prim)
            mass_api.GetMassAttr().Set(phy_props.get("mass", 1.0))
            
            mat_api = UsdPhysics.MaterialAPI.Apply(prim) # Ensure applied
            mat_api.CreateStaticFrictionAttr().Set(phy_props.get("static_friction", 0.5))
            mat_api.CreateDynamicFrictionAttr().Set(phy_props.get("dynamic_friction", 0.5))
            mat_api.CreateRestitutionAttr().Set(phy_props.get("restitution", 0.5))
            
            rb_api = UsdPhysics.RigidBodyAPI(prim)
            vel = phy_props.get("initial_velocity", {})
            rb_api.GetVelocityAttr().Set(Gf.Vec3f(vel.get('x',0), vel.get('y',0), vel.get('z',0)))
            
            # Visual Material (Color)
            if "material" in obj_data:
                color = obj_data["material"].get("base_color", {"r": 1, "g": 1, "b": 1})
                # Simple display color for now
                gprim = UsdGeom.Gprim(prim)
                gprim.GetDisplayColorAttr().Set([Gf.Vec3f(color['r'], color['g'], color['b'])])

        # -- 3. Update Lighting --
        dome = lighting.get("dome_light", {})
        key = lighting.get("key_light", {})
        
        dome_prim = self.stage.GetPrimAtPath("/World/DomeLight")
        if dome_prim:
            dome_light = UsdLux.DomeLight(dome_prim)
            dome_light.GetIntensityAttr().Set(dome.get("intensity", 1000))
            
        key_prim = self.stage.GetPrimAtPath("/World/KeyLight")
        if key_prim:
            key_light = UsdLux.SphereLight(key_prim)
            key_light.GetIntensityAttr().Set(key.get("intensity", 5000))
            kpos = key.get("position", {})
            xform = UsdGeom.Xformable(key_prim)
            xform.ClearXformOpOrder()
            xform.AddTranslateOp().Set(Gf.Vec3d(kpos.get('x',5), kpos.get('y',5), kpos.get('z',5)))


if __name__ == "__main__":
    import sys
    from domain_randomizer import DomainRandomizer
    
    # Example usage
    if len(sys.argv) < 2:
        print("Usage: python usd_variant_generator.py <base_analysis_json> [count]")
        sys.exit(1)
        
    json_path = sys.argv[1]
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    # 1. Load Base
    with open(json_path, 'r') as f:
        base_data = json.load(f)
        
    # 2. Generate Variations in Memory
    randomizer = DomainRandomizer(base_data)
    variations = randomizer.generate_variations(count)
    
    # 3. Create USD with Variants
    generator = USDVariantGenerator()
    output_usd = Path("output/usd_scenes/master_scene_variants.usd")
    
    try:
        generator.create_variant_stage(base_data, variations, output_usd)
        print(f"✅ Created Master Scene with {count} variants!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
