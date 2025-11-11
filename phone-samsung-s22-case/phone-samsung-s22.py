# %%
# type: ignore
# CTRL+Shift+P > OCP CAD VIEWER: Open CAD Viewer

# The markers "# %%" separate code blocks for execution (cells)
# Press shift-enter to execute a cell and move to next cell
# Press ctrl-enter to execute a cell and keep cursor at the position
# For more details, see https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter

# %%
# Imports and config
from build123d import fillet as fillet_edges
from build123d import *
from ocp_vscode import *
import os
import sys

# Import common parts - comment these out if not available
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from _common_parts.screws import *  # noqa: E402
from _common_parts.export import export_model  # noqa: E402

# Used to name the exported files
PART_NAME = "s22_case"

# %%
# Samsung S22 dimensions from our measurements
# Phone dimensions (with camera bump)
# These may be adjusted based on actual tightness fit
phone_height = 145.8  # mm
phone_width = 70   # mm (without volume buttons)
phone_depth = 8    # mm (without camera bump)

# Case parameters
wall_thickness = 1.2  # mm on all sides
corner_radius = 9.6   # mm est 4.8 consensus but clearance and likely wrongness
edge_radius = 1.0     # mm for edge filleting

# Comfort fillet
comfort_fillet = 1

# Offset for side cutouts in Z direction (positive = higher)
cutout_z_offset = 1  # mm

# Bulge amount for curved sides (outward curvature)
side_bulge = 0.8  # mm - how much the sides bulge outward at the middle

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

# Create outer shell with bulging sides using loft
# Bottom profile
bottom_profile = RectangleRounded(case_width, case_height, corner_radius)

# Middle profile (bulged out)
middle_profile = RectangleRounded(
    case_width + 2 * side_bulge,
    case_height + 2 * side_bulge,
    corner_radius
)
middle_profile = middle_profile.move(Location((0, 0, case_depth / 2)))

# Top profile
top_profile = RectangleRounded(case_width, case_height, corner_radius)
top_profile = top_profile.move(Location((0, 0, case_depth)))

# Loft between profiles to create bulged sides
outer_shell = loft([bottom_profile, middle_profile, top_profile])

# Round bottom edge for comfort
outer_shell = fillet(outer_shell.edges(), comfort_fillet)


# Create phone cavity - what we subtract from the shell
# Make cavity slightly larger for clearance=
clearance = 0.2

cavity_width = phone_width + clearance
cavity_height = phone_height + clearance
cavity_depth = phone_depth + clearance


# Position cavity at top of case (leaving wall at bottom) with bulging sides
cavity_base_z = wall_thickness

# Bottom profile
cavity_bottom = RectangleRounded(
    cavity_width, cavity_height, corner_radius - wall_thickness
)
cavity_bottom = cavity_bottom.move(Location((0, 0, cavity_base_z)))

# Middle profile (bulged)
cavity_middle = RectangleRounded(
    cavity_width + 2 * side_bulge,
    cavity_height + 2 * side_bulge,
    corner_radius - wall_thickness
)
cavity_middle = cavity_middle.move(
    Location((0, 0, cavity_base_z + cavity_depth / 2)))

# Top profile
cavity_top = RectangleRounded(
    cavity_width, cavity_height, corner_radius - wall_thickness
)
cavity_top = cavity_top.move(Location((0, 0, cavity_base_z + cavity_depth)))

# Loft to create bulged cavity
cavity = loft([cavity_bottom, cavity_middle, cavity_top])
cavity = fillet(cavity.edges(), comfort_fillet)

# Create a cutout for the screen, leaving a lip
lip_overhang = 3
screen_cutout_width = phone_width - lip_overhang * lip_height
screen_cutout_height = phone_height - lip_overhang * lip_height
screen_cutout_radius = corner_radius - lip_height

# Create screen cutout with bulging sides using loft
screen_base_z = phone_depth + wall_thickness
cutout_depth = wall_thickness + clearance

