# ======================================================================================
#
#     Rapid Deep Neural Networks
#
#     Licensed under the MIT License
# ______________________________________________________________________________________
# ......................................................................................

# Copyright (c) 2022-2025 Pantelis I. Kaplanoglou

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# .......................................................................................
import numpy as np
import matplotlib.pyplot as plt

class AutoMultiImagePlot(object):
  def __init__(self, min=None, max=None, title=None):
    self.rows = []
    self.row_count = 0
    self.row_titles = []
    self.current_row = -1
    self.row_col_count = dict()
    self.max_col_count = 0
    self.min = min
    self.max = max
    self.title = title

  def add_row(self, row_title=None):
    self.current_row = self.row_count
    self.rows.append([])
    self.row_count = len(self.rows)
    self.row_titles.append(row_title)

  def add_column(self, image, image_title=None, color_map=None, aspect=None, extent=None):
    oRowColumns = self.rows[self.current_row]
    dImage = {"image": image, "title": image_title
      , "cmap": color_map, "aspect": aspect
      , "extend": extent}

    oRowColumns.append(dImage)
    self.rows[self.current_row] = oRowColumns
    nColCount = len(oRowColumns)

    self.row_col_count[self.current_row] = nColCount
    if nColCount > self.max_col_count:
      self.max_col_count = nColCount

  def prepare(self, title=None, figure_size=(15, 6), restrict_columns=None):

    nColumns = restrict_columns
    if nColumns is None:
      nColumns = self.max_col_count
    fig, oSubplotGrid = plt.subplots(  nrows=self.row_count, ncols=nColumns
                                     , figsize=figure_size
                                     , subplot_kw={'xticks': [], 'yticks': []})
    bIsSingleRow = self.row_count == 1
    if bIsSingleRow:
      oSubplotGrid = oSubplotGrid[np.newaxis, ...]

    if title is None:
      title = self.title
    fig.suptitle(title)
    for nRowIndex, oRowColumns in enumerate(self.rows):
      if len(oRowColumns) > 0:
        sRowTitle = self.row_titles[nRowIndex]
        nRowImageCount = len(oRowColumns)
        #nIncr = nImageCount // nRowColumnCount
        nIncr = 1
        nImageIndex = 0
        for nColIndex in range(nColumns):
          bMustPlot = nColIndex < nRowImageCount
          #if (nIncr == 0) and (nColIndex > 0):
          #  bMustPlot = False

          if bMustPlot:
            dImage = oRowColumns[nImageIndex]
            oSubPlot = oSubplotGrid[nRowIndex, nColIndex]
            sTitle = dImage['title']
            if sTitle is not None:
              oSubPlot.title.set_text(sTitle)
            oSubPlot.set_xticks([])
            oSubPlot.set_yticks([])
            oSubPlot.imshow(dImage["image"], cmap=dImage["cmap"],
                            aspect=dImage["aspect"], extent=dImage["extend"],
                            vmin=self.min, vmax=self.max
                            )

            if nColIndex == 0:
              if sRowTitle is not None:
                oSubPlot.text(0.0, 0.5, sRowTitle, transform=oSubPlot.transAxes,
                              horizontalalignment='right', verticalalignment='center',
                              fontsize=9, fontweight='bold')
          nImageIndex += nIncr
    fig.subplots_adjust(wspace=0.1, hspace=0.6)
    return self

  # --------------------------------------------------------------------------------------
  def save(self, filename):
    plt.savefig(filename, bbox_inches='tight')
    return self

  # --------------------------------------------------------------------------------------
  def show(self):
    plt.show()
  # --------------------------------------------------------------------------------------
