# ======================================================================================
#
#     Rapid Deep Neural Networks
#
#     Licensed under the MIT License
# ______________________________________________________________________________________
# ......................................................................................

# Copyright (c) 2019-2025 Pantelis I. Kaplanoglou

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

# ......................................................................................
import numpy as np
from sklearn import metrics


# ==============================================================================================================================
class EvaluateClassification(object):
  # --------------------------------------------------------------------------------------------------------------
  def __init__(self, actual_classes, predicted_classes, probabilities=None):
    self.actual_classes = actual_classes
    self.predicted_classes = predicted_classes
    self.confusion_matrix = np.asarray(metrics.confusion_matrix(self.actual_classes, self.predicted_classes))

    self.accuracy = metrics.accuracy_score(self.actual_classes, self.predicted_classes)
    self.precision, self.recall, self.f1score, self.support = metrics.precision_recall_fscore_support(
      self.actual_classes, self.predicted_classes, average=None)
    self.average_precision, self.average_recall, self.average_f1score, self.average_support = metrics.precision_recall_fscore_support(
      self.actual_classes, self.predicted_classes, average='weighted')

    if probabilities is not None:
      self.auc = metrics.roc_auc_score(actual_classes, probabilities)
    else:
      self.auc = None


    self.true_neg = self.confusion_matrix[0][0]
    self.false_pos = self.confusion_matrix[0][1]
    self.false_neg = self.confusion_matrix[1][0]
    self.true_pos = self.confusion_matrix[1][1]

    self.class_count = None
  # --------------------------------------------------------------------------------------------------------------
  def print_confusion_matrix(self):
    nSize = len(self.confusion_matrix[0])
    print("                    Predicted  ")
    print("               --" + "-" * 5 * nSize)
    sLabel = "Actual"
    for nIndex, nRow in enumerate(self.confusion_matrix):
      print("        %s | %s |" % (sLabel, " ".join(["%4d" % x for x in nRow])))
      if nIndex == 0:
        sLabel = " " * len(sLabel)
    print("               --" + "-" * 5 * nSize)
    print()
  # --------------------------------------------------------------------------------------------------------------
  def format_series_as_pc(self, metric_series):
    oValStr = []
    for x in metric_series:
      sX = f"{x*100.0:.2f}"
      oValStr.append(sX)

    oValues = [f"{x:^7}" for x in oValStr]
    return " |".join(oValues)
  # --------------------------------------------------------------------------------------------------------------
  def print_per_class(self, class_names=None):
    if class_names is not None:
      nClassCount = len(class_names.keys())
      oClasses = [f"{class_names[x]:7}" for x in list(range(nClassCount))]
    else:
      oClasses = sorted(np.unique(self.actual_classes))
      nClassCount = len(oClasses)
      oClasses = [f"{x:^7}" for x in oClasses]
    self.class_count = nClassCount

    sClasses = " |".join(oClasses)
    nRepeat = 28 + (7+2)*self.class_count
    print(f"                            |{sClasses}|")
    print("-"*nRepeat)
    print(f"Per Class Recall %          |{self.format_series_as_pc(self.recall[:])}|")
    print(f"Per Class Precision %       |{self.format_series_as_pc(self.precision[:])}|")
    print("-" * nRepeat)
  # --------------------------------------------------------------------------------------------------------------
  def print_overall(self):
    print(f"Accuracy %                  :{self.accuracy*100.0       :.3f}")
    print(f"Average F1 Score %          :{self.average_f1score*100.0:.3f}")
    print(f"Weighted Average Recall %   :{self.average_recall*100.0:.3f}")
    print(f"Weighted Average Precision %:{self.average_precision*100.0:.3f}")
    if (self.class_count == 2) and (self.auc is not None):
      print(f"Area Under the Curve (AUC):{self.auc:.4f}")
    print()
  # --------------------------------------------------------------------------------------------------------------


# ==============================================================================================================================


# alias for compatibility
class CEvaluator(EvaluateClassification):
  pass

