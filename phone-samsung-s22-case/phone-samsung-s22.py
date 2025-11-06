# %%
# type: ignore
# CTRL+Shift+P > OCP CAD VIEWER: Open CAD Viewer

# The markers "# %%" separate code blocks for execution (cells)
# Press shift-enter to execute a cell and move to next cell
# Press ctrl-enter to execute a cell and keep cursor at the position
# For more details, see https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter

# %%
# Imports and config
from build123d import *
from ocp_vscode import *
import os

# Import common parts - comment these out if not available
# import sys
# from pathlib import Path
# sys.path.insert(0, str(Path(__file__).parent.parent))
# from _common_parts.screws import *  # noqa: E402
# from _common_parts.export import export_model  # noqa: E402

# Used to name the exported files
PART_NAME = "s22_case"

# %%
# Samsung S22 dimensions from our measurements
# Phone dimensions (with camera bump)
phone_height = 146.2  # mm
phone_width = 70.6   # mm (without volume buttons)
phone_depth = 7.5    # mm (without camera bump)

# Case parameters
wall_thickness = 1.6  # mm on all sides
corner_radius = 5   # mm est 4.8 consensus but clearance and likely wrongness
edge_radius = 1.0     # mm for edge filleting

# Comfort fillet
comfort_fillet = 1

# Lip that holds the phone in - reduced thickness
lip_height = 0.6  # mm - thinner lip
# mm - radius for the curved profile (smaller, more realistic)
lip_radius = 1.5

# Calculate outer case dimensions
case_height = phone_height + (2 * wall_thickness)
case_width = phone_width + (2 * wall_thickness)
# front side too, we cut out part
case_depth = phone_depth + (2 * wall_thickness)

print(f"Phone dimensions: {phone_height} x {phone_width} x {phone_depth}")
print(f"Case outer dimensions: {case_height} x {case_width} x {case_depth}")


# Create the case in Algebra mode

# Create outer shell - rounded rectangle for the case
outer_shell = RectangleRounded(case_width, case_height, corner_radius)
outer_shell = extrude(outer_shell, case_depth)

# Round bottom edge for comfort
outer_shell = fillet(outer_shell.edges(), comfort_fillet)


# Create phone cavity - what we subtract from the shell
# Make cavity slightly larger for clearance
clearance = 0.2  # mm extra space for phone to fit
cavity_width = phone_width + clearance
cavity_height = phone_height + clearance
cavity_depth = phone_depth + clearance


# Position cavity at top of case (leaving wall at bottom)
cavity = RectangleRounded(cavity_width, cavity_height,
                          corner_radius - wall_thickness)
cavity = extrude(cavity, cavity_depth)
cavity = cavity.move(Location((0, 0, wall_thickness)))
cavity = fillet(cavity.edges(), comfort_fillet)

# Create a cutout for the screen, leaving a lip
screen_cutout_width = phone_width - 2 * lip_height
screen_cutout_height = phone_height - 2 * lip_height
screen_cutout_radius = corner_radius - lip_height

screen_cutout = RectangleRounded(
    screen_cutout_width, screen_cutout_height, screen_cutout_radius
)
# Extrude through the front wall of the case
screen_cutout = extrude(screen_cutout, wall_thickness + clearance)
# Position screen cutout at the front of the case
screen_cutout = screen_cutout.move(
    Location((0, 0, phone_depth + wall_thickness)))


# Subtract cavity from shell
phone_case = outer_shell - cavity - screen_cutout

# Round the inner lip
try:
    front_face = max(
        phone_case.faces().filter_by(
            lambda f: f.normal_at(f.center()).is_parallel(Vector(0, 0, 1))
        ),
        key=lambda f: f.center().Z,
    )
    lip_edges = []
    wires_by_area = front_face.wires().sort_by_area()
    for wire in wires_by_area[1:]:
        lip_edges.extend(wire.edges())
    if lip_edges:
        phone_case = phone_case.fillet(0.35, lip_edges)
