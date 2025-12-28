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
ASSEMBLED_VIEW = True
ASSEMBLY_VIEW_WITH_OFFSET = False

ASSEMBLY_VIEW_X_OFFSET = -0.5
ASSEMBLY_VIEW_Z_OFFSET = 0.5

CASE_X_SIZE = 75
CASE_Y_SIZE = 35
CASE_FREE_SPACE_XY = 4  # Space around board in case
CASE_Z_SPACE = 15  # Z space inside case, excluding walls
CASE_FILLET_RADIUS = 0.5
WALL_THICKNESS = 2  # at least 2 or front cover screws push out
BOARD_ACTUAL_X_SIZE = 68.5
BOARD_ACTUAL_Y_SIZE = 28


# Remaining length of screw after board
BOARD_SCREW_DEPTH = 5.7
FULL_SCREW_DEPTH = 7 - WALL_THICKNESS


# Screw hole diameter (minimal print resistance, vertical)
SCREW_HOLE_DIAMETER = 2.05
SCREW_SLOT_PADDING = 1.5

# Bare minimum excluding screen is 6 for space to board minus visible components
# This is is board holder height, other components adapt to this variable
BOARD_ZSPACE_RESERVED = 5

# Measured TFT size
TFT_X_SIZE = 13
TFT_Y_SIZE = 22

# Nearest edge of TFT to top of board
TFT_TOP_EDGE_TOP_OFFSET = 14.5


# Offset of center of the PIR from edge of the case (USB side)
PIR_CENTER_BOTTOM_OFFSET = 13.75
PIR_OUTER_DIAMETER = 13
PIR_INNER_DIAMETER = 16  # or whatever size you want at the top

# X space needed for usb cable plugin
# minimal tolerance to avoid accidental unplugging
BOARD_X_TO_CABLE_SPACE = 28
USB_CABLE_DIAMETER = 4
USB_CABLE_CENTER_OFFSET = 2
USB_CABLE_OUTSIDE_SPACE = 35

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


# Return Clip with hole, hole, and cutout for wall
def get_screw_and_slots(slot_height: float, override_screw_depth: float = FULL_SCREW_DEPTH):
    clip = Circle(SCREW_HOLE_DIAMETER / 2 + SCREW_SLOT_PADDING)
    clip = extrude(clip, slot_height)

    hole = Circle(SCREW_HOLE_DIAMETER / 2)
    hole = extrude(hole, override_screw_depth)

    wall_cutout = Circle(SCREW_HOLE_DIAMETER / 2)
    wall_cutout = extrude(wall_cutout, WALL_THICKNESS)
    wall_cutout = wall_cutout.translate((0, 0, slot_height))

    return (Compound([clip - hole]), hole, wall_cutout)


# Z positioned holder clip
def get_board_holder_clip():
    screw_depth = 5.7
    clip, hole, _ = get_screw_and_slots(
        BOARD_ZSPACE_RESERVED, BOARD_SCREW_DEPTH)
    hole = hole.translate(
        (0, 0, WALL_THICKNESS + BOARD_ZSPACE_RESERVED - screw_depth))
    clip = clip.translate((0, 0, WALL_THICKNESS))

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
    c1 = Rectangle(USB_CABLE_DIAMETER +
                   USB_CABLE_CENTER_OFFSET, USB_CABLE_DIAMETER)
    c1 = extrude(c1, WALL_THICKNESS)
    c1 = c1.rotate(Axis.Y, 90)
    c1 = c1.translate((
        x_bottom_wall_position() - WALL_THICKNESS / 2,
        0,
        WALL_THICKNESS + (CASE_Z_SPACE / 2) - USB_CABLE_CENTER_OFFSET))
    c1 = fillet(c1.edges().filter_by(Axis.X)[
                2:4], USB_CABLE_DIAMETER / 2 - 0.01)

    return c1


def get_x_wall(half_height_z: bool, include_wall_thickness: bool = True):
    z_size = CASE_Z_SPACE
    if half_height_z:
        z_size /= 2
    if include_wall_thickness:
        z_size += WALL_THICKNESS
    w = Rectangle(WALL_THICKNESS, get_case_y_size(True))
    # Half space size as back cover will do other half
    w = extrude(w, z_size)
    return w


