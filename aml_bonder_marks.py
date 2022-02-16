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
mark_size = 100

# TOP ALIGNMENT MARKS
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

#totalLeft = gdspy.boolean(keepoutLeft, topMarkLeft, 'not')
#totalRight = gdspy.boolean(keepoutRight, topMarkRight, 'not')

cell.add(topMarkLeft)
cell.add(topMarkRight)

# TOP LANDING STRIPS
landing_strip_1 = gdspy.Rectangle((-mark_size/2, 0), (mark_size/2, 4*mm))
landing_strip_2 = gdspy.Rectangle((-mark_size/2, 0), (mark_size/2, -4*mm))
landing_strip_3 = gdspy.Rectangle((0, -mark_size/2), (-4*mm, mark_size/2))
landing_strip_4 = gdspy.Rectangle((0, -mark_size/2), (4*mm, mark_size/2))
landing_strip_5 = gdspy.Rectangle((-mark_size/2, 0), (mark_size/2, 4*mm))
landing_strip_6 = gdspy.Rectangle((-mark_size/2, 0), (mark_size/2, 4*mm))
landing_strip_7 = gdspy.Rectangle((-mark_size/2, 0), (mark_size/2, -4*mm))
landing_strip_8 = gdspy.Rectangle((-mark_size/2, 0), (mark_size/2, -4*mm))

landing_strip_1.translate(-markOffset, mark_size)
landing_strip_2.translate(-markOffset, -mark_size)
landing_strip_3.translate(-markOffset - mark_size, 0)
landing_strip_4.translate(-markOffset + mark_size, 0)
landing_strip_5.rotate(-np.pi/4)
landing_strip_6.rotate(np.pi/4)
landing_strip_7.rotate(-np.pi/4)
landing_strip_8.rotate(np.pi/4)
landing_strip_5.translate(-markOffset + mark_size, mark_size)
landing_strip_6.translate(-markOffset - mark_size, mark_size)
landing_strip_7.translate(-markOffset - mark_size, -mark_size)
landing_strip_8.translate(-markOffset + mark_size, -mark_size)

landing_strips = [landing_strip_1, landing_strip_2, landing_strip_3,
               landing_strip_4, landing_strip_5, landing_strip_6,
               landing_strip_7, landing_strip_8]
for l in landing_strips:
    l_right = gdspy.copy(l, dx=markOffset*2)
    l_bottom = gdspy.copy(l)
    l_bottom.layers = [2]
    l_bottom_right = gdspy.copy(l_bottom, dx=markOffset*2)
    cell.add(l)
    cell.add(l_right)
    cell.add(l_bottom)
    cell.add(l_bottom_right)

radii = np.arange(0.5*mm, 10*mm, 0.1*mm)
landing_circles = [gdspy.Round((0, 0), r, inner_radius=r-25) for r in radii]
for l in landing_circles:
    l_right = gdspy.copy(l, dx=markOffset)
    l_left = gdspy.copy(l, dx=-markOffset)
    l_bottom_left = gdspy.copy(l_left)
    l_bottom_left.layers = [2 for x  in l_bottom_left.layers]
    l_bottom_right = gdspy.copy(l_bottom_left, dx=markOffset*2)
    cell.add(l_right)
    cell.add(l_left)
    cell.add(l_bottom_left)
    cell.add(l_bottom_right)

# BOTTOM ALIGNMENT MARKS


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

gdspy.LayoutViewer(lib)
