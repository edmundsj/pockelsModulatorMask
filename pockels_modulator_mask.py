import numpy as np
import gdspy as gdspy
from testStructures import *
from cellFunctions import *
from ASMLBarcodeGenerator import ASMLBarcodeGenerator

# The GDSII file is called a library, which contains multiple cells.
lib = gdspy.GdsLibrary()

# Geometry must be placed in cells.
cell = lib.new_cell('FIRST')

# Create the geometry (a single rectangle) and add it to the cell.

mm=1000
Lgap = 50
traceWidth = 25
traceSpacing = 10
Rdevice = 1000
multiplier = 0.7
ringWidth = 750 * np.array([np.power(multiplier, 1), np.power(multiplier, 2), np.power(multiplier, 3),
        np.power(multiplier, 4), np.power(multiplier, 5), np.power(multiplier,6), np.power(multiplier, 7)])
absoluteOrigin = np.array([0,0])
dieSize = 10*mm
magnificationASML = 4
fieldSize = dieSize * magnificationASML
fieldSpacing = 4.8*mm # minimum allowed ASML field spacing
bondPadSize = 150

device = gdspy.Round(absoluteOrigin, Rdevice)
cell.add(device)

dieBoundary = gdspy.Rectangle([-dieSize/2, -dieSize/2], [dieSize/2, dieSize/2], layer=1)
dieBoundaryInner = gdspy.Rectangle([-dieSize/2 + traceWidth, -dieSize/2 + traceWidth],
        [dieSize/2 - traceWidth, dieSize/2 - traceWidth], layer=1)
dieBoundary0 = gdspy.boolean(dieBoundary, dieBoundaryInner, 'not', layer=0)
dieBoundary1 = gdspy.boolean(dieBoundary, dieBoundaryInner, 'not', layer=1)
dieBoundary2 = gdspy.boolean(dieBoundary, dieBoundaryInner, 'not', layer=2)
cell.add(dieBoundary0)
cell.add(dieBoundary1)
cell.add(dieBoundary2)

cell.add(generateRings(lib, centerWidth=Rdevice*2+Lgap*2, centerHeight=Rdevice*2+Lgap*2,
    traceWidth=traceWidth, traceSpacing=traceSpacing, ringWidth=ringWidth))

deviceToPadTrace = gdspy.Rectangle([-Rdevice + traceSpacing + traceWidth, traceWidth/2],
        [-dieSize/2 + traceSpacing + traceWidth, -traceWidth/2], layer=1)
cell.add(deviceToPadTrace)

deviceRingContact = gdspy.Round((0, 0), Rdevice - traceSpacing, inner_radius=(Rdevice - traceSpacing - traceWidth), layer=1)
cell.add(deviceRingContact)

bondPad = gdspy.Rectangle([-dieSize/2 + traceWidth + traceSpacing, -bondPadSize/2],
        [-dieSize/2 + traceWidth + traceSpacing + bondPadSize, bondPadSize/2], layer=1)
cell.add(bondPad)


# DONE - Resistor test structures
# 1. Contact resistance test structures
# 2. Sheet resistance test structures
# Both these can be done using transmission line structures. These allow us to determine the transfer length, the sheet resistance, and the specific contact resistance. This will only work when we can pattern the underlying semiconductor, which is not the case with the substrate.

cell.add(addCapacitorStructures(lib, offset=[2000, dieSize/2 - traceWidth - traceSpacing]))
cell.add(addTLMStructures(lib, offset=[0, dieSize/2 - traceWidth - traceSpacing]))
cell.add(addTLMStructures(lib, offset=[0, dieSize/2 - traceWidth - traceSpacing - 200], name="TLM2", width=200))

