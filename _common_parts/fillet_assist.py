from build123d import *
from ocp_vscode import *

# Inverse fillet to add to a cutout shape for rounding the outer edges
def get_outer_fillet(length, radius, edge_id=0):
    of_base = Rectangle(length, radius*2)
    of_base = extrude(of_base, radius*2)
    of_edge = of_base.edges().filter_by(Axis.X).sort_by(Axis.Y)[edge_id]
    actual_fillet = fillet(of_edge, radius=radius)
    return of_base - actual_fillet