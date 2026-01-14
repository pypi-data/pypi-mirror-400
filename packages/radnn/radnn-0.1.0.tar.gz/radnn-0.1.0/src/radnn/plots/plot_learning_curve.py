# ======================================================================================
#
#     Rapid Deep Neural Networks
#
#     Licensed under the MIT License
# ______________________________________________________________________________________
# ......................................................................................

# Copyright (c) 2020-2025 Pantelis I. Kaplanoglou

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
import matplotlib.pyplot as plt

class PlotLearningCurve(object):
  # --------------------------------------------------------------------------------------
  def __init__(self, metrics_dict, model_name):
    self.metrics_dict = metrics_dict
    self.model_name = model_name
    print("Keys in training process log:", self.metrics_dict.keys())
  # --------------------------------------------------------------------------------------
  def prepare(self, metric_key="accuracy", custom_title=None, metric_low=0, metric_high=1.0, is_legend_right=False, is_keras=False):
    sTrainMetricKey = metric_key
    if not is_keras:
      sTrainMetricKey = "train_" + metric_key
    sValMetricKey = "val_" + metric_key
    oLegend = ["training"]
    bHasValidation = sValMetricKey in self.metrics_dict
    oLegend.append("validation")
    
    
    plt.clf()
    plt.plot(self.metrics_dict[sTrainMetricKey])
    if bHasValidation:
      plt.plot(self.metrics_dict[sValMetricKey])
      
    if custom_title is None:
      plt.title(self.model_name + ' ' + metric_key)
    else:
      plt.title(self.model_name + ' ' + custom_title)
      
    plt.ylabel(metric_key.capitalize().title())
    plt.xlabel("Epoch")
    plt.ylim([metric_low, metric_high])
    if is_legend_right:
      plt.legend(oLegend, loc="upper right")
    else:
      plt.legend(oLegend, loc="upper left")
    return self
  # --------------------------------------------------------------------------------------
  def prepare_cost(self, cost_function=None):
    if isinstance(cost_function, str):
      sCostFunctionName = cost_function
    else:
      sClassName = str(cost_function.__class__)
      if ("keras" in sClassName) and ("losses" in sClassName):
        sCostFunctionNameParts = cost_function.name.split("_")
        sCostFunctionNameParts = [x.capitalize() + " " for x in sCostFunctionNameParts]
        sCostFunctionName = " ".join(sCostFunctionNameParts)

    return self.prepare("loss", sCostFunctionName, True)
  # --------------------------------------------------------------------------------------
  def save(self, filename):
    plt.savefig(filename, bbox_inches='tight')
    return self
  # --------------------------------------------------------------------------------------
  def show(self):
    plt.show()
  # --------------------------------------------------------------------------------------


