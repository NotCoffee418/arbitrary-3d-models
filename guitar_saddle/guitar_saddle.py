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
PART_NAME = "guitar_saddle"

# %%
# Algebra mode.

box_width = 79
box_length = 2.9
second_length = 2.9


base_height = 7
cutout_height = 1  # to 5
second_height = 2.66

fillet_size = 1.44

# Base object
base = Rectangle(box_width, box_length)
base = extrude(base, base_height)
base_edges = base.edges()
base = fillet(base_edges, fillet_size)

second = Rectangle(box_width, second_length)
second = extrude(second, second_height)
second_edges = second.edges().filter_by(Axis.Z)
# x_indices = [0, 2]  # whatever indices you need
# second_edges = [second_edges[i] for i in x_indices]
second = fillet(second_edges, fillet_size)

# Cutout 1MM on height one side to 0
with BuildPart() as wedge_cut:
    with BuildSketch(Plane.XZ):  # XZ plane to create the taper profile
        # Triangle: starts at 0, goes to box_width, ramps from 0 to 1mm height
        Polygon((0, 0), (box_width, 0), (box_width, cutout_height))
    extrude(amount=box_length + second_length)  # Full depth
    
cutout = wedge_cut.part.translate((0, box_length, cutout_height/2))


# Subtract to remove like magic
base = (base + second) - cutout


# show([base, dent_l, dent_r]) # Preview with removed part visible
show(base, reset_camera=False)

# %%
# Export
export_part = base
export_model(export_part, PART_NAME)
# %%
