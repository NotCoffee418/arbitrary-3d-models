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
PART_NAME = "ac_pir_detector_case"

# %%
# Algebra mode.

CASE_X_SIZE = 75
CASE_Y_SIZE = 35
CASE_FREE_SPACE_XY = 4  # Space around board in case
CASE_Z_SPACE = 15  # Z space inside case, excluding walls
CASE_FILLET_RADIUS = 0.5
WALL_THICKNESS = 2  # at least 2 or front cover screws push out
BOARD_ACTUAL_X_SIZE = 68.5
BOARD_ACTUAL_Y_SIZE = 28


# Bare minimum excluding screen is 6 for space to board minus visible components
# This is is board holder height, other components adapt to this variable
BOARD_ZSPACE_RESERVED = 5

# Measured TFT size
TFT_X_SIZE = 13
TFT_Y_SIZE = 22

# Nearest edge of TFT to top of board
TFT_TOP_EDGE_TOP_OFFSET = 13.5


# Offset of center of the PIR from edge of the case (USB side)
PIR_CENTER_BOTTOM_OFFSET = 13.75
PIR_OUTER_DIAMETER = 13
PIR_INNER_DIAMETER = 16  # or whatever size you want at the top

# X space needed for usb cable plugin
# minimal tolerance to avoid accidental unplugging
BOARD_X_TO_CABLE_SPACE = 28
USB_CABLE_DIAMETER = 4
USB_CABLE_CLIPABLE_DIAMETER = 2.5

# Board front cover


# TFT side is low X, PIR side is high X
def get_x_board_edge(on_high_x: bool):
    offset = (BOARD_ACTUAL_X_SIZE / 2)
    return offset if on_high_x else -offset


def get_y_board_edge(on_high_y: bool):
    offset = (BOARD_ACTUAL_Y_SIZE / 2)
    return offset if on_high_y else -offset


def get_case_x_size(include_walls: bool):
    # Board size plus free space padding and walls
    wall_space = WALL_THICKNESS * 2 if include_walls else 0
    x_size = wall_space + BOARD_ACTUAL_X_SIZE + CASE_FREE_SPACE_XY * 2

    # Add USB cable space
    x_size += BOARD_X_TO_CABLE_SPACE
    return x_size


# Position offset for case, keeping the board centered
def get_case_x_pos_offset(include_walls: bool):
    # Offset from center to outer edge in X
    wall_offset = WALL_THICKNESS if include_walls else 0
    return -BOARD_X_TO_CABLE_SPACE / 2 + wall_offset


def get_case_y_pos_offset(include_walls: bool):
    # Offset from center to outer edge in Y
    wall_offset = WALL_THICKNESS if include_walls else 0
    return wall_offset


def get_case_y_size(include_walls: bool):
    wall_space = WALL_THICKNESS * 2 if include_walls else 0
    return wall_space + BOARD_ACTUAL_Y_SIZE + CASE_FREE_SPACE_XY * 2


# Z positioned holder clip
def get_board_holder_clip():
    # Remaining length of screw after board
    screw_depth = 5.7

    # Screw hole diameter (minimal print resistance, vertical)
    hole_size = 2.05
    hole_padding = 1.5

    clip = Circle(hole_size / 2 + hole_padding)
    clip = extrude(clip, BOARD_ZSPACE_RESERVED)
    clip = clip.translate((0, 0, WALL_THICKNESS))

    hole = Circle(hole_size / 2)
    hole = extrude(hole, screw_depth)
    hole = hole.translate(
        (0, 0, WALL_THICKNESS + BOARD_ZSPACE_RESERVED - screw_depth))

    return clip - hole


def get_all_holder_clips():
    # Space between holes on board
    x_diff = 63.5
    y_diff = 23.5

    c1 = get_board_holder_clip().translate(
        (-x_diff / 2, -y_diff / 2, 0))
    c2 = get_board_holder_clip().translate(
        (x_diff / 2, -y_diff / 2, 0))
    c3 = get_board_holder_clip().translate(
        (-x_diff / 2, y_diff / 2, 0))
    c4 = get_board_holder_clip().translate(
        (x_diff / 2, y_diff / 2, 0))
    return c1 + c2 + c3 + c4


def pir_hole():
    x_pos = -(BOARD_ACTUAL_X_SIZE / 2) + PIR_CENTER_BOTTOM_OFFSET

    ph = Circle(PIR_OUTER_DIAMETER / 2)
    ph = extrude(ph, WALL_THICKNESS / 2)

    # Create cone for inner allowing more space
    ph_round_inner = Cone(
        PIR_OUTER_DIAMETER / 2, PIR_INNER_DIAMETER / 2, WALL_THICKNESS)

    # Z position fom center, 0 would be WALL_THICKNESS / 2
    ph = ph.translate((x_pos, 0, 0))
    ph_round_inner = ph_round_inner.translate((x_pos, 0, WALL_THICKNESS))
    return ph + ph_round_inner


