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

class PlotConfusionMatrix(object):
  # --------------------------------------------------------------------------------------
  def __init__(self, confusion_matrix, title="Confusion Matrix"):
    self.confusion_matrix = confusion_matrix
    self.title = title
  # --------------------------------------------------------------------------------------
  def prepare(self):
    fig, ax = plt.subplots(figsize=(7.5, 7.5))
    ax.matshow(self.confusion_matrix, cmap=plt.cm.Blues, alpha=0.3)
    for i in range(self.confusion_matrix.shape[0]):
      for j in range(self.confusion_matrix.shape[1]):
        ax.text(x=j, y=i, s=self.confusion_matrix[i, j], va='center', ha='center', size='xx-large')

    plt.xlabel('Predicted Label', fontsize=18)
    plt.ylabel('Actual Label', fontsize=18)
    plt.title(self.title, fontsize=18)
    return self
  # --------------------------------------------------------------------------------------
  def save(self, filename):
    plt.savefig(filename, bbox_inches='tight')
    return self
  # --------------------------------------------------------------------------------------
  def show(self):
    plt.show()
  # --------------------------------------------------------------------------------------