except Exception as e:
    print(f"Failed to fillet lip: {e}")

# Add cutouts for ports and buttons

# Bottom cutout for charging port (USB-C centered)
charging_width = 14  # mm - wide enough for cable
charging_height = wall_thickness + 2  # through the wall
charging_depth = 8  # mm

charging_cutout = Box(charging_width, charging_depth, charging_height, align=(
    Align.CENTER, Align.CENTER, Align.MIN))
charging_cutout = charging_cutout.move(
    Location((0, -case_height/2 + wall_thickness/2, case_depth/2)))

phone_case = phone_case - charging_cutout

# Side cutout for volume buttons (left side when looking at back)
volume_cutout_width = wall_thickness + 2  # through the wall
volume_cutout_height = 25  # mm - length of volume rocker
volume_cutout_depth = 5  # mm - how deep into case

volume_cutout = Box(volume_cutout_width, volume_cutout_height, volume_cutout_depth,
                    align=(Align.CENTER, Align.CENTER, Align.CENTER))
# Position at left side, slightly up from center
volume_cutout = volume_cutout.move(
    Location((-case_width/2 + wall_thickness/2, 15, case_depth/2)))

phone_case = phone_case - volume_cutout

# Side cutout for power button (right side when looking at back)
power_cutout_width = wall_thickness + 2  # through the wall
power_cutout_height = 12  # mm - power button size
power_cutout_depth = 5  # mm

power_cutout = Box(power_cutout_width, power_cutout_height, power_cutout_depth,
                   align=(Align.CENTER, Align.CENTER, Align.CENTER))
# Position at right side, slightly up from center
power_cutout = power_cutout.move(
    Location((case_width/2 - wall_thickness/2, 10, case_depth/2)))

phone_case = phone_case - power_cutout

# Camera cutout (big rectangle for camera area)
camera_width = 40  # mm - camera island width
camera_height = 35  # mm - camera island height
camera_depth = wall_thickness + 2  # through the back wall

camera_cutout = RectangleRounded(camera_width, camera_height, 3)
camera_cutout = extrude(camera_cutout, camera_depth)
# Position at top-left when looking at back
camera_cutout = camera_cutout.move(Location((-15, 45, -1)))

phone_case = phone_case - camera_cutout

# Create an inclined cut for the lip using loft
lip_incline_depth = 1.0  # Depth of the incline
lip_incline_width = 1.5  # Width of the incline area

# Create bottom face (deeper into case - smaller, same as screen cutout)
bottom_rect = RectangleRounded(
    screen_cutout_width,
    screen_cutout_height,
    screen_cutout_radius
)
# Start at Z=0

# Create top face (at the very top of the case - larger)
top_rect = RectangleRounded(
    screen_cutout_width + 2 * lip_incline_width,
    screen_cutout_height + 2 * lip_incline_width,
    screen_cutout_radius
)
top_rect = top_rect.move(Location((0, 0, lip_incline_depth)))

# Loft between the two rectangles to create the inclined surface
# Now goes from smaller (bottom) to larger (top)
lip_incline = loft([bottom_rect, top_rect])

# Position the inclined cut at the front of the case
# Bottom face should be about 0.5mm below the top surface, top face extends above
lip_incline = lip_incline.move(
    Location((0, 0, case_depth - 0.5))
)

# Subtract the inclined cut from the phone case
phone_case = phone_case - lip_incline

# Add nice edge filleting for comfort
try:
    # Fillet outer edges for smooth feel
    edges_to_fillet = phone_case.edges().filter_by(GeomType.LINE)
    phone_case = fillet(edges_to_fillet, radius=edge_radius)
except:
    print("Filleting failed, continuing without fillets")
    pass

# Show the result
show(phone_case, reset_camera=False)
# %%
# Export
export_part = base
export_model(export_part, PART_NAME)
# %%
