#!/bin/bash

# =============================================================================
# COMPLETE DOOR GENERATION & MUJOCO EXPORT SCRIPT
# =============================================================================
# This script generates doors with EXACT parameters and exports to MuJoCo format
# All parameters are hardcoded below - modify them as needed
# =============================================================================

set -e  # Exit on any error

# =============================================================================
# DOOR CONFIGURATION - MODIFY THESE PARAMETERS
# =============================================================================

# Basic door appearance
DOOR_TYPE="panel"           # Options: panel, glass_panel, louver, lite
HANDLE_TYPE="knob"          # Options: knob, lever, pull, bar, none
X_SUBDIVISIONS=1            # Horizontal panel subdivisions (integer)
Y_SUBDIVISIONS=2            # Vertical panel subdivisions (integer)
SEED=1003                   # Seed for consistent generation

# Output settings
EXPORT_FORMAT="mjcf"        # MuJoCo export format
OUTPUT_DIR="sim_exports/${EXPORT_FORMAT}/door/${SEED}"

# Paths
BLENDER_PATH="/Applications/Blender.app/Contents/MacOS/Blender"
INFINIGEN_PATH="/Users/omarrayyann/Documents/infinigen"
SCRIPT_NAME="door_generator_${SEED}.py"

# =============================================================================
# SCRIPT BANNER
# =============================================================================

echo "=============================================================="
echo "🚪 EXACT DOOR GENERATION & MUJOCO EXPORT"
echo "=============================================================="
echo "Door Configuration:"
echo "  • Type: ${DOOR_TYPE}"
echo "  • Handle: ${HANDLE_TYPE}"
echo "  • Subdivisions: ${X_SUBDIVISIONS}x${Y_SUBDIVISIONS}"
echo "  • Seed: ${SEED}"
echo "  • Output: ${OUTPUT_DIR}"
echo "=============================================================="

# =============================================================================
# STEP 1: CREATE DYNAMIC DOOR GENERATOR SCRIPT
# =============================================================================

echo "📝 Creating door generator script..."

cat > "${SCRIPT_NAME}" << EOF
#!/usr/bin/env python3
"""
Dynamic Door Generator Script
Generated automatically with exact parameters
"""

import sys
import os

# Add infinigen to Blender's Python path
infinigen_path = '${INFINIGEN_PATH}'
if infinigen_path not in sys.path:
    sys.path.insert(0, infinigen_path)

# Add conda environment site-packages
conda_site_packages = '/opt/anaconda3/envs/infinigen/lib/python3.11/site-packages'
if conda_site_packages not in sys.path:
    sys.path.insert(0, conda_site_packages)

try:
    import bpy
    import gin
    from infinigen.assets.objects.elements.doors.panel import PanelDoorFactory
    from infinigen.assets.objects.elements.doors.panel import GlassPanelDoorFactory
    from infinigen.assets.objects.elements.doors.louver import LouverDoorFactory
    from infinigen.assets.objects.elements.doors.lite import LiteDoorFactory
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def create_exact_door():
    """Generate door with hardcoded exact parameters"""
    
    # HARDCODED PARAMETERS FROM BASH SCRIPT
    door_type = '${DOOR_TYPE}'
    handle_type = '${HANDLE_TYPE}'
    x_subdivisions = ${X_SUBDIVISIONS}
    y_subdivisions = ${Y_SUBDIVISIONS}
    seed = ${SEED}
    
    print(f"🚪 Generating door with exact parameters:")
    print(f"  • Door type: {door_type}")
    print(f"  • Handle type: {handle_type}")
    print(f"  • X subdivisions: {x_subdivisions}")
    print(f"  • Y subdivisions: {y_subdivisions}")
    print(f"  • Seed: {seed}")
    
    # Clear existing objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Factory selection
    factory_map = {
        'panel': PanelDoorFactory,
        'glass_panel': GlassPanelDoorFactory,
        'louver': LouverDoorFactory,
        'lite': LiteDoorFactory
    }
    
    if door_type not in factory_map:
        raise ValueError(f"Invalid door_type: {door_type}")
    
    # Create factory
    factory_class = factory_map[door_type]
    factory = factory_class(factory_seed=seed)
    
    print(f"📦 Created {factory_class.__name__}")
    
    # FORCE exact parameters (override random generation)
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
    
    # Generate door
    print("🏗️  Generating door asset...")
    door_obj = factory.create_asset()
    
    if door_obj is None:
        raise RuntimeError("Failed to create door asset")
    
    print(f"✅ Door created: {door_obj.name}")
    
    # Save blend file
    blend_file = f"door_{door_type}_{handle_type}_{seed}.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_file)
    print(f"💾 Saved: {blend_file}")
    
    return True

