# ======================================================================================
#
#     Rapid Deep Neural Networks
#
#     Licensed under the MIT License
# ______________________________________________________________________________________
# ......................................................................................

# Copyright (c) 2023-2025 Pantelis I. Kaplanoglou

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
from sklearn import metrics
import matplotlib.pyplot as plt

'''
    Receiver Operator Characteristics (ROC) Plot
'''
class PlotROC(object):
  # --------------------------------------------------------------------------------------
  def __init__(self, actual_labels, predicted_probs, title="Receiving Operator Characteristics Curve"):
    self.actual_labels = actual_labels
    self.predicted_probs = predicted_probs
    self.title = title
  # --------------------------------------------------------------------------------------
  def prepare(self, true_threshold=0.5, figure_size=[6.00, 6.00], is_showing_grid=True):
    plt.rcParams["figure.figsize"] = figure_size
    plt.rcParams["figure.autolayout"] = True

    nFPR, nTPR, nThresholds = metrics.roc_curve(self.actual_labels, self.predicted_probs)
    nAUC = metrics.roc_auc_score(self.actual_labels, self.predicted_probs)
    plt.xlim(0, 1.02)
    plt.ylim(0, 1.02)
    if is_showing_grid:
      plt.grid()
    plt.plot(nFPR, nTPR, label="ROC curve (AUC=%.2f)" % nAUC, linewidth=2)
    plt.plot([0.0, 1.0], [0.0, 1.0], 'r--', label="Random prediction")  # , color="yellow", linewidth=1)

    plt.ylabel("TPR (True Positive Rate)")
    plt.xlabel("FPR (False Positive Rate)")

    nPointIndex = None
    for nThresholdIndex, nThreshold in enumerate(nThresholds):
      if nThreshold < true_threshold:
        nPointIndex = nThresholdIndex
        break

    if nPointIndex is not None:
      plt.plot(nFPR[nPointIndex], nTPR[nPointIndex]
              , label="Threshold %.2f" % nThreshold
              , marker="o", markersize=10, markeredgecolor="blue", markerfacecolor="yellow")
      plt.title(self.title, fontsize=18)
      plt.legend(loc=4)
    return self
  # --------------------------------------------------------------------------------------
  def save(self, filename):
    plt.savefig(filename, bbox_inches='tight')
    return self
  # --------------------------------------------------------------------------------------
  def show(self):
    plt.show()
  # --------------------------------------------------------------------------------------
