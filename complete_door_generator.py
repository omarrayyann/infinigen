"""
Complete door generator and MuJoCo exporter script.
This script generates doors with exact parameters using Infinigen/Blender
and exports them to MuJoCo format in a single consolidated workflow.

Usage: python complete_door_generator.py
"""

import os
import random
import subprocess
import sys
from pathlib import Path

from tqdm import tqdm

NUM_DOORS = 2
RANDOMIZE_PARAMETERS = True

DOOR_TYPE = "louver"

HANDLE_TYPE = "pull"

X_SUBDIVISIONS = 1

Y_SUBDIVISIONS = 2

SEED = 15

DOOR_TYPES = ["panel", "glass_panel", "louver", "lite"]

HANDLE_TYPES = [
    "knob",
    "pull",
]

X_SUBDIVISIONS_RANGE = (1, 3)

Y_SUBDIVISIONS_RANGE = (1, 4)

SEED_RANGE = (1, 1000)

EXPORT_FORMAT = "mjcf"
BLENDER_PATH = "/Applications/Blender.app/Contents/MacOS/Blender"
INFINIGEN_PATH = "/Users/omarrayyann/Documents/infinigen"


def generate_door_parameters(door_index=0):
    """Generate door parameters based on configuration"""
    if RANDOMIZE_PARAMETERS:
        door_type = random.choice(DOOR_TYPES)
        handle_type = random.choice(HANDLE_TYPES)
        x_subdivisions = random.randint(*X_SUBDIVISIONS_RANGE)
        y_subdivisions = random.randint(*Y_SUBDIVISIONS_RANGE)
        seed = random.randint(*SEED_RANGE)
    else:
        door_type = DOOR_TYPE
        handle_type = HANDLE_TYPE
        x_subdivisions = X_SUBDIVISIONS
        y_subdivisions = Y_SUBDIVISIONS
        seed = SEED

    output_dir = f"sim_exports/{EXPORT_FORMAT}/doors/door_{door_index}"

    return {
        "door_type": door_type,
        "handle_type": handle_type,
        "x_subdivisions": x_subdivisions,
        "y_subdivisions": y_subdivisions,
        "seed": seed,
        "output_dir": output_dir,
    }


def setup_python_paths():
    if INFINIGEN_PATH not in sys.path:
        sys.path.insert(0, INFINIGEN_PATH)

    conda_site_packages = "/opt/anaconda3/envs/infinigen/lib/python3.11/site-packages"
    if os.path.exists(conda_site_packages) and conda_site_packages not in sys.path:
        sys.path.insert(0, conda_site_packages)

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


def check_blender_environment():
    try:
        import bpy

        return True
    except ImportError:
        return False


def create_exact_door(door_params):
    try:
        import bpy

        from infinigen.assets.objects.elements.doors.panel import PanelDoorFactory
        from infinigen.assets.objects.elements.doors.panel import GlassPanelDoorFactory
        from infinigen.assets.objects.elements.doors.louver import LouverDoorFactory
        from infinigen.assets.objects.elements.doors.lite import LiteDoorFactory
    except ImportError:
        return False

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    factory_map = {
        "panel": PanelDoorFactory,
        "glass_panel": GlassPanelDoorFactory,
        "louver": LouverDoorFactory,
        "lite": LiteDoorFactory,
    }

    if door_params["door_type"] not in factory_map:
        raise ValueError(f"Invalid door_type: {door_params['door_type']}")

    factory_class = factory_map[door_params["door_type"]]
    factory = factory_class(factory_seed=door_params["seed"])

    factory.handle_type = door_params["handle_type"]
    factory.x_subdivisions = door_params["x_subdivisions"]
    factory.y_subdivisions = door_params["y_subdivisions"]

    door_obj = factory.create_asset()

    if door_obj is None:
        raise RuntimeError("Failed to create door asset")

    blend_file = f"door_{door_params['door_type']}_{door_params['handle_type']}_{door_params['seed']}.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_file)

    return True


def print_banner(door_params):
    """Print door configuration banner"""
    pass


def patch_door_factory():
    """Patch the random_door_factory function to return our exact factory"""

    try:
        from infinigen.assets.objects.elements.doors.panel import PanelDoorFactory
        from infinigen.assets.objects.elements.doors.panel import GlassPanelDoorFactory
        from infinigen.assets.objects.elements.doors.louver import LouverDoorFactory
        from infinigen.assets.objects.elements.doors.lite import LiteDoorFactory
        from infinigen.assets.sim_objects import door as door_module
    except ImportError:
        return False

    factory_map = {
        "panel": PanelDoorFactory,
        "glass_panel": GlassPanelDoorFactory,
        "louver": LouverDoorFactory,
        "lite": LiteDoorFactory,
    }

    def patched_random_door_factory():
        """Patched version that returns our exact door factory with forced parameters"""

        factory_class = factory_map[DOOR_TYPE]

        def create_exact_factory(factory_seed, coarse=False, constants=None):
            factory = factory_class(factory_seed, coarse)

            factory.handle_type = HANDLE_TYPE
            if hasattr(factory, "x_subdivisions"):
                factory.x_subdivisions = X_SUBDIVISIONS
            if hasattr(factory, "y_subdivisions"):
                factory.y_subdivisions = Y_SUBDIVISIONS

            return factory

        return create_exact_factory

    door_module.random_door_factory = patched_random_door_factory
    return True


