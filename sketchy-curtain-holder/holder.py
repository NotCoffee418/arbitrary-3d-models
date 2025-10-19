# %%

# The markers "# %%" separate code blocks for execution (cells)
# Press shift-enter to exectute a cell and move to next cell
# Press ctrl-enter to exectute a cell and keep cursor at the position
# For more details, see https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter

# %%

from build123d import *
from ocp_vscode import *

# %%
# Builder mode

with BuildPart() as bp:
    Box(1, 1, 1)
    fillet(bp.edges(), radius=0.1)

show(bp)

# %%
# Export
exporter = Mesher()
assert bp.part is not None
exporter.add_shape(bp.part)
exporter.write("mypart.3mf")
exporter.write("mypart.stl")
# %%