def get_x_front_cover_walls():
    # Top cover gets a full height wall
    wall_top_x = get_x_wall(False, True).translate((
        x_top_wall_position(),
        get_case_y_pos_offset(True) - WALL_THICKNESS,
        WALL_THICKNESS))

    wall_top_x_edges = wall_top_x.edges().filter_by(Axis.Z)[2:4]
    wall_top_x = fillet(wall_top_x_edges, radius=CASE_FILLET_RADIUS)

    # Bottom wall is half height and has the USB cable cutout
    wall_bottom_x = get_x_wall(True, False).translate((
        x_bottom_wall_position(),
        get_case_y_pos_offset(True) - WALL_THICKNESS,
        WALL_THICKNESS))

    wall_bottom_x_edges = wall_bottom_x.edges().filter_by(Axis.Z)[0:2]
    wall_bottom_x = fillet(wall_bottom_x_edges, radius=CASE_FILLET_RADIUS)

    return wall_top_x + wall_bottom_x - positioned_usb_cable_cutout()


def get_half_y_walls(with_wall_thickness: bool = True, with_fillet: bool = True):
    def y_wall():
        w = Rectangle(get_case_x_size(with_wall_thickness), WALL_THICKNESS)
        # Half space size as back cover will do other half
        w = extrude(w, CASE_Z_SPACE / 2)
        if with_wall_thickness:
            fillet_z = w.edges().filter_by(Axis.Z)
            w = fillet(fillet_z, radius=CASE_FILLET_RADIUS)
        return w

    y_wall_positioned = y_wall().translate((
        get_case_x_pos_offset(True),
        get_case_y_size(False)/2 + WALL_THICKNESS/2,
        WALL_THICKNESS))

    return y_wall_positioned + y_wall_positioned.mirror(Plane.XZ)


def get_back_cover_screw_z_position():
    clip_depth = FULL_SCREW_DEPTH + SCREW_SLOT_PADDING
    return CASE_Z_SPACE + clip_depth / 2 - WALL_THICKNESS / 2 - 0.3


# This is the part where we devolve into nonsense :)
def get_painful_screwholder(is_cutout: bool = False):
    zpos = get_back_cover_screw_z_position()
    s1_slot, s1_hole, s1_wall_cutout = get_screw_and_slots(
        FULL_SCREW_DEPTH + SCREW_SLOT_PADDING)
    s1_slot = s1_slot.rotate(Axis.X, 180).translate((
        CASE_X_SIZE / 2,
        0,
        zpos))
    s1_wall_cutout = s1_wall_cutout.rotate(Axis.X, 180).translate((
        CASE_X_SIZE / 2,
        0,
        zpos + FULL_SCREW_DEPTH + WALL_THICKNESS + WALL_THICKNESS - 0.45))  # sure why not

    pad = Rectangle(SCREW_HOLE_DIAMETER + SCREW_SLOT_PADDING,
                    SCREW_HOLE_DIAMETER + SCREW_SLOT_PADDING*2)
    pad = extrude(pad, FULL_SCREW_DEPTH + SCREW_SLOT_PADDING)
    pad = pad.translate((
        CASE_X_SIZE / 2 + SCREW_SLOT_PADDING,
        0,
        zpos - (FULL_SCREW_DEPTH + SCREW_SLOT_PADDING)))

    pad = pad - s1_hole.translate((
        CASE_X_SIZE / 2,
        0,
        zpos - FULL_SCREW_DEPTH - SCREW_SLOT_PADDING + WALL_THICKNESS - 0.5))  # ???

    if is_cutout:
        return s1_wall_cutout
    else:
        return s1_slot + pad - s1_hole


def get_back_cover_screwholders_and_cutouts(is_cutout=False):
    y_offset = get_case_y_size(False) / 2 - \
        WALL_THICKNESS - 2.5  # Arbitrary margin
    slot1 = get_painful_screwholder(is_cutout)
    slot1 = slot1.translate((0, y_offset, 0))

    slot2 = get_painful_screwholder(is_cutout)
    slot2 = slot2.translate((0, -y_offset, 0))
    return slot1 + slot2


