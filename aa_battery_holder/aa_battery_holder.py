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

# Used to name the exported files
PART_NAME = "aa_battery_holder"

# %%
# Algebra mode.
b_clearance = 0.5
b_diameter = 14.5 + b_clearance
b_length = 49 + b_clearance
b_knob_diameter = 5.5 + b_clearance
# - because we want it to reach i guess, its gonna get cozy...
b_knob_height = 1.5 - b_clearance

case_x_size = 30
case_y_size = 15
case_z_size = 130
case_fillet = 2


def case():
    with BuildPart() as c:
        with BuildSketch():
            # <-- Use your dimension variables here
            Rectangle(case_x_size, case_y_size)
        extrude(amount=case_z_size)
        fillet(c.edges(), radius=case_fillet)
    return c.part


def battery_slot_cutout():
    def battery_slot():
        with BuildPart() as b:
            # Main battery body
            with BuildSketch():
                Circle(radius=b_diameter/2)
            extrude(amount=b_length)

            # + nub
            with BuildSketch(Plane.XY.offset(b_length)):
                Circle(radius=b_knob_diameter/2)
            extrude(amount=b_knob_height)

            # Upwards nub extension
            with BuildSketch(Plane.XY.offset(b_length)):
                with Locations((0, case_z_size/2)):
                    Rectangle(b_knob_diameter, case_z_size)
            extrude(amount=b_knob_height)

            # Upwards battery shape extension
            with BuildSketch(Plane.XY.offset(0)):
                with Locations((0, case_z_size/2)):
                    Rectangle(b_diameter, case_z_size)
            extrude(amount=b_length)

        return b.part
    # .rotate(Axis.X, 90).translate((-(b_diameter+b_clearance)/2, b_length/2, (b_diameter+b_clearance)/2))

    with BuildPart() as cutout:
        # Battery 1
        with Locations((0, 0, 0)):
            add(battery_slot())

        # Battery 2 - positioned next to first one
        with Locations((0, 0, b_length+b_knob_height)):
            add(battery_slot())

        # Remove the middle

    return cutout.part


def connection_clip_hole():
    clip_x_size = 22.22
    clip_z_size = 3.5
    clip_y_size = 10  # arbitrary extrusion size

    with BuildPart() as clip_hole:
        with BuildSketch():
            Rectangle(clip_x_size, clip_y_size)
        extrude(amount=clip_z_size)
    return clip_hole.part


def symbol_engraving(symbol: str):
    with BuildPart() as s:
        with BuildSketch():
            Text(symbol, font_size=10)
        extrude(amount=1)
    return s.part.rotate(Axis.X, 90)  # or -90, or try Axis.Y


with BuildPart() as final:
    add(case().translate((0, 0, -4)))
    add(
        battery_slot_cutout().translate((0, 5, 10)), mode=Mode.SUBTRACT)
    add(
        connection_clip_hole().translate((0, 5, 110.5)), mode=Mode.SUBTRACT)
    add(
        connection_clip_hole().translate((0, 5, 6.5)), mode=Mode.SUBTRACT)
    add(symbol_engraving("+").translate((0, 7.5, 120)), mode=Mode.SUBTRACT)
    add(symbol_engraving("_").translate((0, 7.5, 3)), mode=Mode.SUBTRACT)

show(final, reset_camera=False)

# %%
# Export
export_part = final.part

show(export_part, reset_camera=False)
exporter = Mesher()
exporter.add_shape(export_part)
exporter.write(f"{PART_NAME}.3mf")
exporter.write(f"{PART_NAME}.stl")
# %%
