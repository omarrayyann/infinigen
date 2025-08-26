#!/usr/bin/env python3
"""
Complete Door Generation & MuJoCo Export Script
==============================================
This script generates doors with EXACT parameters and exports to MuJoCo format.
All functionality is contained in a single Python file without external scripts.

Usage:
    python complete_door_generator.py

Or modify the configuration variables below and run.
"""

import os
import subprocess
import sys
from pathlib import Path

# =============================================================================
# DOOR CONFIGURATION - MODIFY THESE PARAMETERS
# =============================================================================

# Basic door appearance
DOOR_TYPE = "louver"  # Options: panel, glass_panel, louver, lite
HANDLE_TYPE = "pull"  # Options: knob, lever, pull, bar, none
X_SUBDIVISIONS = 1  # Horizontal panel subdivisions (integer)
Y_SUBDIVISIONS = 2  # Vertical panel subdivisions (integer)
SEED = 15  # Seed for consistent generation

# Output settings
EXPORT_FORMAT = "mjcf"  # MuJoCo export format
OUTPUT_DIR = f"sim_exports/{EXPORT_FORMAT}/door/{SEED}"

# Paths
BLENDER_PATH = "/Applications/Blender.app/Contents/MacOS/Blender"
INFINIGEN_PATH = "/Users/omarrayyann/Documents/infinigen"

# =============================================================================
# SETUP AND UTILITY FUNCTIONS
# =============================================================================


def setup_python_paths():
    """Setup Python paths for Infinigen and conda environment"""
    # Add infinigen to Python path
    if INFINIGEN_PATH not in sys.path:
        sys.path.insert(0, INFINIGEN_PATH)

    # Add conda environment site-packages
    conda_site_packages = "/opt/anaconda3/envs/infinigen/lib/python3.11/site-packages"
    if os.path.exists(conda_site_packages) and conda_site_packages not in sys.path:
        sys.path.insert(0, conda_site_packages)

    # Remove any conflicting numpy paths
    paths_to_remove = []
    for path in sys.path:
        if (
            "numpy" in path.lower()
            and "site-packages" not in path
            and "infinigen" not in path
        ):
            paths_to_remove.append(path)

    for path in paths_to_remove:
        if path in sys.path:
            sys.path.remove(path)


def print_banner():
    """Print the script banner with configuration"""
    print("=" * 62)
    print("🚪 EXACT DOOR GENERATION & MUJOCO EXPORT")
    print("=" * 62)
    print("Door Configuration:")
    print(f"  • Type: {DOOR_TYPE}")
    print(f"  • Handle: {HANDLE_TYPE}")
    print(f"  • Subdivisions: {X_SUBDIVISIONS}x{Y_SUBDIVISIONS}")
    print(f"  • Seed: {SEED}")
    print(f"  • Output: {OUTPUT_DIR}")
    print("=" * 62)


def check_blender_environment():
    """Check if we're running inside Blender"""
    try:
        import bpy  # noqa: F401

        return True
    except ImportError:
        return False


# =============================================================================
# BLENDER DOOR GENERATION (INLINE)
# =============================================================================