def maybe_more_sane_case_screws(as_cutout: bool = False):
    slot, _, cutout = get_screw_and_slots(CASE_Z_SPACE + SCREW_SLOT_PADDING)
    slot = slot.rotate(Axis.X, 180)
    cutout = cutout.rotate(Axis.X, 0)

    # guess not
    margin = 4
    x_pos = -CASE_X_SIZE / 2 + \
        get_case_x_pos_offset(False) * 2 + WALL_THICKNESS + margin
    y_pos1 = get_case_y_size(False) / 2 - WALL_THICKNESS - margin
    z_pos = CASE_Z_SPACE + WALL_THICKNESS
    z_pos_cutout = 0.5  # aaaaaaaaaaaa

    if as_cutout:
        return cutout.translate((x_pos, y_pos1, z_pos_cutout)) + \
            cutout.translate((x_pos, -y_pos1, z_pos_cutout))
    else:
        return slot.translate((x_pos, y_pos1, z_pos)) + \
            slot.translate((x_pos, -y_pos1, z_pos))


def cover_foot_mount_screw_slots():
    _, _, cutout = get_screw_and_slots(CASE_Z_SPACE + SCREW_SLOT_PADDING)
    cutout = cutout.rotate(Axis.X, 90)

    # guess not
    margin_x = 12
    margin_z = 4
    x_pos = -CASE_X_SIZE / 2 + \
        get_case_x_pos_offset(False) * 2 + WALL_THICKNESS + margin_x
    y_pos1 = CASE_Y_SIZE + WALL_THICKNESS - 0.5
    y_pos2 = -WALL_THICKNESS + 0.5
    # z_pos_cutout = 18.5
    z_pos_cutout = WALL_THICKNESS + CASE_Z_SPACE - margin_z

    return cutout.translate((x_pos, y_pos1, z_pos_cutout)) + \
        cutout.translate((x_pos, y_pos2, z_pos_cutout))


def front_cover():
    # Floor base
    fc = Rectangle(get_case_x_size(True), get_case_y_size(True))
    fc = extrude(fc, WALL_THICKNESS)
    fillet_z = fc.edges().filter_by(Axis.Z)
    fc = fillet(fillet_z, radius=CASE_FILLET_RADIUS)
    fc = fc.translate((get_case_x_pos_offset(True), 0, 0))
    # Assemble related objects
    return fc - (pir_hole() + tft_hole()) + \
        get_all_holder_clips() + add_tft_padding() + \
        get_half_y_walls() + get_x_front_cover_walls() + \
        get_back_cover_screwholders_and_cutouts(False) + \
        maybe_more_sane_case_screws(False)


def back_cover():
    # Cutout one X wall for back cover only
    x_size = get_case_x_size(True) - WALL_THICKNESS

    # Base object
    bc = Rectangle(x_size, get_case_y_size(True))
    bc = extrude(bc, WALL_THICKNESS)
    fillet_z = bc.edges().filter_by(Axis.Z)[0:2]
    bc = fillet(fillet_z, radius=CASE_FILLET_RADIUS)
    bc = bc.rotate(Axis.X, 180)
    bc = bc.translate((
        get_case_x_pos_offset(True) - WALL_THICKNESS / 2,
        0,
        WALL_THICKNESS*2 + CASE_Z_SPACE))

    # Position Y walls relative
    y_walls = get_half_y_walls(False, False).translate((
        0,
        0,
        CASE_Z_SPACE / 2))

    # Back cover X bottom wall
    x_wall_z_pos = WALL_THICKNESS + CASE_Z_SPACE / 2
    x_wall = get_x_wall(True, include_wall_thickness=True)
    x_wall = x_wall.translate((
        x_bottom_wall_position(),
        get_case_y_pos_offset(True) - WALL_THICKNESS,
        x_wall_z_pos))
    x_wall_edges = x_wall.edges().filter_by(Axis.Z)[0:2]
    x_wall = fillet(x_wall_edges, radius=CASE_FILLET_RADIUS)
    
    # Antenna hole
    ah = Circle(3.5)
    ah = extrude(ah, WALL_THICKNESS)
    ah = ah.translate((-50,12,WALL_THICKNESS + CASE_Z_SPACE) )

    final_back_cover = bc + y_walls + x_wall - \
        (get_back_cover_screwholders_and_cutouts(
            True) + maybe_more_sane_case_screws(True) + cover_foot_mount_screw_slots())
    if ASSEMBLED_VIEW and ASSEMBLY_VIEW_WITH_OFFSET:
        final_back_cover = final_back_cover.translate((
            ASSEMBLY_VIEW_X_OFFSET,
            0,
            ASSEMBLY_VIEW_Z_OFFSET))
    return final_back_cover - ah