# X position from outer side of X
def tft_hole_x_position():
    return (BOARD_ACTUAL_X_SIZE / 2) - \
        (TFT_X_SIZE / 2) - TFT_TOP_EDGE_TOP_OFFSET


def tft_hole():
    th = Rectangle(TFT_X_SIZE, TFT_Y_SIZE)
    th = extrude(th, WALL_THICKNESS)
    z_edges = th.edges().filter_by(Axis.Z)
    th = fillet(z_edges, radius=CASE_FILLET_RADIUS)
    th = th.translate((tft_hole_x_position(), 0, 0))
    return th


def add_tft_padding():
    # Measured free space between TFT and case based on holder clips Z size3
    padding_z_size = BOARD_ZSPACE_RESERVED - 4
    padding_x_pos = tft_hole_x_position()
    padding = Rectangle(TFT_X_SIZE + WALL_THICKNESS*2,
                        TFT_Y_SIZE + WALL_THICKNESS*2)
    padding = extrude(padding, padding_z_size)
    padding = padding.translate((padding_x_pos, 0, WALL_THICKNESS))

    # Fillet edges
    pad_edges = padding.edges().filter_by(Axis.Z)
    padding = fillet(pad_edges, radius=CASE_FILLET_RADIUS * 3)

    # Cut out tft hole space
    cutout = tft_hole().translate((0, 0, WALL_THICKNESS))
    return padding - cutout

# Mystery nonsense variables have begun


def x_top_wall_position():
    return CASE_X_SIZE / 2 - get_case_x_pos_offset(True) / 2 - WALL_THICKNESS - CASE_FILLET_RADIUS / 2


def x_bottom_wall_position():
    return -CASE_X_SIZE - get_case_x_pos_offset(True) - WALL_THICKNESS - CASE_FILLET_RADIUS / 2


def positioned_usb_cable_cutout():
    usb_cutout = Circle(USB_CABLE_DIAMETER / 2)
    usb_cutout = extrude(usb_cutout, WALL_THICKNESS)
    usb_cutout = usb_cutout.rotate(Axis.Y, 90)
    usb_cutout = usb_cutout.translate((
        x_bottom_wall_position() - WALL_THICKNESS / 2,
        0,
        WALL_THICKNESS + (CASE_Z_SPACE / 2)))
    return usb_cutout


def half_x_walls():
    def x_wall(half_height_z, include_walls=True):
        z_size = CASE_Z_SPACE
        if half_height_z:
            z_size /= 2
        if include_walls:
            z_size += WALL_THICKNESS
        w = Rectangle(WALL_THICKNESS, get_case_y_size(True))
        # Half space size as back cover will do other half
        w = extrude(w, z_size)
        return w

    # Top cover gets a full height wall
    wall_top_x = x_wall(False, True).translate((
        x_top_wall_position(),
        get_case_y_pos_offset(True) - WALL_THICKNESS,
        WALL_THICKNESS))

    wall_top_x_edges = wall_top_x.edges().filter_by(Axis.Z)[2:4]
    wall_top_x = fillet(wall_top_x_edges, radius=CASE_FILLET_RADIUS)

    # Bottom wall is half height and has the USB cable cutout
    wall_bottom_x = x_wall(True, False).translate((
        x_bottom_wall_position(),
        get_case_y_pos_offset(True) - WALL_THICKNESS,
        WALL_THICKNESS))

    wall_bottom_x_edges = wall_bottom_x.edges().filter_by(Axis.Z)[0:2]
    wall_bottom_x = fillet(wall_bottom_x_edges, radius=CASE_FILLET_RADIUS)

    return wall_top_x + wall_bottom_x - positioned_usb_cable_cutout()


def half_y_walls():
    def y_wall():
        w = Rectangle(get_case_x_size(True), WALL_THICKNESS)
        # Half space size as back cover will do other half
        w = extrude(w, CASE_Z_SPACE / 2)
        fillet_z = w.edges().filter_by(Axis.Z)
        w = fillet(fillet_z, radius=CASE_FILLET_RADIUS)
        return w

    y_wall_positioned = y_wall().translate((
        get_case_x_pos_offset(True),
        get_case_y_size(False)/2 + WALL_THICKNESS/2,
        WALL_THICKNESS))

    return y_wall_positioned + y_wall_positioned.mirror(Plane.XZ)


def floor_base():
    # Base object
    fc = Rectangle(get_case_x_size(True),
                   get_case_y_size(True))
    fc = extrude(fc, WALL_THICKNESS)
    fillet_z = fc.edges().filter_by(Axis.Z)
    fc = fillet(fillet_z, radius=CASE_FILLET_RADIUS)
    return fc


def front_cover():
    fc = floor_base()
    fc = fc.translate((get_case_x_pos_offset(True), 0, 0))

    # Assemble related objects
    return fc - (pir_hole() + tft_hole()) + \
        get_all_holder_clips() + add_tft_padding() + \
        half_y_walls() + half_x_walls()


final = front_cover()

show(final, reset_camera=Camera.KEEP)

# %%
# Export
export_part = final
export_model(export_part, PART_NAME)
# %%
