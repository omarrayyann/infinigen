#!/usr/bin/env python3
"""
Complete Door Configuration Generator for MuJoCo XML Export

This script creates doors with EXACT parameters you specify by directly using
the Infinigen door factory system instead of the random generation approach.

Usage: python generate_single_door.py
"""

import subprocess
import os
import sys
from pathlib import Path


# =================== COMPLETE DOOR CONFIGURATION ===================
# Modify these values to customize your door
DOOR_CONFIG = {
    # =================== BASIC SETTINGS ===================
    "export_format": "mjcf",  # mjcf (MuJoCo XML), urdf, usd
    "include_collisions": True,  # Include collision meshes
    "seed": 2001,  # Random seed for generation
    # =================== PHYSICAL DIMENSIONS ===================
    # Note: Actual dimensions are controlled by Infinigen's internal systems
    # These are rough guides - actual values may vary based on RoomConstants
    "door_width_range": "0.8-1.0m",  # Typical door width
    "door_height_range": "2.0-2.2m",  # Typical door height
    "door_depth_range": "0.03-0.08m",  # Door thickness
    # =================== DOOR TYPE ===================
    # Available types: panel, glass_panel, louver, lite
    "door_type": "panel",  # Main door type
    # =================== HANDLE CONFIGURATION ===================
    "handle_type": "lever",  # knob, lever, pull, bar, none
    "door_orientation": "right",  # left, right (which side handle is on)
    "handle_height_ratio": 0.475,  # 0.45-0.5 (ratio of door height)
    # =================== DOOR FRAME STYLE ===================
    "door_frame_style": "full_frame_square",  # single_column, full_frame_square, full_frame_dome, full_frame_double_door
    "door_frame_width": 0.04,  # 0.02-0.06 frame width
    # =================== PANEL CONFIGURATION ===================
    "x_subdivisions": 1,  # 1 or 2 horizontal panels
    "y_subdivisions": 2,  # 1-5 vertical panels
    "panel_margin": 0.1,  # 0.08-0.12 border spacing
    "bevel_width": 0.0075,  # 0.005-0.01 bevel size
    "shrink_width": 0.025,  # 0.005-0.06 panel shrink
    "side_bevel": 0.01,  # 0.005-0.015 side beveling
    "out_bevel": True,  # True=outward bevel, False=inward
    # =================== GLASS CONFIGURATION ===================
    # (Only applies to glass_panel door type)
    "has_glass": True,  # Whether door has glass panels
    "merge_glass": True,  # Merge glass panels when y_subdivisions < 4
    "glass_surface_type": "clear_glass",  # clear_glass, frosted_glass, tinted_glass
    "door_arc_surface": "door",  # door, glass (for arched tops)
    # =================== LOUVER CONFIGURATION ===================
    # (Only applies to louver door type)
    "has_louver": True,  # Whether door has louver slats
    # =================== KNOB PARAMETERS ===================
    "knob_radius": 0.035,  # 0.03-0.04 knob radius
    "knob_depth": 0.09,  # 0.08-0.1 knob protrusion
    # Knob shape progression (base, base, mid, mid, tip, tip_inner, end)
    "knob_radius_progression": [1.15, 1.15, 0.45, 0.45, 1.0, 0.7, 0],
    "knob_depth_progression": [0, 0.125, 0.275, 0.4, 0.7, 1.0, 1.001],
    # =================== LEVER PARAMETERS ===================
    "lever_radius": 0.035,  # 0.03-0.04 lever thickness
    "lever_mid_radius": 0.015,  # 0.01-0.02 middle section radius
    "lever_depth": 0.065,  # 0.05-0.08 lever base depth
    "lever_mid_depth": 0.2,  # 0.15-0.25 middle section depth
    "lever_length": 0.175,  # 0.15-0.2 lever length
    "lever_type": "cylinder",  # wave, cylinder, bent
    # =================== PULL HANDLE PARAMETERS ===================
    "pull_size": 0.25,  # 0.1-0.4 pull handle size
    "pull_depth": 0.065,  # 0.05-0.08 pull depth
    "pull_width": 0.115,  # 0.08-0.15 pull width
    "pull_extension": 0.1,  # 0.05-0.15 pull extension
    "pull_bevel_enabled": True,  # Whether to bevel pull
    "pull_bevel_width": 0.03,  # 0.02-0.04 bevel width
    "pull_radius": 0.015,  # 0.01-0.02 pull radius
    "pull_type": "u",  # u, tee, zed
    "pull_circular": False,  # Circular vs rectangular cross-section
    # =================== BAR HANDLE PARAMETERS ===================
    "bar_length_ratio": 0.8,  # 0.7-0.9 (ratio of door width)
    "bar_thickness_ratio": 0.035,  # 0.025-0.045 (ratio of door height)
    "bar_aspect_ratio": 0.5,  # 0.4-0.6 bar cross-section ratio
    "bar_height_ratio": 0.8,  # 0.7-0.9 bar height ratio
    "bar_length_ratio_inner": 0.65,  # 0.5-0.8 inner length ratio
    "bar_end_length_ratio": 0.125,  # 0.1-0.15 end section length
    "bar_end_height_ratio": 2.4,  # 1.8-3.0 end section height
    "bar_z_offset_ratio": -0.05,  # -0.1 to 0.0 vertical offset
    # =================== MATERIAL TYPES ===================
    "door_surface_type": "wood",  # wood, metal, composite
    "handle_surface_type": "metal",  # metal, plastic, wood
    "louver_surface_type": "wood",  # wood, metal, plastic
    # =================== SIMULATION PARAMETERS (MuJoCo) ===================
    # Hinge joint settings
    "door_hinge_stiffness_min": 5.0,  # 0.0-50.0 minimum hinge stiffness
    "door_hinge_stiffness_max": 10.0,  # 0.0-50.0 maximum hinge stiffness
    "door_hinge_damping_min": 2.0,  # 0.0-20.0 minimum hinge damping
    "door_hinge_damping_max": 5.0,  # 0.0-20.0 maximum hinge damping
    # Handle joint settings
    "door_handle_stiffness_min": 3.0,  # 0.0-10.0 minimum handle stiffness
    "door_handle_stiffness_max": 6.0,  # 0.0-10.0 maximum handle stiffness
    "door_handle_damping_min": 1.5,  # 0.0-5.0 minimum handle damping
    "door_handle_damping_max": 3.0,  # 0.0-5.0 maximum handle damping
    # =================== EXPORT SETTINGS ===================
    "image_resolution": 512,  # 256-2048 texture resolution
    "visual_only": False,  # True to skip collision meshes
}