def create_exact_door():
    """Generate door with exact parameters (runs inside Blender)"""

    try:
        import bpy
        from infinigen.assets.objects.elements.doors.panel import PanelDoorFactory
        from infinigen.assets.objects.elements.doors.panel import GlassPanelDoorFactory
        from infinigen.assets.objects.elements.doors.louver import LouverDoorFactory
        from infinigen.assets.objects.elements.doors.lite import LiteDoorFactory
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

    print("🚪 Generating door with exact parameters:")
    print(f"  • Door type: {DOOR_TYPE}")
    print(f"  • Handle type: {HANDLE_TYPE}")
    print(f"  • X subdivisions: {X_SUBDIVISIONS}")
    print(f"  • Y subdivisions: {Y_SUBDIVISIONS}")
    print(f"  • Seed: {SEED}")

    # Clear existing objects
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    # Factory selection
    factory_map = {
        "panel": PanelDoorFactory,
        "glass_panel": GlassPanelDoorFactory,
        "louver": LouverDoorFactory,
        "lite": LiteDoorFactory,
    }

    if DOOR_TYPE not in factory_map:
        raise ValueError(f"Invalid door_type: {DOOR_TYPE}")

    # Create factory
    factory_class = factory_map[DOOR_TYPE]
    factory = factory_class(factory_seed=SEED)

    print(f"📦 Created {factory_class.__name__}")

    # FORCE exact parameters (override random generation)
    print("🔧 Forcing exact parameters...")
    print(f"  Before: handle_type='{getattr(factory, 'handle_type', 'unknown')}'")
    print(f"  Before: x_subdivisions={getattr(factory, 'x_subdivisions', 'unknown')}")
    print(f"  Before: y_subdivisions={getattr(factory, 'y_subdivisions', 'unknown')}")

    factory.handle_type = HANDLE_TYPE
    factory.x_subdivisions = X_SUBDIVISIONS
    factory.y_subdivisions = Y_SUBDIVISIONS

    print(f"  After: handle_type='{factory.handle_type}'")
    print(f"  After: x_subdivisions={factory.x_subdivisions}")
    print(f"  After: y_subdivisions={factory.y_subdivisions}")

    # Generate door
    print("🏗️  Generating door asset...")
    door_obj = factory.create_asset()

    if door_obj is None:
        raise RuntimeError("Failed to create door asset")

    print(f"✅ Door created: {door_obj.name}")

    # Save blend file
    blend_file = f"door_{DOOR_TYPE}_{HANDLE_TYPE}_{SEED}.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_file)
    print(f"💾 Saved: {blend_file}")

    return True


# =============================================================================
# MUJOCO EXPORT (INLINE)
# =============================================================================


def patch_door_factory():
    """Patch the random_door_factory function to return our exact factory"""

    try:
        from infinigen.assets.objects.elements.doors.panel import PanelDoorFactory
        from infinigen.assets.objects.elements.doors.panel import GlassPanelDoorFactory
        from infinigen.assets.objects.elements.doors.louver import LouverDoorFactory
        from infinigen.assets.objects.elements.doors.lite import LiteDoorFactory
        from infinigen.assets.sim_objects import door as door_module
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

    # Factory mapping
    factory_map = {
        "panel": PanelDoorFactory,
        "glass_panel": GlassPanelDoorFactory,
        "louver": LouverDoorFactory,
        "lite": LiteDoorFactory,
    }

    def patched_random_door_factory():
        """Patched version that returns our exact door factory with forced parameters"""

        print(f"🔧 PATCHED random_door_factory called - returning {DOOR_TYPE} factory")

        # Select our exact factory
        factory_class = factory_map[DOOR_TYPE]

        def create_exact_factory(factory_seed, coarse=False, constants=None):
            # Create the factory
            factory = factory_class(factory_seed, coarse)

            # Force our exact parameters
            print(f"🔧 Forcing exact parameters on {factory_class.__name__}:")
            print(f"  • handle_type: {HANDLE_TYPE}")
            print(f"  • x_subdivisions: {X_SUBDIVISIONS}")
            print(f"  • y_subdivisions: {Y_SUBDIVISIONS}")

            factory.handle_type = HANDLE_TYPE
            if hasattr(factory, "x_subdivisions"):
                factory.x_subdivisions = X_SUBDIVISIONS
            if hasattr(factory, "y_subdivisions"):
                factory.y_subdivisions = Y_SUBDIVISIONS

            print(f"  ✅ Patched {factory_class.__name__} successfully")
            return factory

        return create_exact_factory

    # Apply the monkey patch
    door_module.random_door_factory = patched_random_door_factory
    print("✅ Applied door factory patch")
    return True