def export_to_mujoco(door_params):
    """Export the generated door to MuJoCo format using subprocess with clean environment"""

    Path(door_params["output_dir"]).mkdir(parents=True, exist_ok=True)

    export_script_content = f'''

import sys
import os
from pathlib import Path

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
    sys.exit(1)

factory_map = {{
    'panel': PanelDoorFactory,
    'glass_panel': GlassPanelDoorFactory,
    'louver': LouverDoorFactory,
    'lite': LiteDoorFactory
}}

def patched_random_door_factory():
    """Patched version that returns our exact door factory"""
    
    factory_class = factory_map["{door_params["door_type"]}"]
    
    def create_exact_factory(factory_seed, coarse=False, constants=None):
        factory = factory_class(factory_seed, coarse)
        
        factory.handle_type = "{door_params["handle_type"]}"
        if hasattr(factory, 'x_subdivisions'):
            factory.x_subdivisions = {door_params["x_subdivisions"]}
        if hasattr(factory, 'y_subdivisions'):
            factory.y_subdivisions = {door_params["y_subdivisions"]}
            
        return factory
    
    return create_exact_factory

door_module.random_door_factory = patched_random_door_factory

try:    
    export_path, semantic_mapping = sf.spawn_simready(
        name="door",
        seed={door_params["seed"]},
        exporter="{EXPORT_FORMAT}",
        export_dir=Path("{door_params["output_dir"]}").parent.parent,
        visual_only=True
    )
    
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)
'''

    export_script_path = "/tmp/mujoco_export_script.py"
    with open(export_script_path, "w") as f:
        f.write(export_script_content)

    try:
        result = subprocess.run(
            ["/opt/anaconda3/envs/infinigen/bin/python", export_script_path],
            capture_output=True,
            text=True,
            cwd=INFINIGEN_PATH,
        )

        if result.returncode == 0:
            import re

            export_match = re.search(r"✅ Exported to: (.+)", result.stdout)
            if export_match:
                actual_export_path = Path(export_match.group(1))
                actual_export_dir = actual_export_path.parent

                import shutil

                if actual_export_dir.exists():
                    Path(door_params["output_dir"]).mkdir(parents=True, exist_ok=True)

                    for item in actual_export_dir.rglob("*"):
                        if item.is_file():
                            rel_path = item.relative_to(actual_export_dir)
                            target_path = Path(door_params["output_dir"]) / rel_path
                            target_path.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(item, target_path)

            return True
        else:
            return False

    finally:
        if os.path.exists(export_script_path):
            os.remove(export_script_path)


def verify_output(door_params):
    """Verify that the output files were created successfully"""

    door_xml_path = Path(door_params["output_dir"]) / "door.xml"

    if door_xml_path.exists():
        try:
            with open(door_xml_path, "r") as f:
                f.read()
        except Exception:
            pass

        visual_assets_dir = Path(door_params["output_dir"]) / "assets" / "visual"
        if visual_assets_dir.exists():
            for asset_file in visual_assets_dir.glob("*"):
                if asset_file.suffix in [".obj", ".mtl"]:
                    pass

        return True
    else:
        return False


def print_completion_summary(door_params):
    """Print the completion summary"""
    pass


def print_usage_instructions():
    """Print usage instructions"""
    pass


def run_blender_generation(door_params):
    """Run Blender door generation using subprocess"""

    if not os.path.exists(BLENDER_PATH):
        return False

    temp_script_content = f'''

import sys
import os
from pathlib import Path

current_dir = "{os.path.dirname(os.path.abspath(__file__))}"
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

DOOR_TYPE = "{door_params["door_type"]}"
HANDLE_TYPE = "{door_params["handle_type"]}"
X_SUBDIVISIONS = {door_params["x_subdivisions"]}
Y_SUBDIVISIONS = {door_params["y_subdivisions"]}
SEED = {door_params["seed"]}
OUTPUT_DIR = "{door_params["output_dir"]}"

exec(open("{__file__}").read())
'''

    temp_script_path = Path("/tmp") / f"temp_door_gen_{door_params['seed']}.py"
    with open(temp_script_path, "w") as f:
        f.write(temp_script_content)

    original_cwd = os.getcwd()
    os.chdir(INFINIGEN_PATH)

    try:
        result = subprocess.run(
            [BLENDER_PATH, "--background", "--python", str(temp_script_path)],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            return True
        else:
            if "🎉 Door generation successful!" in result.stdout:
                return True
            else:
                return False

    finally:
        os.chdir(original_cwd)

        if temp_script_path.exists():
            temp_script_path.unlink()


def main():
    """Main execution function"""

    setup_python_paths()

    if check_blender_environment():
        try:
            door_params = generate_door_parameters(0)
            success = create_exact_door(door_params)
            if not success:
                sys.exit(1)
        except Exception:
            import traceback

            traceback.print_exc()
            sys.exit(1)
    else:
        try:
            generated_doors = []
            for door_idx in tqdm(
                range(NUM_DOORS), desc="Generating doors", unit="door"
            ):
                door_params = generate_door_parameters(door_idx)

                if not run_blender_generation(door_params):
                    return False

                if not export_to_mujoco(door_params):
                    return False

                if not verify_output(door_params):
                    return False

                generated_doors.append(door_params["output_dir"])

            print(f"\nGenerated {NUM_DOORS} doors:")
            for i, output_dir in enumerate(generated_doors):
                print(f"  Door {i + 1}: {output_dir}")

            return True

        except Exception:
            import traceback

            traceback.print_exc()
            return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