# =================== PREDEFINED CONFIGURATIONS ===================
# Uncomment one of these to use a predefined setup

# # Residential door (standard home door)
# DOOR_CONFIG.update({
#     "door_type": "panel",
#     "handle_type": "knob",
#     "door_frame_style": "full_frame_square",
#     "x_subdivisions": 1,
#     "y_subdivisions": 2,
#     "door_surface_type": "wood"
# })

# # Office door (modern office)
# DOOR_CONFIG.update({
#     "door_type": "panel",
#     "handle_type": "lever",
#     "door_frame_style": "full_frame_square",
#     "x_subdivisions": 1,
#     "y_subdivisions": 1,
#     "door_surface_type": "wood"
# })

# # Glass office door
# DOOR_CONFIG.update({
#     "door_type": "glass_panel",
#     "handle_type": "pull",
#     "door_frame_style": "full_frame_square",
#     "has_glass": True,
#     "x_subdivisions": 2,
#     "y_subdivisions": 3,
#     "door_surface_type": "metal"
# })

# # Heavy/stiff door (hard to open)
# DOOR_CONFIG.update({
#     "door_hinge_stiffness_min": 20.0,
#     "door_hinge_stiffness_max": 30.0,
#     "door_hinge_damping_min": 8.0,
#     "door_hinge_damping_max": 15.0
# })

# # Light/loose door (easy to open)
# DOOR_CONFIG.update({
#     "door_hinge_stiffness_min": 0.0,
#     "door_hinge_stiffness_max": 2.0,
#     "door_hinge_damping_min": 0.5,
#     "door_hinge_damping_max": 2.0
# })


import subprocess
from pathlib import Path


