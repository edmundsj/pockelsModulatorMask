import numpy as np
import gdspy as gdspy
from itertools import product
from testStructures import *
from cellFunctions import *
from ASMLBarcodeGenerator import ASMLBarcodeGenerator

# The GDSII file is called a library, which contains multiple cells.
lib = gdspy.GdsLibrary()

# Geometry must be placed in cells.
cell = lib.new_cell('FIRST')

mm=1000
Lgap = 50
trace_width = 2 # Width of traces
trace_spacing = 1 # Distance from trace to nearest feature
magnificationASML = 4
die_length = 5*mm
fieldSize = die_length * magnificationASML
fieldSpacing = 4.8*mm # minimum allowed ASML field spacing
text_size = 20 # size of text used on most of the die
die_padding = 400 # amount of space from the edge of the die to important features
pad_size = 120 # bond pad length and width
pad_spacing = 10 # spacing between bond pad duplicates

absoluteOrigin = np.array([0,0])

### BEGIN DEVICE STRUCTURES

device_diameters = [5, 10, 20, 40, 80, 160, 320, 640, 1280]
device_spacing = 1*mm
device_coordinates = [np.array(x)*device_spacing for x in \
                     [(1,1), (0,1),(-1,1),
                       (1,0),(0,0),(-1,0),
                       (-1,-1),(0,-1),(1,-1)]]
# ensure the contacts only take up 1% of device area
ring_contact_spacing = 4 * trace_spacing
ring_contact_width = 4 * trace_width
devices = [gdspy.Round(center, diameter/2) \
        for center, diameter in zip(device_coordinates, device_diameters)]
ito_preserve = [gdspy.Round(
        center,
        diameter/2 + ring_contact_width + ring_contact_spacing,
        layer=1) \
        for center, diameter in zip(device_coordinates, device_diameters)]
ring_contacts = [gdspy.Round(
        center,
        diameter/2 + ring_contact_width + ring_contact_spacing,
        inner_radius= diameter/2 + ring_contact_spacing,
        layer=2) \
        for center, diameter in zip(device_coordinates, device_diameters)]

for r, i, d in zip(ring_contacts, ito_preserve, devices):
    cell.add(d)
    cell.add(i)
    cell.add(r)


dieBoundary = gdspy.Rectangle([-die_length/2, -die_length/2], [die_length/2, die_length/2], layer=1)
dieBoundaryInner = gdspy.Rectangle([-die_length/2 + trace_width, -die_length/2 + trace_width],
        [die_length/2 - trace_width, die_length/2 - trace_width], layer=1)
dieBoundary0 = gdspy.boolean(dieBoundary, dieBoundaryInner, 'not', layer=0)
dieBoundary1 = gdspy.boolean(dieBoundary, dieBoundaryInner, 'not', layer=1)
dieBoundary2 = gdspy.boolean(dieBoundary, dieBoundaryInner, 'not', layer=2)
cell.add(dieBoundary0)
cell.add(dieBoundary1)
cell.add(dieBoundary2)

