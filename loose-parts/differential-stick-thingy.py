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

hex_diameter = 6
hex_height = 20
circle_diameter = 6
circle_height = 20


hex = RegularPolygon(radius=hex_diameter/2, side_count=6)
hex = extrude(hex, hex_height)
circle = Circle(circle_diameter/2)
circle = extrude(circle, circle_height)
circle = circle.move(Location((0, 0, hex_height)))
final = hex + circle


show(final)

# %%
# Export
export_part = final

show(export_part)
exporter = Mesher()
exporter.add_shape(export_part)
exporter.write(f"{PART_NAME}.3mf")
exporter.write(f"{PART_NAME}.stl")
# %%