# DONE - Line (exposure) test structures
testLines1 = addTestLines(lib, offset=[-2000, dieSize/2 - traceWidth - traceSpacing], width=0.5, name="LINES0.5")
testLines2 = addTestLines(lib, offset=[-1700, dieSize/2 - traceWidth - traceSpacing], width=2, name="LINES2")
testLines3 = addTestLines(lib, offset=[-1400, dieSize/2 - traceWidth - traceSpacing], width=5, name="LINES5")
testLines4 = addTestLines(lib, offset=[-1100, dieSize/2 - traceWidth - traceSpacing], width=10, name="LINES10")
testLines5 = addTestLines(lib, offset=[-800, dieSize/2 - traceWidth - traceSpacing], width=20, name="LINES20")
testLines = lib.new_cell('LINES')
testLines.add(testLines1)
testLines.add(testLines2)
testLines.add(testLines3)
testLines.add(testLines4)
testLines.add(testLines5)
cell.add(testLines)

cell.add(addTestLines(lib, offset=[-2000, dieSize/2 - traceWidth - traceSpacing-400], width=0.5,
    name="LINES0.5_1", layer=1))
cell.add(addTestLines(lib, offset=[-1700, dieSize/2 - traceWidth - traceSpacing - 400], width=2,
    name="LINES2_1", layer=1))
cell.add(addTestLines(lib, offset=[-1400, dieSize/2 - traceWidth - traceSpacing - 400], width=5,
    name="LINES5_1", layer=1))
cell.add(addTestLines(lib, offset=[-1100, dieSize/2 - traceWidth - traceSpacing - 400], width=10,
    name="LINES10_1", layer=1))
cell.add(addTestLines(lib, offset=[-800, dieSize/2 - traceWidth - traceSpacing - 400], width=20,
    name="LINES20_1", layer=1))

cell.add(addTestLines(lib, offset=[-2000, dieSize/2 - traceWidth - traceSpacing], width=0.5,
    name="LINES0.5_2", layer=2))
cell.add(addTestLines(lib, offset=[-1700, dieSize/2 - traceWidth - traceSpacing], width=2,
    name="LINES2_2", layer=2))
cell.add(addTestLines(lib, offset=[-1400, dieSize/2 - traceWidth - traceSpacing], width=5,
    name="LINES5_2", layer=2))
cell.add(addTestLines(lib, offset=[-1100, dieSize/2 - traceWidth - traceSpacing], width=10,
    name="LINES10_2", layer=2))
cell.add(addTestLines(lib, offset=[-800, dieSize/2 - traceWidth - traceSpacing], width=20,
    name="LINES20_2", layer=2))

# TODO - Focusing pattern (layer 3)
focusingRings = generateRings(lib, centerWidth=4*Rdevice+8*Lgap, offset=[Rdevice+3*Lgap, 0], centerHeight=Rdevice*2+Lgap*2,
    layer=2, name="RINGS_FOCUS", ringWidth=ringWidth)
cell.add(focusingRings)

firstMirror = gdspy.Round([0, 0], Rdevice, layer=2)
focusingMirror = lib.new_cell('focusing_mirror')
focusingMirror.add(firstMirror)
focusingMirror2 = gdspy.CellReference(focusingMirror, [Rdevice*(1+1/2)+Lgap, 0], magnification=1/2.0)
focusingMirror3 = gdspy.CellReference(focusingMirror, [Rdevice*(1+2*1/2+1/4)+2*Lgap, 0], magnification=1/4.0)
focusingMirror4 = gdspy.CellReference(focusingMirror, [Rdevice*(1+2*1/2+2*1/4+1/8)+3*Lgap, 0], magnification=1/8.0)
focusingMirror5 = gdspy.CellReference(focusingMirror, [Rdevice*(1+2*1/2+2*1/4+2*1/8+1/16)+4*Lgap, 0],
        magnification=1/16.0)
focusingMirror6 = gdspy.CellReference(focusingMirror, [Rdevice*(1+2*1/2+2*1/4+2*1/8+2*1/16+1/32)+5*Lgap, 0],
        magnification=1/32.0)
focusingMirror7 = gdspy.CellReference(focusingMirror, [Rdevice*(1+2*1/2+2*1/4+2*1/8+2*1/16+2*1/32+1/64)+6*Lgap, 0],
        magnification=1/64.0)