# def foot():
#     foot = Rectangle


def foot_base():
    fb = Rectangle(60, 60)
    fb = extrude(fb, WALL_THICKNESS)
    fb_edges = fb.edges().filter_by(Axis.Z)
    fb = fillet(fb_edges, radius=CASE_FILLET_RADIUS)
    fb_edges = fb.edges().filter_by(Axis.Y)[1]
    fb = fillet(fb_edges, radius=CASE_FILLET_RADIUS)
    fb = fb.translate((
        0,
        0,
        WALL_THICKNESS))

    foot_l = Rectangle(10, WALL_THICKNESS*1.5)
    foot_l = extrude(foot_l, USB_CABLE_OUTSIDE_SPACE+20)
    foot_l = foot_l.translate((
        -5,
        -get_case_y_size(True)/2 - WALL_THICKNESS + 0.1,
        WALL_THICKNESS))
    foot_l = fillet(foot_l.edges(), radius=CASE_FILLET_RADIUS)

    foot_l_hole = Circle(SCREW_HOLE_DIAMETER/2)
    foot_l_hole = extrude(foot_l_hole, WALL_THICKNESS*1.5 + 1)
    foot_l_hole = foot_l_hole.rotate(Axis.X, 90)
    foot_l_hole = foot_l_hole.translate((
        -5,
        -get_case_y_size(True)/2 - WALL_THICKNESS / 2 + 1.5,
        WALL_THICKNESS + USB_CABLE_OUTSIDE_SPACE + 15))

    foot_r = Rectangle(10, WALL_THICKNESS*1.5)
    foot_r = extrude(foot_r, USB_CABLE_OUTSIDE_SPACE+20)
    foot_r = foot_r.translate((
        -5,
        get_case_y_size(True)/2 + WALL_THICKNESS - 0.1,
        WALL_THICKNESS))
    foot_r = fillet(foot_r.edges(), radius=CASE_FILLET_RADIUS)

    foot_r_hole = Circle(SCREW_HOLE_DIAMETER/2)
    foot_r_hole = extrude(foot_r_hole, WALL_THICKNESS*1.5 + 1)
    foot_r_hole = foot_r_hole.rotate(Axis.X, 90)
    foot_r_hole = foot_r_hole.translate((
        -5,
        get_case_y_size(True)/2 + WALL_THICKNESS*2,
        WALL_THICKNESS + USB_CABLE_OUTSIDE_SPACE + 15))

    return fb + foot_l - foot_l_hole + foot_r - foot_r_hole


def foot_final():
    final = foot_base()
    final = final.rotate(Axis.Y, 90)
    final = final.translate((
        -103.3,
        0,
        CASE_Z_SPACE / 2 + 0.5))
    return final


show(front_cover(), back_cover(), foot_final(), reset_camera=Camera.KEEP)
# show(front_cover(), reset_camera=Camera.KEEP)
# show(back_cover(), reset_camera=Camera.KEEP)
# show(foot_final(), reset_camera=Camera.KEEP)

# %%
# Export
front_cover_export = front_cover().solids()[0]
export_model(front_cover_export, f"{PART_NAME}_front")

back_cover_export = back_cover()
export_model(back_cover_export, f"{PART_NAME}_back")

foot_export = foot_final()
export_model(foot_export, f"{PART_NAME}_foot")
# %%
