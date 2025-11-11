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
PART_NAME = "wl_1865"

# %%
# Algebra mode.

outer_diam_bot = 6
outer_diam_top = 5
inner_diam = 3
height = 4.5

outer_bot = Circle(outer_diam_bot/2)
outer_bot = extrude(outer_bot, height / 2)

with BuildPart() as outer_top:
    with BuildSketch():
        Circle(outer_diam_bot / 2)

    with BuildSketch(Plane.XY.offset(height / 2)):
        Circle(outer_diam_top / 2)

    loft()
outer_top = outer_top.part.translate((0, 0, height / 2))

inner = Circle(inner_diam/2)
inner = extrude(inner, height)

final = (outer_bot + outer_top) - inner


# show([base, dent_l, dent_r]) # Preview with removed part visible
show(final, reset_camera=False)

# %%
# Export
export_part = final
export_model(export_part, PART_NAME)
# %%
