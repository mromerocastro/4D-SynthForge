"""
Simple USD Scene Generator

Generates standalone USD files that can be opened in Isaac Sim GUI.
No simulation execution - just USD export.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_usd_only(analysis_json_path: str | Path, output_usd_path: str | Path):
    """
    Generate a USD file from analysis JSON without running simulation.
    
    This creates a pure USD file that can be opened in Isaac Sim GUI.
    """
    from pxr import Usd, UsdGeom, UsdPhysics, Gf, UsdLux, PhysxSchema
    
    # Load analysis
    with open(analysis_json_path, 'r') as f:
        analysis_data = json.load(f)
    
    output_usd_path = Path(output_usd_path)
    output_usd_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"🔧 Creating USD scene: {output_usd_path}")
    
    # Create USD stage
    stage = Usd.Stage.CreateNew(str(output_usd_path))
    
    # Set metadata
    stage.SetMetadata("metersPerUnit", 1.0)
    stage.SetMetadata("upAxis", "Y")
    
    # Create world
    world_prim = UsdGeom.Xform.Define(stage, "/World")
    stage.SetDefaultPrim(world_prim.GetPrim())
    
    # Extract data
    scene_comp = analysis_data.get("scene_composition", {})
    physics = analysis_data.get("physics_estimation", {})
    lighting = analysis_data.get("lighting_conditions", {})
    
    # Create physics scene
    gravity = physics.get("gravity", {"x": 0.0, "y": -9.81, "z": 0.0})
    physics_scene = UsdPhysics.Scene.Define(stage, "/World/physicsScene")
    physics_scene.CreateGravityDirectionAttr().Set(Gf.Vec3f(0.0, -1.0, 0.0))
    physics_scene.CreateGravityMagnitudeAttr().Set(abs(gravity.get('y', 9.81)))
    
    # PhysX settings
    physx_scene = PhysxSchema.PhysxSceneAPI.Apply(stage.GetPrimAtPath("/World/physicsScene"))
    physx_scene.CreateEnableCCDAttr(True)
    physx_scene.CreateEnableStabilizationAttr(True)
    
    logger.info("✓ Physics scene configured")
    
    # Create ground
    ground_path = "/World/Ground"
    ground = UsdGeom.Mesh.Define(stage, ground_path)
    
    points = [
        Gf.Vec3f(-5, 0, -5),
        Gf.Vec3f(5, 0, -5),
        Gf.Vec3f(5, 0, 5),
        Gf.Vec3f(-5, 0, 5)
    ]
    ground.CreatePointsAttr(points)
    ground.CreateFaceVertexCountsAttr([4])
    ground.CreateFaceVertexIndicesAttr([0, 1, 2, 3])
    ground.CreateNormalsAttr([Gf.Vec3f(0, 1, 0)] * 4)
    
    UsdPhysics.CollisionAPI.Apply(ground.GetPrim())
    ground_material = UsdPhysics.MaterialAPI.Apply(ground.GetPrim())
    ground_material.CreateStaticFrictionAttr(0.5)
    ground_material.CreateDynamicFrictionAttr(0.4)
    ground_material.CreateRestitutionAttr(0.3)
    
    logger.info("✓ Ground created")
    
    # Create objects
    physics_map = {obj.get("id"): obj for obj in physics.get("objects", [])}
    
    for i, obj in enumerate(scene_comp.get("objects", [])):
        obj_id = obj.get("id", f"object_{i}")
        obj_type = obj.get("type", "sphere")
        position = obj.get("position", {"x": 0, "y": 1, "z": 0})
        scale = obj.get("scale", {"x": 0.5, "y": 0.5, "z": 0.5})
        
        path = f"/World/{obj_id}"
        pos = Gf.Vec3d(position.get('x', 0), position.get('y', 1), position.get('z', 0))
        
        # Create geometry
        if obj_type == "sphere":
            geom = UsdGeom.Sphere.Define(stage, path)
            geom.CreateRadiusAttr(scale.get('x', 0.5))
            geom.AddTranslateOp().Set(pos)
        elif obj_type == "cube":
            geom = UsdGeom.Cube.Define(stage, path)
            geom.CreateSizeAttr(scale.get('x', 1.0))
            geom.AddTranslateOp().Set(pos)
        elif obj_type == "cylinder":
            geom = UsdGeom.Cylinder.Define(stage, path)
            geom.CreateRadiusAttr(scale.get('x', 0.5))
            geom.CreateHeightAttr(scale.get('y', 1.0))
            geom.AddTranslateOp().Set(pos)
        else:
            geom = UsdGeom.Sphere.Define(stage, path)
            geom.CreateRadiusAttr(0.5)
            geom.AddTranslateOp().Set(pos)
        
        # Add physics if available
        physics_props = physics_map.get(obj_id)
        if physics_props:
            prim = stage.GetPrimAtPath(path)
            
            rigid_body = UsdPhysics.RigidBodyAPI.Apply(prim)
            velocity = physics_props.get('initial_velocity', {'x': 0, 'y': 0, 'z': 0})
            rigid_body.CreateVelocityAttr(Gf.Vec3f(
                velocity.get('x', 0),
                velocity.get('y', 0),
                velocity.get('z', 0)
            ))
            
            mass_api = UsdPhysics.MassAPI.Apply(prim)
            mass_api.CreateMassAttr(physics_props.get('mass', 1.0))
            
            UsdPhysics.CollisionAPI.Apply(prim)
            
            material_api = UsdPhysics.MaterialAPI.Apply(prim)
            material_api.CreateStaticFrictionAttr(physics_props.get('static_friction', 0.3))
            material_api.CreateDynamicFrictionAttr(physics_props.get('dynamic_friction', 0.25))
            material_api.CreateRestitutionAttr(physics_props.get('restitution', 0.5))
            
            logger.info(f"✓ Created {obj_id} with physics")
        else:
            logger.info(f"✓ Created {obj_id} (static)")
    
    # Add lighting
    dome_intensity = lighting.get("dome_light", {}).get("intensity", 1000.0)
    dome_light = UsdLux.DomeLight.Define(stage, "/World/DomeLight")
    dome_light.CreateIntensityAttr(dome_intensity)
    
    key_light_data = lighting.get("key_light", {})
    key_intensity = key_light_data.get("intensity", 5000.0)
    key_pos = key_light_data.get("position", {"x": 5, "y": 5, "z": 5})
    
    key_light = UsdLux.SphereLight.Define(stage, "/World/KeyLight")
    key_light.CreateIntensityAttr(key_intensity)
    key_light.CreateRadiusAttr(0.5)
    key_light.AddTranslateOp().Set(Gf.Vec3d(
        key_pos.get('x', 5),
        key_pos.get('y', 5),
        key_pos.get('z', 5)
    ))
    
    logger.info("✓ Lighting configured")
    
    # Add camera
    camera_data = analysis_data.get("camera_estimation", {"position": {"x": 0, "y": 1.5, "z": 3}})
    cam_pos = camera_data.get("position", {"x": 0, "y": 1.5, "z": 3})
    
    camera = UsdGeom.Camera.Define(stage, "/World/Camera")
    camera.CreateFocalLengthAttr(camera_data.get("focal_length", 50.0))
    camera.CreateFocusDistanceAttr(100)
    camera.AddTranslateOp().Set(Gf.Vec3d(
        cam_pos.get('x', 0),
        cam_pos.get('y', 1.5),
        cam_pos.get('z', 3)
    ))
    
    logger.info("✓ Camera configured")
    
    # Save USD
    stage.Save()
    
    logger.info(f"✅ USD file saved: {output_usd_path}")
    logger.info(f"\n📂 To open in Isaac Sim:")
    logger.info(f"   1. Open Isaac Sim GUI")
    logger.info(f"   2. File → Open")
    logger.info(f"   3. Navigate to: {output_usd_path}")
    logger.info(f"   4. Click Play ▶️ to run simulation")
    
    return output_usd_path


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python usd_generator.py <analysis_json>")
        print("\nExample:")
        print("  python usd_generator.py output/ball_cup_analysis.json")
        sys.exit(1)
    
    from config import USD_SCENES_DIR
    
    json_file = sys.argv[1]
    output_file = USD_SCENES_DIR / "scene.usd"
    
    try:
        generate_usd_only(json_file, output_file)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