def export_to_mujoco():
    """Export the generated door to MuJoCo format using subprocess with clean environment"""

    print("\n🚀 Exporting to MuJoCo format with exact parameters...")

    # Create output directory
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    # Create a simple export script that will run in clean environment
    export_script_content = f'''#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add infinigen to Python path
infinigen_path = "{INFINIGEN_PATH}"
if infinigen_path not in sys.path:
    sys.path.insert(0, infinigen_path)

try:
    from infinigen.core.sim import sim_factory as sf
    from infinigen.assets.objects.elements.doors.panel import PanelDoorFactory
    from infinigen.assets.objects.elements.doors.panel import GlassPanelDoorFactory
    from infinigen.assets.objects.elements.doors.louver import LouverDoorFactory
    from infinigen.assets.objects.elements.doors.lite import LiteDoorFactory
    from infinigen.assets.sim_objects import door as door_module
except ImportError as e:
    print(f"❌ Import error: {{e}}")
    sys.exit(1)

# Factory mapping
factory_map = {{
    'panel': PanelDoorFactory,
    'glass_panel': GlassPanelDoorFactory,
    'louver': LouverDoorFactory,
    'lite': LiteDoorFactory
}}

def patched_random_door_factory():
    """Patched version that returns our exact door factory"""
    print(f"🔧 PATCHED random_door_factory called - returning {DOOR_TYPE} factory")
    
    factory_class = factory_map["{DOOR_TYPE}"]
    
    def create_exact_factory(factory_seed, coarse=False, constants=None):
        factory = factory_class(factory_seed, coarse)
        
        print(f"🔧 Forcing exact parameters on {{factory_class.__name__}}:")
        print(f"  • handle_type: {HANDLE_TYPE}")
        print(f"  • x_subdivisions: {X_SUBDIVISIONS}")
        print(f"  • y_subdivisions: {Y_SUBDIVISIONS}")
        
        factory.handle_type = "{HANDLE_TYPE}"
        if hasattr(factory, 'x_subdivisions'):
            factory.x_subdivisions = {X_SUBDIVISIONS}
        if hasattr(factory, 'y_subdivisions'):
            factory.y_subdivisions = {Y_SUBDIVISIONS}
            
        print(f"  ✅ Patched {{factory_class.__name__}} successfully")
        return factory
    
    return create_exact_factory

# Apply the monkey patch
door_module.random_door_factory = patched_random_door_factory
print("✅ Applied door factory patch")

try:
    print("🚀 Running door export...")
    
    export_path, semantic_mapping = sf.spawn_simready(
        name="door",
        seed={SEED},
        exporter="{EXPORT_FORMAT}",
        export_dir=Path("{OUTPUT_DIR}").parent.parent.parent,
        visual_only=True
    )
    
    print(f"✅ Exported to: {{export_path}}")
    print("🎉 MuJoCo export successful!")
    
except Exception as e:
    print(f"💥 Export error: {{e}}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
'''

    # Write the export script
    export_script_path = "/tmp/mujoco_export_script.py"
    with open(export_script_path, "w") as f:
        f.write(export_script_content)

    try:
        # Run the export script using conda environment from infinigen directory
        result = subprocess.run(
            ["/opt/anaconda3/envs/infinigen/bin/python", export_script_path],
            capture_output=True,
            text=True,
            cwd=INFINIGEN_PATH,
        )

        if result.returncode == 0:
            print("✅ MuJoCo export completed successfully")
            print(result.stdout)
            return True
        else:
            print("❌ MuJoCo export failed")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False

    finally:
        # Cleanup export script
        if os.path.exists(export_script_path):
            os.remove(export_script_path)


# =============================================================================
# OUTPUT VERIFICATION AND SUMMARY
# =============================================================================


def verify_output():
    """Verify that the output files were created successfully"""

    print("\n🔍 Verifying output...")

    door_xml_path = Path(OUTPUT_DIR) / "door.xml"

    if door_xml_path.exists():
        print(f"✅ Found: {door_xml_path}")

        # Check for handle components in XML
        try:
            with open(door_xml_path, "r") as f:
                xml_content = f.read()
                if "handle_" in xml_content:
                    print("✅ Handle components found in XML")
                else:
                    print("⚠️  No handle components found in XML")
        except Exception as e:
            print(f"⚠️  Could not read XML file: {e}")

        # List visual assets
        visual_assets_dir = Path(OUTPUT_DIR) / "assets" / "visual"
        if visual_assets_dir.exists():
            print("✅ Visual assets:")
            for asset_file in visual_assets_dir.glob("*"):
                if asset_file.suffix in [".obj", ".mtl"]:
                    print(f"     {asset_file.name}")

        return True
    else:
        print(f"❌ door.xml not found in {OUTPUT_DIR}")
        return False


