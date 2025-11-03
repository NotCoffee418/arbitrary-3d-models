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
from _common_parts.fillet_assist import *  # noqa: E402
from _common_parts.export import export_model  # noqa: E402

from curtain_blocker.blocker import get_slider, base_height



# Used to name the exported files
PART_NAME = "curtain_holder"

# %%
# Algebra mode.
slider = get_slider()

ring_radius = 5
ring_depth = 2.2
ring_z_offset = base_height - ring_radius * 1.4



def get_ring():
    outer_radius = ring_radius + 1
    inner_radius = ring_radius - 1
    ring = Cylinder(outer_radius, ring_depth)
    hole = Cylinder(inner_radius, ring_depth + 2).move(Location((0, 0, -1)))
    ring_final = ring - hole
    
    # Round the edges
    ring_final = ring_final.fillet(0.5, ring_final.edges())
    
    ring_final = ring_final.rotate(Axis.X, 90)
    ring_final = ring_final.move(Location((0, 0, ring_z_offset)))
    return ring_final




# Create parts

final = slider + get_ring().move(Location((0, 0, base_height+1)))


export_part = final
show(export_part)  # Preview with removed part visible
# show(final)

# %%
# Export

show(export_part)
export_model(export_part, PART_NAME)
# %%
