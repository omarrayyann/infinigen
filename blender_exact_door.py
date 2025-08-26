#!/usr/bin/env python3
"""
Blender-Compatible Exact Door Generator
This version works with Blender's built-in Python environment
"""

import sys
import os

# Add infinigen to Blender's Python path
infinigen_path = "/Users/omarrayyann/Documents/infinigen"
if infinigen_path not in sys.path:
    sys.path.insert(0, infinigen_path)

# Also add conda environment site-packages to get gin-config
conda_site_packages = "/opt/anaconda3/envs/infinigen/lib/python3.11/site-packages"
if conda_site_packages not in sys.path:
    sys.path.insert(0, conda_site_packages)

print("🐍 Python path configured for Blender")
print(f"📦 Infinigen path: {infinigen_path}")
print(f"📦 Conda packages: {conda_site_packages}")

try:
    import bpy

    print("✅ Blender Python (bpy) loaded successfully")
except ImportError:
    print("❌ Not running in Blender - bpy not available")
    sys.exit(1)

try:
    # Test gin import
    import gin

    print("✅ gin-config loaded successfully")
except ImportError as e:
    print(f"❌ gin-config import failed: {e}")
    print("Installing gin-config in Blender's Python...")

    # Try to install gin-config for Blender's Python
    import subprocess

    blender_python = sys.executable
    try:
        subprocess.check_call([blender_python, "-m", "pip", "install", "gin-config"])
        import gin

        print("✅ gin-config installed and loaded")
    except Exception as install_error:
        print(f"❌ Could not install gin-config: {install_error}")
        print("Please install gin-config manually for Blender's Python")
        sys.exit(1)

# Now import Infinigen door factories
try:
    from infinigen.assets.objects.elements.doors.panel import PanelDoorFactory
    from infinigen.assets.objects.elements.doors.panel import GlassPanelDoorFactory
    from infinigen.assets.objects.elements.doors.louver import LouverDoorFactory
    from infinigen.assets.objects.elements.doors.lite import LiteDoorFactory

    print("✅ Infinigen door factories loaded successfully")
except ImportError as e:
    print(f"❌ Could not load Infinigen door factories: {e}")
    sys.exit(1)


def create_exact_door(
    door_type="panel", handle_type="lever", x_subdivisions=1, y_subdivisions=2, seed=42
):
    """
    Create a door with EXACT specified parameters using Blender.

    Args:
        door_type: 'panel', 'glass_panel', 'louver', or 'lite'
        handle_type: 'lever', 'knob', 'pull', 'bar', or 'none'
        x_subdivisions: Number of horizontal subdivisions (integer)
        y_subdivisions: Number of vertical subdivisions (integer)
        seed: Fixed seed for consistent results

    Returns:
        Blender object of the created door
    """

    print("\n🚪 Creating door with EXACT parameters:")
    print(f"  • Door type: {door_type}")
    print(f"  • Handle type: {handle_type}")
    print(f"  • X subdivisions: {x_subdivisions}")
    print(f"  • Y subdivisions: {y_subdivisions}")
    print(f"  • Seed: {seed}")

    # Clear existing objects
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    print("🧹 Cleared existing objects")

    # Select the factory class based on door type
    factory_map = {
        "panel": PanelDoorFactory,
        "glass_panel": GlassPanelDoorFactory,
        "louver": LouverDoorFactory,
        "lite": LiteDoorFactory,
    }

    if door_type not in factory_map:
        raise ValueError(
            f"Unknown door_type '{door_type}'. Valid options: {list(factory_map.keys())}"
        )

    # Create factory with fixed seed
    factory_class = factory_map[door_type]
    print(f"📦 Creating {factory_class.__name__} with seed {seed}")

    try:
        factory = factory_class(factory_seed=seed)
        print(f"✅ Factory created successfully")
    except Exception as e:
        print(f"❌ Factory creation failed: {e}")
        raise

    # FORCE exact parameters (this overrides the random generation!)
    print("🔧 Forcing exact parameters...")
    print(f"  Before: handle_type='{getattr(factory, 'handle_type', 'unknown')}'")
    print(f"  Before: x_subdivisions={getattr(factory, 'x_subdivisions', 'unknown')}")
    print(f"  Before: y_subdivisions={getattr(factory, 'y_subdivisions', 'unknown')}")

    factory.handle_type = handle_type
    factory.x_subdivisions = x_subdivisions
    factory.y_subdivisions = y_subdivisions

    print(f"  After: handle_type='{factory.handle_type}'")
    print(f"  After: x_subdivisions={factory.x_subdivisions}")
    print(f"  After: y_subdivisions={factory.y_subdivisions}")

    # Generate the door asset
    print("🏗️  Generating door asset...")
    try:
        door_obj = factory.create_asset()

        if door_obj is None:
            raise RuntimeError("create_asset() returned None")

        print(f"✅ Door created successfully: {door_obj.name}")
        return door_obj

    except Exception as e:
        print(f"❌ Door creation failed: {e}")
        import traceback

        traceback.print_exc()
        raise


def save_door_blend(filename="exact_door.blend"):
    """Save the current scene to a blend file"""
    bpy.ops.wm.save_as_mainfile(filepath=filename)
    print(f"💾 Saved to: {filename}")


def main():
    """Generate door with your exact specifications"""

    # YOUR EXACT SPECIFICATIONS:
    DOOR_CONFIG = {
        "door_type": "panel",  # panel, glass_panel, louver, lite
        "handle_type": "knob",  # lever, knob, pull, bar, none
        "x_subdivisions": 1,  # horizontal subdivisions
        "y_subdivisions": 2,  # vertical subdivisions
        "seed": 42,  # fixed seed for consistency
    }

    print("=" * 60)
    print("🎯 EXACT DOOR PARAMETER CONTROL")
    print("=" * 60)
    print("This script bypasses SimDoorFactory.random_door_factory()")
    print("to give you EXACT control over all door parameters.")

    try:
        # Create the door with your exact specifications
        door = create_exact_door(**DOOR_CONFIG)

        # Save the result
        save_door_blend()

        print("\n" + "=" * 60)
        print("🎉 SUCCESS!")
        print("=" * 60)
        print("Your door has been created with EXACT parameters:")
        print(f"  ✅ Door type: {DOOR_CONFIG['door_type']} (NOT random)")
        print(f"  ✅ Handle type: {DOOR_CONFIG['handle_type']} (NOT random)")
        print(f"  ✅ X subdivisions: {DOOR_CONFIG['x_subdivisions']} (NOT random)")
        print(f"  ✅ Y subdivisions: {DOOR_CONFIG['y_subdivisions']} (NOT random)")
        print("\n📁 Output file: exact_door.blend")
        print("🚀 The door is now ready for export to simulation!")

        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
    else:
        print("\n🎊 Door generation completed successfully!")
