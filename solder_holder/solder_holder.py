
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
import math

# Import common parts
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from _common_parts.screws import *  # noqa: E402

# Used to name the exported files
PART_NAME = "solder_holder"

# %%
# Algebra mode.
BASE_X_SIZE = 80
BASE_Y_SIZE = 65
BASE_Z_SIZE = 6
BASE_FILLET = 1  # idk whatthis parami s anymore, not that
BASE_WEIGHT_GAP_X_SIZE = 70
BASE_WEIGHT_GAP_Y_SIZE = 55
BASE_WEIGHT_GAP_Z_SIZE = 3
WEIGHT_HOLE_DIAMETER = 23
HOLDER_SHAFT_X_SIZE_TOP = 20
HOLDER_SHAFT_X_SIZE_BOT = 30
HOLDER_SHAFT_Y_SIZE = 63
HOLDER_SHAFT_DEPTH = 3.2
HOLDER_SHAFT_FILLET = 1.5
HOLDER_BAR_DIAMETER = 15
HOLDER_BAR_LENGTH = 60
BAR_OFFSET_FROM_TOP = 5
BAR_COVER_DIAMETER = 18
BAR_COVER_THICKNESS = 3

# Base Weight gap
with BuildPart(mode=Mode.ADD) as base_weight_gap:
    with BuildSketch():
        Rectangle(BASE_WEIGHT_GAP_X_SIZE, BASE_WEIGHT_GAP_Y_SIZE)
    extrude(amount=BASE_WEIGHT_GAP_Z_SIZE)
    fillet(base_weight_gap.edges().filter_by(Axis.Z), radius=BASE_FILLET)

# Base part
with BuildPart() as base:
    # Outer base
    with BuildSketch():
        Rectangle(BASE_X_SIZE, BASE_Y_SIZE)
    extrude(amount=BASE_Z_SIZE)
    fillet(base.edges().filter_by(Axis.Z), radius=3)
    fillet(base.edges().filter_by(Axis.X), radius=1)


# Weight hole bottom of base
with BuildPart() as weight_hole:
    with BuildSketch():
        Circle(WEIGHT_HOLE_DIAMETER/2)
    extrude(amount=BASE_WEIGHT_GAP_Z_SIZE)

# Shaft holder
with BuildPart() as shaft:
    x_offset = (HOLDER_SHAFT_X_SIZE_BOT - HOLDER_SHAFT_X_SIZE_TOP) / 2
    with BuildSketch(Plane.XY):
        Polygon(
            (0, -HOLDER_SHAFT_Y_SIZE/2),
            (HOLDER_SHAFT_X_SIZE_BOT, -HOLDER_SHAFT_Y_SIZE/2),
            (HOLDER_SHAFT_X_SIZE_TOP + x_offset, HOLDER_SHAFT_Y_SIZE/2),
            (x_offset, HOLDER_SHAFT_Y_SIZE/2)
        )
    extrude(amount=HOLDER_SHAFT_DEPTH)
    fillet(shaft.edges(), radius=HOLDER_SHAFT_FILLET)

# Holder bar
# Holder bar
with BuildPart() as holder_bar:
    with BuildSketch(Plane.XY.offset(HOLDER_SHAFT_DEPTH)):
        with Locations((0, HOLDER_SHAFT_Y_SIZE/2 - HOLDER_BAR_DIAMETER/2 - BAR_OFFSET_FROM_TOP, 0)):
            Circle(HOLDER_BAR_DIAMETER/2)
    extrude(amount=HOLDER_BAR_LENGTH - HOLDER_SHAFT_DEPTH)

    # bar cover
    with BuildSketch(Plane.XY.offset(HOLDER_SHAFT_DEPTH + HOLDER_BAR_LENGTH - BAR_COVER_THICKNESS)):
        with Locations((0, HOLDER_SHAFT_Y_SIZE/2 - HOLDER_BAR_DIAMETER/2 - BAR_OFFSET_FROM_TOP, 0)):
            Circle(BAR_COVER_DIAMETER/2)
    extrude(amount=BAR_COVER_THICKNESS)

    # Fillet the top edge of the cover (circular edge at the top)
    top_edges = holder_bar.edges().sort_by(Axis.Z)[-1]  # Get top edge
    fillet(top_edges, radius=0.5)


# Final
with BuildPart() as final_base:
    add(base.part)
    add(base_weight_gap.part, mode=Mode.SUBTRACT)
    add(weight_hole, mode=Mode.ADD)

with BuildPart() as final_holder:
    add(shaft.part, mode=Mode.ADD)
    add(holder_bar.part, mode=Mode.ADD)

with BuildPart() as combined:
    add(final_base.part, mode=Mode.ADD)
    with Locations((0, 32.5, 35)):
        add(final_holder.part, rotation=(90, 0, 0), mode=Mode.ADD)


# show([base, dent_l, dent_r]) # Preview with removed part visible
show(combined, reset_camera=False)

# %%
# Export

show(combined, reset_camera=False)
# exporter_base = Mesher()
# exporter_base.add_shape(final_base.part)
# exporter_base.write(f"{PART_NAME}_base.3mf")
# exporter_base.write(f"{PART_NAME}_base.stl")

# exporter_combined = Mesher()
# exporter_combined.add_shape(final_holder.part)
# exporter_combined.write(f"{PART_NAME}_holder.3mf")
# exporter_combined.write(f"{PART_NAME}_holder.stl")

exporter_combined = Mesher()
exporter_combined.add_shape(combined.part)
exporter_combined.write(f"{PART_NAME}.3mf")
exporter_combined.write(f"{PART_NAME}.stl")
# %%
