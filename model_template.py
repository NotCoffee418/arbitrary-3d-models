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

# Used to name the exported files
PART_NAME = "part_name"

# %%
# Algebra mode.

box_w = 1.0
box_h = 0.5
base_d = 0.7
dent_start_d = 0.3
dent_d = 0.15
dent_h = 0.1

# Base object
base = Rectangle(box_w, box_h)
base = extrude(base, base_d)

# Dent


def get_dent():
    dent_shape = Rectangle(box_w, dent_d)
    dent_shape = extrude(dent_shape, dent_h)
    return dent_shape


# Specify dent locations
dent_l = get_dent().move(Location((0, -box_h/2+dent_d/2, dent_start_d)))
dent_r = get_dent().move(Location((0, box_h/2-dent_d/2, dent_start_d)))

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
exporter.write("{PART_NAME}.stl")
# %%
