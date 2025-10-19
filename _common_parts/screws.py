from build123d import *
from ocp_vscode import *
from bd_warehouse.thread import MetricTrapezoidalThread


def get_screw_base(diameter=8, pitch=1.5, length=20, head_diameter=None, head_height=None):
    """Make a simple flathead screw with metric trapezoidal thread."""

    if head_diameter is None:
        head_diameter = diameter * 1.8
    if head_height is None:
        head_height = diameter * 0.6

    # Metric trapezoidal thread (size format: "DiameterxPitch")
    size = f"{diameter}x{pitch}"
    thread = MetricTrapezoidalThread(
        size=size,
        length=length,
        external=True
    )

    # Flat head
    head = Cylinder(radius=head_diameter/2, height=head_height)
    head = head.move(Location((0, 0, head_height/2)))

    # Center of the screw to connect head and thread
    center = Cylinder(radius=diameter/2 - pitch/2, height=length)
    center = center.move(Location((0, 0, length/2)))

    # Combine
    screw = thread + head + center

    return screw
