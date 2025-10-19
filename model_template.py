# %%

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

# Used to name the exported files
PART_NAME = "rename_me_part_name"

# %%
# Algebra mode.

box_width = 2
box_length = 0.5
base_height = 1

dent_y = 0.3  # Offset from bottom of box
dent_depth = 0.15
dent_height = 0.2

# Base object
base = Rectangle(box_width, box_length)
base = extrude(base, base_height)

# Dent shape function


def get_dent():
    dent_shape = Rectangle(box_width, dent_depth)
    dent_shape = extrude(dent_shape, dent_height)
    return dent_shape


# Specify dent locations
dent_l = get_dent().move(Location((0, -box_length/2+dent_depth/2, dent_y)))
dent_r = get_dent().move(Location((0, box_length/2-dent_depth/2, dent_y)))

# Subtract to remove like magic
base = base - dent_l - dent_r


# show([base, dent_l, dent_r]) # Preview with removed part visible
show(base)

# %%
# Export
export_part = base

show(export_part)
exporter = Mesher()
assert base is not None
exporter.add_shape(export_part)
exporter.write(f"{PART_NAME}.3mf")
exporter.write(f"{PART_NAME}.stl")
# %%