def bond_pad_group(offset=[0,0], pad_spacing=50, layer=2):

    bond_pad_center = gdspy.Rectangle(
        [offset[0],
            offset[1] - pad_size/2],
        [offset[0] + pad_size,
            offset[1] + pad_size/2],
            layer=layer)

    bond_pad_top = gdspy.Rectangle(
        [offset[0],
            offset[1] - pad_size/2 - pad_spacing - pad_size],
        [offset[0] + pad_size,
            offset[1] + pad_size/2 - pad_spacing - pad_size],
            layer=layer)

    bond_pad_bottom = gdspy.Rectangle(
        [offset[0],
            offset[1] - pad_size/2 + pad_spacing + pad_size],
        [offset[0] + pad_size,
            offset[1] + pad_size/2 + pad_spacing + pad_size],
        layer=layer)

    connector_trace = gdspy.Rectangle(
        [offset[0] + pad_size*2 + trace_spacing,
            offset[1] - pad_spacing - pad_size/2 - pad_size],
        [offset[0] + pad_size*2 + trace_spacing + trace_width,
            offset[1] + pad_size/2 + pad_spacing + pad_size],
        layer=layer)

    connector_top = gdspy.Rectangle(
        [offset[0] + pad_size,
            offset[1] + pad_spacing + pad_size/2 + pad_size/2],
        [offset[0] + pad_size*2 + trace_spacing + trace_width,
            offset[1] + pad_spacing + pad_size/2 + pad_size/2 + \
            trace_width],
        layer=layer)

    connector_middle = gdspy.Rectangle(
        [offset[0] + pad_size,
            offset[1]],
        [offset[0] + pad_size*2 + trace_width,
            offset[1] + trace_width],
        layer=layer)

    connector_bottom = gdspy.Rectangle(
        [offset[0] + pad_size,
            offset[1] - pad_spacing - pad_size/2 - pad_size/2],
        [offset[0] + pad_size*2 + trace_width,
            offset[1] - pad_spacing - pad_size/2 - pad_size/2 + trace_width],
        layer=layer)

    full_polygon_1 = gdspy.boolean(bond_pad_center, bond_pad_top,
            "or", layer=layer)
    full_polygon_2 = gdspy.boolean(bond_pad_bottom, connector_trace,
            "or", layer=layer)
    connector_polygon_1 = gdspy.boolean(connector_top, connector_bottom,
            "or", layer=layer)
    connector_polygon_2 = gdspy.boolean(connector_middle, connector_trace,
            "or", layer=layer)

    connector_polygon = gdspy.boolean(connector_polygon_1,
            connector_polygon_2,
            "or", layer=layer)
    full_polygon = gdspy.boolean(full_polygon_1, full_polygon_2,
            "or", layer=layer)

    full_polygon = gdspy.boolean(full_polygon, connector_polygon,
            "or", layer=layer)
    return full_polygon

pad_locations = [
    [-die_length/2 + die_padding,
    (die_length - die_padding * 2 - pad_size*3 - pad_spacing*2)/2*(1-x/4)] \
                for x in range(9)]
text_locations = [[x[0] + pad_size + trace_spacing,
               x[1] + trace_width + trace_spacing] \
                for x in pad_locations]
bond_groups = [bond_pad_group(offset=loc, pad_spacing=pad_spacing ) \
              for loc in pad_locations]
bond_text = [str(diam) + 'u' for diam in device_diameters]
bond_text_gds = [gdspy.Text(t, text_size, offset, layer=2) \
    for t, offset in zip(bond_text, text_locations)]
for text, group in zip(bond_text_gds, bond_groups):
    cell.add(group)
    cell.add(text)

# Routing traces
for i in range(9):
    distance_from_center = device_diameters[i]/2 + ring_contact_spacing
    if i < 5:
        trace_start_location = device_coordinates[i] + distance_from_center/ np.sqrt(2) * np.array([-1,1])
    else:
        trace_start_location = device_coordinates[i] + distance_from_center / np.sqrt(2) * np.array([-1, -1])

    trace_delta_vector = abs(pad_locations[i] - trace_start_location)
    trace_delta_height = trace_delta_vector[1]
    trace_delta_width = trace_delta_vector[0] - trace_delta_height
    trace_final_location = pad_locations[i]
    trace = gdspy.Path(trace_width, trace_start_location)
    if i < 3:
        trace.segment(trace_delta_height * np.sqrt(2), direction=3/4*np.pi, layer=2)
        trace.turn(trace_width, 1/4*np.pi, layer=2)
        trace.segment(trace_delta_width, direction='-x', layer=2)
    elif i == 3:
        trace.segment(trace_delta_height*2/3 * np.sqrt(2), direction=3/4*np.pi, layer=2)
        trace.turn(trace_width, 1/4*np.pi, layer=2)
        trace.segment(trace_delta_width/3, direction='-x', layer=2)
        trace.turn(trace_width, -1/4*np.pi, layer=2)
        trace.segment(trace_delta_height*1/3 * np.sqrt(2), direction=3/4*np.pi, layer=2)
        trace.turn(trace_width, 1/4*np.pi, layer=2)
        trace.segment(trace_delta_width*2/3, direction='-x', layer=2)
    elif i == 4:
        trace.segment(1/3*mm * np.sqrt(2), direction=3/4*np.pi, layer=2)
        trace.turn(trace_width, 1/4*np.pi, layer=2)
        trace.segment(trace_delta_width*2/3 - 2/3*mm, direction='-x', layer=2)
        trace.turn(trace_width, -1/4*np.pi, layer=2)
        trace.segment((trace_delta_height + 1/3*mm)*np.sqrt(2), direction=-3/4*np.pi, layer=2)
        trace.turn(trace_width, 1/4*np.pi, layer=2)
        trace.segment(trace_delta_width*1/3, direction='-x', layer=2)
    elif i >= 5:
        trace.segment(trace_delta_height * np.sqrt(2), direction=-3/4*np.pi, layer=2)
        trace.turn(trace_width, 1/4*np.pi, layer=2)
        trace.segment(trace_delta_width, direction='-x', layer=2)

    cell.add(trace)

