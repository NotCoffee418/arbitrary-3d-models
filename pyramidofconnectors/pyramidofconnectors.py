# %%
# type: ignore
# CTRL+Shift+P > OCP CAD VIEWER: Open CAD Viewer

# The markers "# %%" separate code blocks for execution (cells)
# Press shift-enter to exectute a cell and move to next cell
# Press ctrl-enter to exectute a cell and keep cursor at the position
# For more details, see https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter

# %%
# Imports and config
from build123d import *
from ocp_vscode import *

# Import common parts
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from _common_parts.screws import *  # noqa: E402
from _common_parts.export import export_model  # noqa: E402

# Used to name the exported files
PART_NAME = "pyramidofconnectors"

# %%

# NOTE!! This kinda worked but it was way too attached to eachother still got stringy because hopping around.


# Load and rotate the source STL
source_stl_path = Path(__file__).parent / "source_connector.stl"

# Part dimensions after rotation
part_x = 7
part_y = 7
part_z = 17

# Pyramid config
spacing = 0.5  # 0.5mm between parts

# Pyramid layers: 4x4, 3x3, 2x2, 1x1
layers = [4, 3, 2, 1]

pyramid_parts = []
current_z = 0

for layer_idx, layer_size in enumerate(layers):
    # Calculate offsets for this layer
    x_step = part_x + spacing
    y_step = part_y + spacing

    # Center this layer
    start_x = -(layer_size - 1) * x_step / 2
    start_y = -(layer_size - 1) * y_step / 2

    for row in range(layer_size):
        for col in range(layer_size):
            x_pos = start_x + col * x_step
            y_pos = start_y + row * y_step

            # Load STL
            part = import_stl(str(source_stl_path))

            # Try using Location with rotation angles directly
            loc = Location((x_pos, y_pos, current_z), (90, 0, 0))
            part = part.locate(loc)
            pyramid_parts.append(part)

    # Move up for next layer
    current_z += part_z + spacing

# Combine all parts
pyramid = Compound(children=pyramid_parts)

show(pyramid, reset_camera=Camera.KEEP)

# %%
# Export
export_part = pyramid
export_model(export_part, PART_NAME)
# %%