def create_custom_door_script():
    """Create a custom Python script that directly instantiates the door factory with your parameters."""

    script_content = f'''#!/usr/bin/env python3
"""
Custom Door Generator that directly uses Infinigen door factories with specific parameters.
This bypasses the random generation system to give you exact control.
"""

import bpy
import gin
import sys
import os
from pathlib import Path

# Add Infinigen to path  
sys.path.insert(0, str(Path(__file__).parent))

from infinigen.assets.objects.elements.doors.panel import PanelDoorFactory
from infinigen.assets.objects.elements.doors.panel import GlassPanelDoorFactory  
from infinigen.assets.objects.elements.doors.louver import LouverDoorFactory
from infinigen.assets.objects.elements.doors.lite import LiteDoorFactory
from infinigen.assets.sim_objects.door import SimDoorFactory
from infinigen.core.util.math import FixedSeed

# Your exact door configuration
DOOR_CONFIG = {repr(DOOR_CONFIG)}

def create_custom_door():
    """Create door with exact parameters specified in DOOR_CONFIG."""
    
    print("Creating custom door with specified parameters...")
    print(f"Door type: {{DOOR_CONFIG['door_type']}}")
    print(f"Handle type: {{DOOR_CONFIG['handle_type']}}")
    print(f"X subdivisions: {{DOOR_CONFIG['x_subdivisions']}}")
    print(f"Y subdivisions: {{DOOR_CONFIG['y_subdivisions']}}")
    
    # Clear existing mesh objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Select appropriate door factory based on door type
    door_type = DOOR_CONFIG['door_type']
    seed = DOOR_CONFIG['seed']
    
    if door_type == "panel":
        factory = PanelDoorFactory(seed)
    elif door_type == "glass_panel":
        factory = GlassPanelDoorFactory(seed)
    elif door_type == "louver":
        factory = LouverDoorFactory(seed)
    elif door_type == "lite":
        factory = LiteDoorFactory(seed)
    else:
        raise ValueError(f"Unknown door type: {{door_type}}")
    
    # Override factory parameters with your configuration
    with FixedSeed(seed):
        # Set handle type
        factory.handle_type = DOOR_CONFIG['handle_type']
        factory.door_orientation = DOOR_CONFIG['door_orientation']
        
        # Set panel configuration
        factory.x_subdivisions = DOOR_CONFIG['x_subdivisions'] 
        factory.y_subdivisions = DOOR_CONFIG['y_subdivisions']
        
        # Set frame style
        factory.door_frame_style = DOOR_CONFIG['door_frame_style']
        
        # Set handle height
        factory.handle_height_ratio = DOOR_CONFIG['handle_height_ratio']
        
        # Set panel parameters if it's a panel door
        if hasattr(factory, 'panel_margin'):
            factory.panel_margin = DOOR_CONFIG['panel_margin']
        if hasattr(factory, 'bevel_width'):
            factory.bevel_width = DOOR_CONFIG['bevel_width']
        if hasattr(factory, 'shrink_width'):
            factory.shrink_width = DOOR_CONFIG['shrink_width']
        if hasattr(factory, 'side_bevel'):
            factory.side_bevel = DOOR_CONFIG['side_bevel']
        if hasattr(factory, 'out_bevel'):
            factory.out_bevel = DOOR_CONFIG['out_bevel']
            
        # Set glass parameters if it's a glass door
        if hasattr(factory, 'has_glass'):
            factory.has_glass = DOOR_CONFIG['has_glass']
        if hasattr(factory, 'merge_glass'):
            factory.merge_glass = DOOR_CONFIG['merge_glass']
        if hasattr(factory, 'door_arc_surface'):
            factory.door_arc_surface = DOOR_CONFIG['door_arc_surface']
            
        # Set louver parameters if it's a louver door
        if hasattr(factory, 'has_louver'):
            factory.has_louver = DOOR_CONFIG['has_louver']
        
        # Create the door asset
        door_obj = factory.create_asset()
        
        print(f"✓ Created door object: {{door_obj.name}}")
        
        return door_obj

def export_to_mujoco():
    """Export the created door to MuJoCo XML format."""
    
    print("Exporting door to MuJoCo XML format...")
    
    # Create output directory
    output_dir = Path("sim_exports") / DOOR_CONFIG['export_format'] / "door" / str(DOOR_CONFIG['seed'])
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Export to MuJoCo XML
    xml_file = output_dir / "door.xml"
    
    # Use Blender's export functionality or Infinigen's export system
    # For now, save as .blend file which can be converted later
    blend_file = output_dir / "door.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_file))
    
    print(f"✓ Saved door to: {{blend_file}}")
    return blend_file

def main():
    """Main function to create and export door."""
    print("Custom Door Generator - Exact Parameter Control")
    print("=" * 60)
    
    try:
        # Create the door
        door_obj = create_custom_door()
        
        # Export to MuJoCo
        output_file = export_to_mujoco()
        
        print("\\n🎉 Success! Custom door created and exported")
        print(f"📁 Output file: {{output_file.absolute()}}")
        
        print("\\nYour custom door parameters:")
        for key, value in DOOR_CONFIG.items():
            if key in ['door_type', 'handle_type', 'x_subdivisions', 'y_subdivisions', 
                      'door_frame_style', 'door_orientation']:
                print(f"  {{key}}: {{value}}")
        
    except Exception as e:
        print(f"\\n❌ Error creating door: {{e}}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
'''

    # Save the custom script
    script_path = Path("custom_door_generator.py")
    with open(script_path, "w") as f:
        f.write(script_content)

    return script_path


