# %%
# type: ignore
# CTRL+Shift+P > OCP CAD VIEWER: Open CAD Viewer

# The markers "# %%" separate code blocks for execution (cells)
# Press shift-enter to exectute a cell and move to next cell
# Press ctrl-enter to exectute a cell and keep cursor at the position
# For more details, see https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter

# %%
# Imports and config
from bd_warehouse.thread import IsoThread
from build123d import *
from ocp_vscode import *

# Import common parts
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from _common_parts.screws import *  # noqa: E402
from _common_parts.export import export_model  # noqa: E402

# Used to name the exported files
PART_NAME = "hose_soap_container"

# %%
# Algebra mode.

# --- CONSTANTS ---
SCREW_MAJOR_DIAMETER = 48.5
SCREW_PITCH = 5.0
SCREW_LENGTH = 10.0
SCREW_CORE_DIAMETER = 46.5

SEPERATOR_HEIGHT = 4
SEPERATOR_DIAMETER = 51

CONTAINER_DIAMETER = 45
# CONTAINER_HEIGHT = 80  # real value
CONTAINER_HEIGHT = 15  # test print


CONTAINER_WALL_THICKNESS = 4


def get_container_screw():
    """
    Makes the threaded stud for the container.
    No head, just the threaded cylinder.
    """
    # We use 'chamfer' on the bottom so it's easy to screw into the lid
    # We use 'square' on the top so it sits flush against the container wall
    end_finishes = ("chamfer", "square")

    # Create the ISO thread
    # major_diameter is the outer width (48.5)
    thread = IsoThread(
        major_diameter=SCREW_MAJOR_DIAMETER,
        pitch=SCREW_PITCH,
        length=SCREW_LENGTH,
        external=True,
        end_finishes=end_finishes,
        interference=0.1
    )

    # Create the core (the solid part inside the threads)
    # We use the CORE_DIAMETER to ensure the 'valleys' of the thread are solid
    core = Cylinder(
        radius=SCREW_CORE_DIAMETER / 2,
        height=SCREW_LENGTH
    )

    # Move core so it starts at Z=0 and goes up to SCREW_LENGTH
    core = core.move(Location((0, 0, SCREW_LENGTH/2)))

    # Combine: The thread is the 'skin', the core is the 'meat'
    # We use '+' to union them into one single solid part
    screw_stud = thread + core

    return screw_stud


def get_separator() -> Solid:
    """Return an additional cylindrical separator that sits directly on top of the screw."""
    # A simple cylinder – adjust dimensions as needed.
    sep = Cylinder(radius=SEPERATOR_DIAMETER/2, height=SEPERATOR_HEIGHT)

    # Position it exactly at the top of the screw (SCREW_LENGTH).
    sep = sep.move(Location((0, 0, SCREW_LENGTH + SEPERATOR_HEIGHT/2)))

    return sep


def get_soap_container() -> Solid:
    """
    Creates the top container part.
    Positioned directly on top of the separator.
    """
    # Create the cylinder for the soap container
    # We use the diameter and height provided by constants
    container = Cylinder(
        radius=CONTAINER_DIAMETER / 2,
        height=CONTAINER_HEIGHT
    )

    # Position it so its BOTTOM face sits at the TOP of the separator.
    # The top of the separator is at Z = SCREW_LENGTH + SEPERATOR_HEIGHT
    z_start_position = SCREW_LENGTH + SEPERATOR_HEIGHT

    # Move the cylinder so its base is at the calculated Z position
    container = container.move(
        Location((0, 0, z_start_position + CONTAINER_HEIGHT / 2)))

    return container


def get_container_cutout() -> Solid:
    """
    Creates the cylinder used to hollow out the assembly.
    The height is adjusted to leave a floor at the bottom.
    """
    # The total height of the entire object (from Z=0 to top)
    total_assembly_height = SCREW_LENGTH + SEPERATOR_HEIGHT + CONTAINER_HEIGHT

    # The height of our 'drill bit' (the cutout cylinder)
    # It starts at the top and goes down to the floor level.
    cutout_height = total_assembly_height - CONTAINER_WALL_THICKNESS

    # Note: If you want the hole to go all the way through the screw/separator too,
    # we just make sure it's long enough to reach the bottom of the container.

    cutout_radius = (CONTAINER_DIAMETER / 2) - CONTAINER_WALL_THICKNESS

    # Create the cylinder
    cutout = Cylinder(radius=cutout_radius, height=cutout_height)

    cutout = cutout.move(
        Location((0, 0, -CONTAINER_WALL_THICKNESS/2 + total_assembly_height/2)))

    return cutout


# Combine everything
final = (get_container_screw() + get_separator() +
         get_soap_container()) - get_container_cutout()


# show([base, dent_l, dent_r]) # Preview with removed part visible
show(final, reset_camera=False)

# %%
# Export
export_part = final
export_model(export_part, PART_NAME)
# %%