def print_completion_summary():
    """Print the completion summary"""

    print("\n" + "=" * 62)
    print("🎉 DOOR GENERATION & EXPORT COMPLETE!")
    print("=" * 62)
    print("Generated door with EXACT parameters:")
    print(f"  ✅ Door type: {DOOR_TYPE}")
    print(f"  ✅ Handle type: {HANDLE_TYPE}")
    print(f"  ✅ Subdivisions: {X_SUBDIVISIONS}x{Y_SUBDIVISIONS}")
    print(f"  ✅ Seed: {SEED}")
    print()
    print("Output files:")
    print(f"  📁 Directory: {OUTPUT_DIR}")
    print(f"  📄 MuJoCo XML: {OUTPUT_DIR}/door.xml")
    print(f"  🎨 Visual assets: {OUTPUT_DIR}/assets/visual/")
    print(f"  📊 Metadata: {OUTPUT_DIR}/metadata.json")
    print()
    print("🚀 Your door is ready for MuJoCo simulation!")
    print("=" * 62)


def print_usage_instructions():
    """Print usage instructions"""

    print("\n💡 To generate different doors, modify these variables at the top:")
    print('   DOOR_TYPE = "panel"        # panel, glass_panel, louver, lite')
    print('   HANDLE_TYPE = "bar"       # knob, lever, pull, bar, none')
    print("   X_SUBDIVISIONS = 1          # horizontal subdivisions")
    print("   Y_SUBDIVISIONS = 2          # vertical subdivisions")
    print("   SEED = 32                 # seed for consistency")
    print()
    print(f"Then run: python {__file__}")


# =============================================================================
# WORKFLOW EXECUTION
# =============================================================================


def run_blender_generation():
    """Run Blender door generation using subprocess"""

    if not os.path.exists(BLENDER_PATH):
        print(f"❌ Blender not found at: {BLENDER_PATH}")
        return False

    print("\n🏗️  Generating door with Blender...")

    # Change to infinigen directory
    original_cwd = os.getcwd()
    os.chdir(INFINIGEN_PATH)

    try:
        # Run Blender with this script (it will detect Blender environment and run door generation)
        result = subprocess.run(
            [BLENDER_PATH, "--background", "--python", __file__],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("✅ Door generation completed successfully")
            print(result.stdout)
            return True
        else:
            # Check if the generation actually succeeded by looking for success message
            # Blender often exits with non-zero code even on success due to warnings
            if "🎉 Door generation successful!" in result.stdout:
                print(
                    "✅ Door generation completed successfully (Blender had warnings but generation succeeded)"
                )
                print(result.stdout)
                if result.stderr:
                    print("ℹ️  Blender warnings (these are usually harmless):")
                    print(
                        result.stderr[:500] + "..."
                        if len(result.stderr) > 500
                        else result.stderr
                    )
                return True
            else:
                print("❌ Door generation failed")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                return False

    finally:
        # Return to original directory
        os.chdir(original_cwd)


# =============================================================================
# MAIN EXECUTION
# =============================================================================


def main():
    """Main execution function"""

    # Setup Python paths
    setup_python_paths()

    # Check if we're running inside Blender
    if check_blender_environment():
        # We're inside Blender - run the door generation
        print("🔧 Running inside Blender environment")
        try:
            success = create_exact_door()
            if success:
                print("\n🎉 Door generation successful!")
            else:
                print("\n❌ Door generation failed!")
                sys.exit(1)
        except Exception as e:
            print(f"\n💥 Error: {e}")
            import traceback

            traceback.print_exc()
            sys.exit(1)
    else:
        # We're in regular Python - run the full workflow
        try:
            # Print banner
            print_banner()

            # Step 1: Generate door with Blender
            if not run_blender_generation():
                print("❌ Failed at door generation step")
                return False

            # Step 2: Export to MuJoCo
            if not export_to_mujoco():
                print("❌ Failed at MuJoCo export step")
                return False

            # Step 3: Verify output
            if not verify_output():
                print("❌ Failed at output verification step")
                return False

            # Print completion summary
            print_completion_summary()
            print_usage_instructions()

            return True

        except Exception as e:
            print(f"\n💥 Unexpected error: {e}")
            import traceback

            traceback.print_exc()
            return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