if __name__ == "__main__":
    try:
        success = create_exact_door()
        if success:
            print("\\n🎉 Door generation successful!")
        else:
            print("\\n❌ Door generation failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\\n💥 Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
EOF

echo "✅ Created: ${SCRIPT_NAME}"

# =============================================================================
# STEP 2: GENERATE DOOR WITH BLENDER
# =============================================================================

echo ""
echo "🏗️  Generating door with Blender..."

if [ ! -f "${BLENDER_PATH}" ]; then
    echo "❌ Blender not found at: ${BLENDER_PATH}"
    echo "Please update BLENDER_PATH in this script"
    exit 1
fi

cd "${INFINIGEN_PATH}"

# Run Blender with our custom script
"${BLENDER_PATH}" --background --python "${SCRIPT_NAME}"

if [ $? -eq 0 ]; then
    echo "✅ Door generation completed successfully"
else
    echo "❌ Door generation failed"
    exit 1
fi

# =============================================================================
# STEP 3: EXPORT TO MUJOCO
# =============================================================================

echo ""
echo "🚀 Exporting to MuJoCo format..."

# Create output directory
mkdir -p "${OUTPUT_DIR}"

# Run MuJoCo export
python scripts/spawn_asset.py -exp "${EXPORT_FORMAT}" -n door -s "${SEED}"

if [ $? -eq 0 ]; then
    echo "✅ MuJoCo export completed successfully"
else
    echo "❌ MuJoCo export failed"
    exit 1
fi

# =============================================================================
# STEP 4: VERIFY OUTPUT AND CLEANUP
# =============================================================================

echo ""
echo "🔍 Verifying output..."

# Check if door.xml was created
if [ -f "${OUTPUT_DIR}/door.xml" ]; then
    echo "✅ Found: ${OUTPUT_DIR}/door.xml"
    
    # Check for handle components in XML
    if grep -q "handle_" "${OUTPUT_DIR}/door.xml"; then
        echo "✅ Handle components found in XML"
    else
        echo "⚠️  No handle components found in XML"
    fi
    
    # List generated assets
    if [ -d "${OUTPUT_DIR}/assets/visual" ]; then
        echo "✅ Visual assets:"
        ls -la "${OUTPUT_DIR}/assets/visual/" | grep -E '\.(obj|mtl)$' | awk '{print "     " $9}'
    fi
    
else
    echo "❌ door.xml not found in ${OUTPUT_DIR}"
    exit 1
fi

# Cleanup temporary script
rm -f "${SCRIPT_NAME}"
echo "🧹 Cleaned up temporary files"

# =============================================================================
# COMPLETION SUMMARY
# =============================================================================

echo ""
echo "=============================================================="
echo "🎉 DOOR GENERATION & EXPORT COMPLETE!"
echo "=============================================================="
echo "Generated door with EXACT parameters:"
echo "  ✅ Door type: ${DOOR_TYPE}"
echo "  ✅ Handle type: ${HANDLE_TYPE}"
echo "  ✅ Subdivisions: ${X_SUBDIVISIONS}x${Y_SUBDIVISIONS}"
echo "  ✅ Seed: ${SEED}"
echo ""
echo "Output files:"
echo "  📁 Directory: ${OUTPUT_DIR}"
echo "  📄 MuJoCo XML: ${OUTPUT_DIR}/door.xml"
echo "  🎨 Visual assets: ${OUTPUT_DIR}/assets/visual/"
echo "  📊 Metadata: ${OUTPUT_DIR}/metadata.json"
echo ""
echo "🚀 Your door is ready for MuJoCo simulation!"
echo "=============================================================="

# =============================================================================
# USAGE INSTRUCTIONS
# =============================================================================

echo ""
echo "💡 To generate different doors, modify these variables at the top:"
echo "   DOOR_TYPE=\"panel\"        # panel, glass_panel, louver, lite"
echo "   HANDLE_TYPE=\"knob\"       # knob, lever, pull, bar, none"
echo "   X_SUBDIVISIONS=1          # horizontal subdivisions"
echo "   Y_SUBDIVISIONS=2          # vertical subdivisions"
echo "   SEED=1003                 # seed for consistency"
echo ""
echo "Then run: bash $0"
