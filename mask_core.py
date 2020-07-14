import numpy as np
import gdspy as gdspy
from jordanGDS import *

# The GDSII file is called a library, which contains multiple cells.
lib = gdspy.GdsLibrary()

# Geometry must be placed in cells.
cell = lib.new_cell('FIRST')

# Create the geometry (a single rectangle) and add it to the cell.

Lgap = 50
traceWidth = 25
traceSpacing = 10
Rdevice = 1000
multiplier = 0.7
ringLength = 750 * np.array([np.power(multiplier, 1), np.power(multiplier, 2), np.power(multiplier, 3),
        np.power(multiplier, 4), np.power(multiplier, 5), np.power(multiplier,6), np.power(multiplier, 7)])
absoluteOrigin = np.array([0,0])
dieSize = 10000
bondPadSize = 150

device = gdspy.Round(absoluteOrigin, Rdevice)
cell.add(device)

dieBoundary = gdspy.Rectangle([-dieSize/2, -dieSize/2], [dieSize/2, dieSize/2], layer=1)
dieBoundaryInner = gdspy.Rectangle([-dieSize/2 + traceWidth, -dieSize/2 + traceWidth],
        [dieSize/2 - traceWidth, dieSize/2 - traceWidth], layer=1)
dieBoundary = gdspy.boolean(dieBoundary, dieBoundaryInner, 'not', layer=1)
cell.add(dieBoundary)

for i in range(len(ringLength)):

    outerHalfLength = Rdevice + Lgap + np.sum(ringLength[0:i+1]) + np.sum(ringLength[0:i])
    innerHalfLength = Rdevice + Lgap + 2*np.sum(ringLength[0:i])

    outerPoints = np.array([[-outerHalfLength, -outerHalfLength],
        [-outerHalfLength, outerHalfLength],
        [outerHalfLength, outerHalfLength],
        [outerHalfLength, -outerHalfLength]])

    innerPoints = np.array([[-innerHalfLength, -innerHalfLength],
        [-innerHalfLength, innerHalfLength],
    [innerHalfLength, innerHalfLength],
    [innerHalfLength, -innerHalfLength]])

    cutoutPoints = np.array([[-innerHalfLength, traceSpacing + traceWidth/2],
        [-outerHalfLength, traceSpacing + traceWidth/2],
        [-outerHalfLength, -traceSpacing -traceWidth/2],
        [-innerHalfLength, -traceSpacing -traceWidth/2]])

    ringOuter = gdspy.Polygon(outerPoints)
    ringInner = gdspy.Polygon(innerPoints)
    ringCutout = gdspy.Polygon(cutoutPoints)
    ring = gdspy.boolean(ringOuter, ringInner, 'not')
    ring = gdspy.boolean(ring, ringCutout, 'not', layer=1)

    cell.add(ring)

trace = gdspy.Rectangle([-Rdevice + traceSpacing + traceWidth, traceWidth/2],
        [-dieSize/2 + traceSpacing + traceWidth, -traceWidth/2], layer=1)
cell.add(trace)

contact = gdspy.Round((0, 0), Rdevice - traceSpacing, inner_radius=(Rdevice - traceSpacing - traceWidth), layer=1)
cell.add(contact)

bondPad = gdspy.Rectangle([-dieSize/2 + traceWidth + traceSpacing, -bondPadSize/2],
        [-dieSize/2 + traceWidth + traceSpacing + bondPadSize, bondPadSize/2], layer=1)
cell.add(bondPad)


# DONE - Resistor test structures
# 1. Contact resistance test structures
# 2. Sheet resistance test structures
# Both these can be done using transmission line structures. These allow us to determine the transfer length, the sheet resistance, and the specific contact resistance. This will only work when we can pattern the underlying semiconductor, which is not the case with the substrate.

cell.add(addCapacitorStructures(lib, offset=[2000, dieSize/2 - traceWidth - traceSpacing]))
cell.add(addTLMStructures(lib, offset=[0, dieSize/2 - traceWidth - traceSpacing]))

# TODO - Line (exposure) test structures

# TODO - Focusing pattern (layer 3)

# Save the library in a file called 'first.gds'.
lib.write_gds('first.gds')

# Optionally, save an image of the cell as SVG.
cell.write_svg('first.svg')

# Display all cells using the internal viewer.
gdspy.LayoutViewer()
