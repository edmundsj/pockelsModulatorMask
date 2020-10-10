import numpy as np
import gdspy
from testStructures import *
from cellFunctions import *

# The GDSII file is called a library, which contains multiple cells.
lib = gdspy.GdsLibrary()

# Units are in microns
mm = 1e3

# Geometry must be placed in cells.
cell = lib.new_cell('FIRST')
markOffset = 58*mm


topMarkLeft = gdspy.Polygon([(-10, 10), (-10, 50), (10, 50), (10, 10), (50, 10), (50, -10), \
        (10, -10), (10, -50), (-10, -50), (-10, -10), (-50, -10), (-50, 10), (-10, 10)])
topMarkRight = gdspy.Polygon([(-10, 10), (-10, 50), (10, 50), (10, 10), (50, 10), (50, -10), \
        (10, -10), (10, -50), (-10, -50), (-10, -10), (-50, -10), (-50, 10), (-10, 10)])
topMarkLeft.translate(-markOffset,0)
topMarkRight.translate(markOffset,0)
keepoutLeft = gdspy.Rectangle((-5*mm, -5*mm), (5*mm, 5*mm))
keepoutRight = gdspy.Rectangle((-5*mm, -5*mm), (5*mm, 5*mm))
keepoutLeft.translate(-markOffset, 0)
keepoutRight.translate(markOffset, 0)

totalLeft = gdspy.boolean(keepoutLeft, topMarkLeft, 'not')
totalRight = gdspy.boolean(keepoutRight, topMarkRight, 'not')

cell.add(totalLeft)
cell.add(totalRight)


# Display all cells using the internal viewer.
#gdspy.LayoutViewer(lib)

bottomLib = gdspy.GdsLibrary()
bottomCell = bottomLib.new_cell('TOP')
print(bottomLib)

squareOffset = 10+5+35/2
bottomSquare = gdspy.Rectangle((-35/2, -35/2), (35/2, 35/2), layer=2)
bottomSquareTR = gdspy.copy(bottomSquare)
bottomSquareTR.translate(squareOffset, squareOffset)
bottomSquareTL = gdspy.copy(bottomSquare)
bottomSquareTL.translate(-squareOffset, squareOffset)
bottomSquareBR = gdspy.copy(bottomSquare)
bottomSquareBR.translate(squareOffset, -squareOffset)
bottomSquareBL = gdspy.copy(bottomSquare)
bottomSquareBL.translate(-squareOffset, -squareOffset)
bottomMark = gdspy.Cell('Bottom Mark')

bottomMark.add(bottomSquareTR)
bottomMark.add(bottomSquareTL)
bottomMark.add(bottomSquareBR)
bottomMark.add(bottomSquareBL)

bottomMarkRight = gdspy.PolygonSet(bottomMark.get_polygons(), layer=2)
bottomMarkLeft = gdspy.copy(bottomMarkRight)

bottomMarkRight.translate(markOffset, 0)
bottomMarkLeft.translate(-markOffset, 0)


cell.add(bottomMarkLeft)
cell.add(bottomMarkRight)
# SAVE THE FILE
lib.write_gds('aml_marks.gds')

#gdspy.LayoutViewer(lib)
