import gdspy
import numpy as np

# The GDSII file is called a library, which contains multiple cells.
lib = gdspy.GdsLibrary()

# Geometry must be placed in cells.
cell = lib.new_cell('FIRST')

# Create the geometry (a single rectangle) and add it to the cell.
#rect = gdspy.Rectangle((0, 0), (2, 1))
rect = gdspy.Rectangle(np.array([0, 0]), np.array([2, 1]))
newCell = lib.new_cell('SECOND')
newCell.add(rect)
cell.add(newCell)

# Save the library in a file called 'first.gds'.
lib.write_gds('first.gds')

# Optionally, save an image of the cell as SVG.
cell.write_svg('first.svg')

# Display all cells using the internal viewer.
gdspy.LayoutViewer()
