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
PART_NAME = "gear_slotter"

# %%
# Algebra mode.

outer_diam = 5
inner_diam = 3.35
height = 8.9
hole_pos = 2
hole_diam = 3.2

outer = Circle(outer_diam/2)
outer = extrude(outer, height)

inner = Circle(inner_diam/2)
inner = extrude(inner, height)

hole = Circle(hole_diam / 2)
hole = extrude(hole, (outer_diam - inner_diam) * 2)
hole = hole.rotate(Axis.X, 90)
hole = hole.translate((0, 0, hole_pos))


final = outer - inner - hole


# show([base, dent_l, dent_r]) # Preview with removed part visible
show(final, reset_camera=False)

# %%
# Export
export_part = final
export_model(export_part, PART_NAME)
# %%