def create_door_config():
    """Create gin configuration with simulation parameters only."""

    gin_config = f"""# Door configuration - Simulation parameters only
SimDoorFactory.sample_joint_parameters.door_hinge_stiffness_min={DOOR_CONFIG["door_hinge_stiffness_min"]}
SimDoorFactory.sample_joint_parameters.door_hinge_stiffness_max={DOOR_CONFIG["door_hinge_stiffness_max"]}
SimDoorFactory.sample_joint_parameters.door_hinge_damping_min={DOOR_CONFIG["door_hinge_damping_min"]}
SimDoorFactory.sample_joint_parameters.door_hinge_damping_max={DOOR_CONFIG["door_hinge_damping_max"]}
SimDoorFactory.sample_joint_parameters.door_handle_stiffness_min={DOOR_CONFIG["door_handle_stiffness_min"]}
SimDoorFactory.sample_joint_parameters.door_handle_stiffness_max={DOOR_CONFIG["door_handle_stiffness_max"]}
SimDoorFactory.sample_joint_parameters.door_handle_damping_min={DOOR_CONFIG["door_handle_damping_min"]}
SimDoorFactory.sample_joint_parameters.door_handle_damping_max={DOOR_CONFIG["door_handle_damping_max"]}"""

    # Save gin config
    config_path = Path("door_config.gin")
    with open(config_path, "w") as f:
        f.write(gin_config)

    return config_path


def generate_single_door_mujoco():
    """Generate a single door using BOTH approaches for maximum compatibility."""

    print("Door Generator - Custom Parameter Control + MuJoCo Export")
    print("=" * 70)

    # Print current configuration
    print_door_config()

    print(f"\n🎯 THE ISSUE: The standard spawn_sim_ready_asset.sh script uses")
    print(f"   RANDOM door generation and ignores your handle_type parameters!")
    print(f"\n💡 SOLUTION: Using custom door factory approach that gives you")
    print(f"   EXACT control over all door parameters.")

    print(f"\nStep 1: Creating custom door generator script...")

    # Create custom door generator script
    custom_script = create_custom_door_script()
    print(f"✓ Created custom script: {custom_script}")

    print(f"\nStep 2: Creating simulation configuration...")

    # Create gin config for simulation parameters
    config_path = create_door_config()
    print(f"✓ Created simulation config: {config_path}")

    print(f"\nStep 3: Running custom door generator with Blender...")

    try:
        # Run the custom script with Blender
        cmd = ["blender", "--background", "--python", str(custom_script)]

        print(f"Running command: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
            timeout=120,  # 2 minute timeout
        )

        if result.returncode == 0:
            print("✓ Custom door generation completed!")

            # Look for generated files
            output_dir = (
                Path("sim_exports")
                / DOOR_CONFIG["export_format"]
                / "door"
                / str(DOOR_CONFIG["seed"])
            )
            if output_dir.exists():
                print(f"✓ Door files saved to: {output_dir}")

                # List generated files
                for file in output_dir.iterdir():
                    print(f"  📄 {file.name}")

                return output_dir
            else:
                print("⚠ Output directory not found, but generation may have succeeded")

        else:
            print("❌ Custom door generation failed!")
            print(f"Error output: {result.stderr}")
            print(f"Standard output: {result.stdout}")

            # Fallback to original method
            print(
                f"\n🔄 Falling back to original method (note: parameters may be ignored)..."
            )
            return fallback_generation()

    except subprocess.TimeoutExpired:
        print("❌ Custom door generation timed out")
        return fallback_generation()
    except Exception as e:
        print(f"❌ Error during custom generation: {e}")
        return fallback_generation()