# Bottom profile (at the base)
screen_bottom = RectangleRounded(
    screen_cutout_width, screen_cutout_height, screen_cutout_radius
)
screen_bottom = screen_bottom.move(Location((0, 0, screen_base_z)))

# Middle profile (bulged)
screen_middle = RectangleRounded(
    screen_cutout_width + 2 * side_bulge,
    screen_cutout_height + 2 * side_bulge,
    screen_cutout_radius
)
screen_middle = screen_middle.move(
    Location((0, 0, screen_base_z + cutout_depth / 2)))

# Top profile
screen_top = RectangleRounded(
    screen_cutout_width, screen_cutout_height, screen_cutout_radius
)
screen_top = screen_top.move(Location((0, 0, screen_base_z + cutout_depth)))

# Loft to create bulged screen cutout
screen_cutout = loft([screen_bottom, screen_middle, screen_top])


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
# Note this also has mic hole
charging_width = 16  # mm - USB-C standard width
charging_height = 6  # mm - USB-C standard height
charging_depth = wall_thickness + 2  # through the wall
charging_x_offset = -2.5  # from center

charging_cutout = Box(charging_width, charging_depth, charging_height,
                      align=(Align.CENTER, Align.MIN, Align.CENTER))
# Round with 2mm radius for comfortable cable insertion
charging_cutout = fillet(charging_cutout.edges().filter_by(Axis.Y), 2.0)
charging_cutout = charging_cutout.move(
    Location((charging_x_offset, -case_height/2 - 1, case_depth/2 + cutout_z_offset)))

phone_case = phone_case - charging_cutout

# Speaker/mic hole on bottom right
speaker_width = 12  # mm
speaker_height = 5  # mm
speaker_depth = wall_thickness + 2  # through the wall
speaker_x_offset = 55  # mm from left edge

speaker_cutout = Box(speaker_width, speaker_depth, speaker_height,
                     align=(Align.CENTER, Align.MIN, Align.CENTER))
speaker_cutout = fillet(speaker_cutout.edges().filter_by(Axis.Y), 1.5)
speaker_cutout = speaker_cutout.move(
    Location((-case_width/2 + speaker_x_offset, -case_height/2 - 1, case_depth/2 + cutout_z_offset)))

phone_case = phone_case - speaker_cutout

# Microphone hole on bottom (opposite side from USB, at top edge)
mic_diameter = 3  # mm
mic_depth = wall_thickness + 2  # through the wall

mic_cutout = Cylinder(
    radius=mic_diameter / 2,
    height=mic_depth,
    align=(Align.CENTER, Align.CENTER, Align.MIN)
)
# Rotate to point along Y axis (into the top edge)
mic_cutout = mic_cutout.rotate(Axis.X, 90)
# Position at X=8 on the TOP edge
mic_cutout = mic_cutout.move(
    Location((8, case_height/2 + 1, case_depth/2 + cutout_z_offset)))

phone_case = phone_case - mic_cutout

# Side cutout for volume buttons (RIGHT side when looking at back)
volume_cutout_height = 20  # mm - length of volume rocker
volume_cutout_depth = 4  # mm - how deep into case
volume_cutout_width = wall_thickness + 2  # through the wall
volume_button_y_offset = -47.5  # from top edge

volume_cutout = Box(volume_cutout_width, volume_cutout_height, volume_cutout_depth,
                    align=(Align.MAX, Align.CENTER, Align.CENTER))
volume_cutout = fillet(volume_cutout.edges().filter_by(Axis.X), 1.5)
volume_cutout = volume_cutout.move(
    Location((case_width/2 + 1, case_height/2 + volume_button_y_offset, case_depth/2 + cutout_z_offset)))

phone_case = phone_case - volume_cutout

