"""
Utility
--------
Read a document and create a PDF showing the original page layout.
Useful mainly for PDFs where /CropBox is not equal to /Mediabox and / or
when image and text locations should be shown.

The output is a PDF with pages having input /MediaBox dimensions.
All text in the output is repositioned with respect to the /CropBox location
in the input. Text is shown surrounded by its text block rectangle. Images are
not displayed, but their locations are indicated by empty rectangles with
some meta information.
"""
import sys
import time
import fitz

print(fitz.__doc__)
t0 = time.time()
doc1 = fitz.open(sys.argv[1])
doc2 = fitz.open()
red = (1, 0, 0)
blue = (0, 0, 1)
green = (0, 1, 0)
gray = (0.9, 0.9, 0.9)

for page1 in doc1:
    blks = page1.getTextBlocks(images=True)  # read text blocks of input page
    # create new page in output with /MediaBox dimensions
    page2 = doc2.newPage(-1, width=page1.MediaBoxSize[0], height=page1.MediaBoxSize[1])
    # the text font we use
    page2.insertFont(fontfile=None, fontname="Helvetica")
    img = page2.newShape()  # prepare /Contents object

    # calculate /CropBox & displacement
    disp = fitz.Rect(page1.CropBoxPosition, page1.CropBoxPosition)
    croprect = page1.rect + disp

    # draw original /CropBox rectangle
    img.drawRect(croprect)
    img.finish(color=gray, fill=gray)

    for b in blks:  # loop through the blocks
        r = fitz.Rect(b[:4])  # block rectangle
        # add dislacement of original /CropBox
        r += disp
        img.drawRect(r)  # surround block rectangle

        if b[-1] == 1:  # if image block ...
            color = red
            a = fitz.TEXT_ALIGN_CENTER
        else:  # if text block
            color = blue
            a = fitz.TEXT_ALIGN_LEFT

        img.finish(width=0.3, color=color)

        if r.isEmpty:  # do not rely on meaningful rects
            print(
                "skipping text of empty rect at (%g, %g) on page %i"
                % (r.x0, r.y0, page1.number)
            )
        else:
            # insert text of the block using a small, indicative fontsize
            img.insertTextbox(
                r, b[4], fontname="/Helvetica", fontsize=8, color=color, align=a
            )

    img.commit()  # store /Contents of out page

# save output file
doc2.save("layout-" + doc1.name, garbage=4, deflate=True, clean=True)
t1 = time.time()
print("total time: %g sec" % (t1 - t0))
