import gdspy
import numpy as np

def addTLMStructures(lib, width=100, spacing=[50,100,150,200], padding=5, name="TLM",
        offset=[0,0], alignment='top', textSize=50):
    print(name)
    tempCell = lib.new_cell(name)
    if alignment == 'top':
        for i in range(len(spacing)+1):
            if(i<len(spacing)):
                texti = gdspy.Text(str(spacing[i]) + 'u', textSize,
                        [offset[0] + i*width + sum(spacing[0:i]) + width/2 + spacing[i]/2, offset[1] - textSize],
                        layer=1)
                tempCell.add(texti)

            contacti = gdspy.Rectangle(
                    [offset[0] + padding + i*width + sum(spacing[0:i]), offset[1] - padding - textSize],
                    [offset[0] + padding + (i+1)*width + sum(spacing[0:i]), offset[1] - textSize - padding - width], layer=1)
            tempCell.add(contacti)

        filmRegion = gdspy.Rectangle([offset[0], offset[1] - textSize],
            [offset[0] + 2*padding + 5*width + sum(spacing), offset[1] - textSize - 2*padding - width], layer=0)
        widthText = gdspy.Text(str(width) + 'u', textSize,
            [offset[0] - textSize*4, offset[1] - textSize - width/2], layer=1)
        tempCell.add(filmRegion)
        tempCell.add(widthText)

        return tempCell
    else:
        raise NotImplementedError

def addCapacitorStructures(lib, width=[50,100,200,400,800], spacing=100, name="CAPS",
        offset=[0,0], alignment='top', textSize=50):

    tempCell = lib.new_cell(name)
    if alignment == 'top':
        for i in range(len(width)):
            texti = gdspy.Text(str(width[i]) + 'u', textSize,
                    [offset[0] + i*spacing + sum(width[0:i]), offset[1] - textSize],
                    layer=1)
            capi = gdspy.Rectangle(
                    [offset[0] + i*spacing + sum(width[0:i]), offset[1] - textSize],
                    [offset[0] + i*spacing + sum(width[0:i+1]), offset[1] - textSize - width[i]], layer=1)

            tempCell.add(texti)
            tempCell.add(capi)

        return tempCell
    else:
        raise NotImplementedError