### END DEVICE STRUCTURES ###

### BEGIN TEST STRUCTURES ###

# ELECTRICAL TEST STRUCTURES - capacitor and contact resistance
cell.add(addCapacitorStructures(lib, width=[200,400],
            offset=[1700, die_length/2 - die_padding-1000], name="CAPS1"))
cell.add(addCapacitorStructures(lib, width=[200,400],
            offset=[1700, die_length/2 - die_padding -1500], name="CAPS2"))
cell.add(addCapacitorStructures(lib, width=[200,400],
            offset=[1700, die_length/2 - die_padding -1500], name="CAPS3", layer=1))
cell.add(addTLMStructures(lib, offset=[500, die_length/2 - die_padding]))
cell.add(addTLMStructures(lib, offset=[500, die_length/2 - die_padding - 200], name="TLM2", width=200))

# LITHOGRAPHIC TEST STRUCTURES - lines
test_widths = [0.5, 2, 5, 10]
test_lines = [addTestLines(lib,
        offset=[-1700 + 300*i, die_length/2-50],
        width=x,
        name='LINES' + str(x),
        layer=0) \
        for i, x in enumerate(test_widths)]
test_line_cell = lib.new_cell('LINES')
for line in test_lines:
    test_line_cell.add(line)
cell.add(test_line_cell)


cell.add(addTestLines(lib, offset=[-200, die_length/2-50], width=0.5,
    name="LINES0.5_1", layer=1))
cell.add(addTestLines(lib, offset=[100, die_length/2-50], width=2,
    name="LINES2_1", layer=1))
cell.add(addTestLines(lib, offset=[400, die_length/2-50], width=5,
    name="LINES5_1", layer=1))
cell.add(addTestLines(lib, offset=[700, die_length/2-50], width=10,
    name="LINES10_1", layer=1))

cell.add(addTestLines(lib, offset=[1000, die_length/2-50], width=0.5,
    name="LINES0.5_2", layer=2))
cell.add(addTestLines(lib, offset=[1300, die_length/2-50], width=2,
    name="LINES2_2", layer=2))
cell.add(addTestLines(lib, offset=[1600, die_length/2 - 50], width=5,
    name="LINES5_2", layer=2))
cell.add(addTestLines(lib, offset=[1900, die_length/2 - 50], width=10,
    name="LINES10_2", layer=2))

lib.write_gds('jepckmod2_core.gds')

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
#layer0Cell = gdspy.boolean(layer0Mask, layer0Cell, 'not', layer=4)

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

# BARCODE AND BARCODE TEXT
barcodeCell, textCell = ASMLBarcodeGenerator.generateBarcodeAndText('JEPCKMOD2')
reticleCell.add(barcodeCell)
reticleCell.add(textCell)

# SAVE THE FILE
reticleLibrary.write_gds('jepckmod2.gds')

# Display all cells using the internal viewer.
#gdspy.LayoutViewer(reticleLibrary)
