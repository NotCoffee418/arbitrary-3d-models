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
import math

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from _common_parts.screws import *  # noqa: E402
from _common_parts.fillet_assist import *  # noqa: E402


# Used to name the exported files
PART_NAME = "curtain_blocker"

# %%
# Algebra mode.

# slider config
base_width = 12
base_length = 9
base_height = 7  # 14 is gonna be the absolute limit
base_fillet_radius = 0.2

# Config dents
dent_z = 2.2  # Offset from bottom of box
dent_depth = 2
dent_height = 3.2
dent_fillet_radius = 0.2

# Config blocker
blocker_height = 30


# Config validation
if base_height + blocker_height < 15:
    raise ValueError("Blocker height not long enough to actually block")


def get_dent(is_right=False):
    # Define shape
    dent_shape = Rectangle(base_width, dent_depth)
    dent_shape = extrude(dent_shape, dent_height)

    # Fillet inner edges
    x_edges = dent_shape.edges().filter_by(Axis.X)
    specific_edges = [x_edges[2], x_edges[3]]
    dent_shape = fillet(specific_edges, radius=dent_fillet_radius)

    # Add outer fillets
    of1 = get_outer_fillet(base_width, dent_fillet_radius, edge_id=0)
    of2 = of1.mirror(Plane.XY)
    of1 = of1.move(
        Location((0, -dent_depth/2 + dent_fillet_radius, dent_height)))
    of2 = of2.move(Location((0, -dent_depth/2 + dent_fillet_radius, 0)))
    final_dent = dent_shape + of1 + of2
    if is_right:
        final_dent = final_dent.mirror(Plane.XZ)
    return final_dent


def get_slider():
    # Base object
    base = Rectangle(base_width, base_length)
    base = extrude(base, base_height)
    base = fillet(base.edges(), radius=base_fillet_radius)

    # Specify dent locations
    dent_l = get_dent(False).move(
        Location((0, -base_length/2+dent_depth/2, dent_z)))
    dent_r = get_dent(True).move(
        Location((0, base_length/2-dent_depth/2, dent_z)))

    # Subtract to remove like magic
    return base - dent_l - dent_r


def get_blocker():
    deg = 8
    blocker = Box(base_width, base_length, blocker_height)

    # Calculate exactly how far forward the cutter needs to be
    cutter_depth = base_width * math.sin(math.radians(deg)) + base_length*0.5

    cutter = Box(base_width*2, cutter_depth, blocker_height*2)

    pivot_x = base_width/2
    pivot_y = base_length/2

    # Position cutter so its back edge is at the front of the blocker
    cutter = cutter.move(Location((0, base_length/2 + cutter_depth/2, 0)))

    # Rotate around front-right corner
    cutter = cutter.move(Location((-pivot_x, -pivot_y, 0)))
    cutter = cutter.rotate(Axis.Z, deg)
    cutter = cutter.move(Location((pivot_x, pivot_y, 0)))

    blocker_final = blocker - cutter

    # Try filleting - select edges and apply fillet
    blocker_final = fillet(blocker_final.edges(), radius=base_fillet_radius)

    return blocker_final.move(Location((0, 0, base_height*2-(base_fillet_radius+dent_fillet_radius)*2)))


# Create parts
final = get_slider() + get_blocker().move(Location((0, 0, base_height+1)))


export_part = final
show(export_part)  # Preview with removed part visible
# show(final)


# %%
# Export


show(export_part)
exporter = Mesher()
exporter.add_shape(export_part)
exporter.write(f"{PART_NAME}.3mf")
exporter.write(f"{PART_NAME}.stl")
# %%