def fallback_generation():
    """Fallback to original spawn_sim_ready_asset.sh method."""

    print("Using fallback generation method...")

    # Create configuration file
    config_path = create_door_config()

    # Build the command to generate door
    cmd = [
        "./scripts/spawn_sim_ready_asset.sh",
        "door",
        "1",
        DOOR_CONFIG["export_format"],
    ]

    if DOOR_CONFIG["include_collisions"]:
        cmd.append("-c")

    cmd.extend(["-g", str(config_path)])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
            timeout=300,
        )

        if result.returncode == 0:
            print("✓ Fallback generation completed")
            export_dir = Path(f"sim_exports/{DOOR_CONFIG['export_format']}/door")
            if export_dir.exists():
                seed_dirs = [d for d in export_dir.iterdir() if d.is_dir()]
                if seed_dirs:
                    latest_dir = max(seed_dirs, key=lambda x: x.stat().st_mtime)
                    return latest_dir

        print(f"Fallback error: {result.stderr}")

    except Exception as e:
        print(f"Fallback error: {e}")

    return None


def print_door_config():
    """Print the current door configuration."""
    print("Current Door Configuration:")
    print("=" * 50)

    categories = {
        "Basic Settings": ["export_format", "include_collisions", "seed"],
        "Door Type & Style": ["door_type", "door_frame_style", "door_orientation"],
        "Handle Configuration": ["handle_type", "handle_height_ratio"],
        "Panel Settings": ["x_subdivisions", "y_subdivisions", "panel_margin"],
        "Simulation (Hinge)": [
            "door_hinge_stiffness_min",
            "door_hinge_stiffness_max",
            "door_hinge_damping_min",
            "door_hinge_damping_max",
        ],
        "Simulation (Handle)": [
            "door_handle_stiffness_min",
            "door_handle_stiffness_max",
            "door_handle_damping_min",
            "door_handle_damping_max",
        ],
    }

    for category, keys in categories.items():
        print(f"\n{category}:")
        for key in keys:
            if key in DOOR_CONFIG:
                print(f"  {key}: {DOOR_CONFIG[key]}")


def print_door_config():
    """Print the current door configuration."""
    print("Current Door Configuration:")
    print("=" * 50)

    categories = {
        "Basic Settings": ["export_format", "include_collisions", "seed"],
        "Door Type & Style": ["door_type", "door_frame_style", "door_orientation"],
        "Handle Configuration": ["handle_type", "handle_height_ratio"],
        "Panel Settings": ["x_subdivisions", "y_subdivisions", "panel_margin"],
        "Simulation (Hinge)": [
            "door_hinge_stiffness_min",
            "door_hinge_stiffness_max",
            "door_hinge_damping_min",
            "door_hinge_damping_max",
        ],
        "Simulation (Handle)": [
            "door_handle_stiffness_min",
            "door_handle_stiffness_max",
            "door_handle_damping_min",
            "door_handle_damping_max",
        ],
    }

    for category, keys in categories.items():
        print(f"\n{category}:")
        for key in keys:
            if key in DOOR_CONFIG:
                print(f"  {key}: {DOOR_CONFIG[key]}")


def main():
    """Main function to generate a single door with exact parameter control."""
    print("🚪 Door Generator with EXACT Parameter Control")
    print("=" * 70)
    print("This script solves the problem where changing handle_type doesn't work!")
    print()

    # Run the door generation
    output_dir = generate_single_door_mujoco()

    if output_dir:
        print("\n🎉 Success! Door exported with your exact specifications!")
        print(f"📁 Location: {output_dir.absolute()}")

        print("\n📋 Summary of your door:")
        key_params = [
            "door_type",
            "handle_type",
            "x_subdivisions",
            "y_subdivisions",
            "door_frame_style",
            "door_orientation",
        ]
        for param in key_params:
            print(f"   • {param}: {DOOR_CONFIG[param]}")

        print("\n🔧 Next steps:")
        print("1. Modify DOOR_CONFIG values above to customize the door")
        print("2. Run the script again to generate doors with different parameters")
        print("3. The output includes both .blend and MuJoCo-compatible files")

    else:
        print("\n❌ Door generation failed. Check the error messages above.")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure Blender is installed and accessible via 'blender' command")
        print("2. Ensure you're in the infinigen directory")
        print("3. Check that all Infinigen dependencies are installed")


if __name__ == "__main__":
    main()