cell.add(focusingMirror)
cell.add([focusingMirror2, focusingMirror3, focusingMirror4, focusingMirror5, focusingMirror6, focusingMirror7])

# Change polarity of each layer as necessary
myPolygons = cell.get_polygons(by_spec=True)
layer0Coordinates = myPolygons[(0, 0)]
layer1Coordinates = myPolygons[(1, 0)]
layer2Coordinates = myPolygons[(2, 0)]

# FINALLY, IMPORT THE RETICLE TEMPLATE, ADD THE BARCODE, AND 
# ADD OUR EXISTING MASK SCALED AND SHIFTED APPROPRIATELY.
reticleLibrary = gdspy.GdsLibrary()
reticleLibrary.read_gds('asml_templates/asml300-4field_no_lines.gds')
reticleCell = reticleLibrary.cells['reticle_template']

# SEPARATE OUR MASK INTO ITS CONSTITUENT LAYERS, MAGNIFY THEM, AND TRANSLATE THEM.
layer0Cell = gdspy.Cell('LAYER0') # For some reason this is getting converted into a polygonSet when we attempt
# a boolean operation, I'm guessing it's an implicit typecast prior to executing the boolean.
layer1Cell = gdspy.Cell('LAYER1')
layer2Cell = gdspy.Cell('LAYER2')

for coords in layer0Coordinates:
    tempPolygon = gdspy.Polygon(coords, layer=4)
    tempPolygon.scale(4)
    tempPolygon.translate((-fieldSize - fieldSpacing)/2, (fieldSize + fieldSpacing)/2)
    layer0Cell.add(tempPolygon)

# Invert the mask for layer 0
layer0Mask =  gdspy.Rectangle([-fieldSpacing/2, fieldSpacing/2],
        [-fieldSpacing/2 - fieldSize, fieldSpacing/2 + fieldSize])
layer0Cell = gdspy.boolean(layer0Mask, layer0Cell, 'not', layer=4)

for coords in layer1Coordinates:
    tempPolygon = gdspy.Polygon(coords, layer=4)
    tempPolygon.scale(4)
    tempPolygon.translate((fieldSize + fieldSpacing)/2, (fieldSize + fieldSpacing)/2)
    layer1Cell.add(tempPolygon)

for coords in layer2Coordinates:
    tempPolygon = gdspy.Polygon(coords, layer=4)
    tempPolygon.scale(4)
    tempPolygon.translate((-fieldSize - fieldSpacing) / 2, (-fieldSize - fieldSpacing)/2)
    layer2Cell.add(tempPolygon)

layer2Mask = gdspy.Rectangle([-fieldSpacing/2, -fieldSpacing/2],
        [-fieldSpacing/2 - fieldSize, -fieldSpacing/2 - fieldSize])
layer2Cell = gdspy.boolean(layer2Mask, layer2Cell, 'not', layer=4)

layer4Mask = gdspy.Rectangle([fieldSpacing/2, -fieldSpacing/2],
        [fieldSpacing/2 + fieldSize, -fieldSpacing/2 - fieldSize])
layer4Reference = gdspy.CellReference(layer1Cell, (0, -fieldSize -fieldSpacing))
layer4Cell = gdspy.boolean(layer4Mask, layer4Reference, 'not', layer=4)

reticleCell.add(layer0Cell)
reticleCell.add(layer1Cell)
reticleCell.add(layer2Cell)
reticleCell.add(layer4Cell)

# ADD THE BARCODE AND BARCODE TEXT
barcodeCell, textCell = ASMLBarcodeGenerator.generateBarcodeAndText('JEPCKMOD1')
reticleCell.add(barcodeCell)
reticleCell.add(textCell)

# SAVE THE FILE
reticleLibrary.write_gds('jepckmod1.gds')

# Display all cells using the internal viewer.
gdspy.LayoutViewer(reticleLibrary)
