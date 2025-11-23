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
WALL_THICKNESS = 2.5
BOARD_ACTUAL_X_SIZE = 68
BOARD_ACTUAL_Y_SIZE = 28

# Base object
base = Rectangle(CASE_X_SIZE, CASE_Y_SIZE)
base = extrude(base, WALL_THICKNESS)


# Z positioned holder clip
def get_board_holder_clip():
    # Bare minimum excluding screen is 6 for space to board minus visible components
    board_zspace_reserved = 7

    # Remaining length of screw after board
    screw_depth = 5.7

    # Screw hole diameter (minimal print resistance, vertical)
    hole_size = 2
    hole_padding = 2

    clip = Circle(hole_size / 2 + hole_padding)
    clip = extrude(clip, board_zspace_reserved)
    clip = clip.translate((0, 0, WALL_THICKNESS))

    hole = Circle(hole_size / 2)
    hole = extrude(hole, screw_depth)
    hole = hole.translate(
        (0, 0, WALL_THICKNESS + board_zspace_reserved - screw_depth))

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
    # Offset of center of the PIR from edge of the case (USB side)
    pir_center_bottom_offset = 14.8
    pir_diameter = 13

    ph = Circle(pir_diameter / 2)
    ph = extrude(ph, WALL_THICKNESS)

    x_pos = -(BOARD_ACTUAL_X_SIZE / 2) + pir_center_bottom_offset
    ph = ph.translate(
        (x_pos, 0, 0))
    return ph


def tft_hole():
    # Nearest edge of TFT to top of board
    tft_top_edge_top_offset = 12.5
    tft_x_size = 13.5
    tft_y_size = 22

    th = Rectangle(tft_x_size, tft_y_size)
    th = extrude(th, WALL_THICKNESS)

    x_pos = (BOARD_ACTUAL_X_SIZE / 2) - \
        (tft_x_size / 2) - tft_top_edge_top_offset
    th = th.translate(
        (x_pos, 0, 0))
    return th


board_slot = base - (pir_hole() + tft_hole()) + get_all_holder_clips()
show(board_slot, reset_camera=False)

# %%
# Export
export_part = base
export_model(export_part, PART_NAME)
# %%
