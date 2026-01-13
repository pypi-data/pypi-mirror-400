import os
import sys
import bpy
import logging
import addon_utils
from pathlib import Path

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)

if int(os.environ.get('BLENDER_DEBUGGING_ON', '0')):
    try:
        import debugpy
        port = int(os.environ.get('BLENDER_DEBUG_PORT', 5678))
        debugpy.configure(python=sys.executable)
        debugpy.listen(port)
        logger.info(f'Waiting for debugger to attach on port {port}...')
        debugpy.wait_for_client()
    except ImportError:
        logger.error(
            'Failed to initialize debugger because debugpy is not available '
            'in the current python environment.'
        )


def post_startup(*args):
    # optionally start the MCP server if that addon is available
    if hasattr(bpy.ops, 'blendermcp'):
        bpy.ops.blendermcp.start_server()

    print("Blender startup script from poly_hammer_utils completed.")

BLENDER_SCRIPTS_FOLDERS = [Path(i) for i in os.environ.get('BLENDER_SCRIPTS_FOLDERS', '').split(os.pathsep)]

for scripts_folder in BLENDER_SCRIPTS_FOLDERS:
    script_directory = bpy.context.preferences.filepaths.script_directories.get(scripts_folder.parent.name)
    if script_directory:
        bpy.context.preferences.filepaths.script_directories.remove(script_directory)

    script_directory = bpy.context.preferences.filepaths.script_directories.new()
    script_directory.name = scripts_folder.parent.name
    script_directory.directory = str(scripts_folder)
    
    # Add the addons folder to sys.path so Python can import addon modules
    addons_folder = scripts_folder / 'addons'
    if addons_folder.exists() and str(addons_folder) not in sys.path:
        sys.path.append(str(addons_folder))

# Refresh addon list to discover newly added addons from script directories
addon_utils.modules_refresh()

for scripts_folder in BLENDER_SCRIPTS_FOLDERS:
    addons_folder = scripts_folder / 'addons'
    if not addons_folder.exists():
        continue
    for addon in os.listdir(addons_folder):
        if (addons_folder / addon).is_dir():
            bpy.ops.preferences.addon_enable(module=addon)

# add a function to the event timer that will fire after everything is initialized
bpy.app.timers.register(post_startup, first_interval=0.1)