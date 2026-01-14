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
from matplotlib import cm

class MultiScatterPlot(object):
  # --------------------------------------------------------------------------------------
  # Constructor
  def __init__(self, title, data=None, class_count=10, class_names=None):
    # ................................................................
    # // Fields \\
    self.Title = title
    self.Data = data

    self.ClassCount = class_count
    if class_names is not None:
      self.ClassNames = class_names
      self.ClassCount = len(self.ClassNames)

    if (self.ClassCount <= 10):
      self.ColorMap = cm.get_cmap("tab10")
    elif (self.ClassCount <= 20):
      self.ColorMap = cm.get_cmap("tab20")
    else:
      self.ColorMap = cm.get_cmap("prism")
      # self.ColorMap = colors.ListedColormap(["darkorange","darkseagreen"])

    self.PlotDimensions = [14, 8]
    self.PointSize = 48

    self.PanesPerRow = 2
    if self.Data is not None:
      self.Panes = len(self.Data)

    self.__fig = None
    self.__ax = None
    # ................................................................

  # --------------------------------------------------------------------------------------
  def add_data(self, dataset_name, samples, labels=None):
    if self.Data is None:
      self.Data = []

    if labels is None:
      labels = np.zeros((samples.shape[0]), np.int32)
    self.Data.append([dataset_name, samples, labels])
    self.Panes = len(self.Data)

  # --------------------------------------------------------------------------------------
  def prepare(self, index, x_axis_caption, y_axis_caption):
    # The 2D data for the scatter plot
    sDataName, nSamples, nLabels = self.Data[index]
    nXValues = nSamples[:, 0]
    nYValues = nSamples[:, 1]
    nLabels = nLabels

    if self.__fig is None:
      if self.Panes == 1:
        self.__fig, self.__ax = plt.subplots(nrows=1, ncols=1, sharex=False, sharey=False, squeeze=False,
                                             figsize=self.PlotDimensions)
      else:
        nRows = self.Panes // self.PanesPerRow
        if (self.Panes % self.PanesPerRow != 0):
          nRows += 1
        self.__fig, self.__ax = plt.subplots(nrows=nRows, ncols=self.PanesPerRow, sharex=False, sharey=False,
                                             squeeze=False, figsize=self.PlotDimensions)

    nRow = index // self.PanesPerRow
    nCol = index - (nRow * self.PanesPerRow)
    oPlot = self.__ax[nCol, nRow]
    oPlot.set_xlabel(x_axis_caption)
    oPlot.set_ylabel(y_axis_caption)
    oPlot.set_title(sDataName)

    oScatter = oPlot.scatter(nXValues, nYValues, s=self.PointSize, c=nLabels, cmap=self.ColorMap)

    oLegend = oPlot.legend(*oScatter.legend_elements(), loc="lower right", title="Classes", framealpha=0.4,
                           labelspacing=0.1)
    oPlot.add_artist(oLegend)

    if index == self.Panes - 1:
      plt.title(self.Title)
      plt.tight_layout(pad=1.01)

    return self
  # --------------------------------------------------------------------------------------
  def save(self, filename):
    plt.savefig(filename, bbox_inches='tight')
    return self
  # --------------------------------------------------------------------------------------
  def show(self):
    plt.show()
  # --------------------------------------------------------------------------------------