# Side cutout for power button (RIGHT side when looking at back)
power_cutout_height = 12  # mm - power button size
power_cutout_depth = 3.5  # mm
power_cutout_width = wall_thickness + 2  # through the wall
power_button_y_offset = -70  # from top edge

power_cutout = Box(power_cutout_width, power_cutout_height, power_cutout_depth,
                   align=(Align.MAX, Align.CENTER, Align.CENTER))
power_cutout = fillet(power_cutout.edges().filter_by(Axis.X), 1.5)
power_cutout = power_cutout.move(
    Location((case_width/2 + 1, case_height/2 + power_button_y_offset, case_depth/2 + cutout_z_offset)))

phone_case = phone_case - power_cutout

# Camera cutout (rounded rectangle at top-left corner)
camera_width = 21.5  # mm - camera island width (X direction)
camera_height = 49.2  # mm - camera island height (Y direction)
camera_depth = wall_thickness + 2  # through the back wall

# Create rectangle with two rounded corners and two sharp corners
camera_base = Rectangle(camera_width, camera_height)
camera_cutout = extrude(camera_base, camera_depth)

# Fillet two corners, and the other two with minimal
edges = camera_cutout.edges().filter_by(Axis.Z)
top_left_edges = [e for e in edges if e.center().X < 0 and e.center().Y > 0]
bottom_right_edges = [e for e in edges if e.center().X >
                      0 and e.center().Y < 0]

camera_cutout = fillet(top_left_edges + bottom_right_edges, 0.5)

top_right_edges = [e for e in camera_cutout.edges().filter_by(
    Axis.Z) if e.center().X > 0 and e.center().Y > 0]
bottom_left_edges = [e for e in camera_cutout.edges().filter_by(
    Axis.Z) if e.center().X < 0 and e.center().Y < 0]

camera_cutout = fillet(top_right_edges + bottom_left_edges, corner_radius)

# Position at top-left corner accounting for wall thickness
camera_x_offset = case_width/2 - camera_width/2 - wall_thickness - 2
camera_y_offset = case_height/2 - camera_height/2 - wall_thickness - 2

camera_cutout = camera_cutout.move(
    Location((camera_x_offset, camera_y_offset, -1)))

phone_case = phone_case - camera_cutout

# Flashlight cutout (circular, tapered from 5mm to 6mm diameter)
flashlight_diameter_top = 6  # mm - at the back surface
flashlight_diameter_bottom = 6.1  # mm - at the inner surface
flashlight_depth = wall_thickness + 2  # through the back wall

flashlight_x_offset = phone_width / 2 - 27
flashlight_y_offset = phone_height / 2 - 12

# Create a tapered cone for flashlight
flashlight_cutout = Cone(
    bottom_radius=flashlight_diameter_bottom / 2,
    top_radius=flashlight_diameter_top / 2,
    height=flashlight_depth,
    align=(Align.CENTER, Align.CENTER, Align.MIN)
)

flashlight_cutout = flashlight_cutout.move(
    Location((flashlight_x_offset, flashlight_y_offset, -1))
)

phone_case = phone_case - flashlight_cutout

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

# Add nice edge filleting for comfort - with better filtering
try:
    # Only fillet specific edges to avoid conflicts
    # Get vertical edges (Z-axis aligned) on the outer perimeter
    vertical_edges = phone_case.edges().filter_by(Axis.Z)

    # Filter to only outer edges (not internal cutout edges)
    outer_edges = [e for e in vertical_edges if abs(
        e.center().X) > case_width/2 - 0.5 or abs(e.center().Y) > case_height/2 - 0.5]

    if outer_edges:
        phone_case = fillet(outer_edges, radius=edge_radius)
except Exception as e:
    print(f"Filleting failed: {e}, continuing without fillets")

# Show the result
show(phone_case, reset_camera=False)
# %%


# # Export
export_model(phone_case, PART_NAME)
# # %%rt_model(export_part, PART_NAME)
# # %%

# %%
