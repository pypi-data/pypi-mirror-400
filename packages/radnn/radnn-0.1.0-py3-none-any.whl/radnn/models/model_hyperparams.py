# ======================================================================================
#
#     Rapid Deep Neural Networks
#
#     Licensed under the MIT License
# ______________________________________________________________________________________
# ......................................................................................

# Copyright (c) 2018-2026 Pantelis I. Kaplanoglou

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
from . import CNNSizeFactor


class ModelHyperparams(object):
  # --------------------------------------------------------------------------------------------------------------------
  def __init__(self, hprm: dict | None = None):
    self.hprm = hprm
    self.model_name = None
    self.base_name = ""
    self.architecture = ""
    self.variant = ""
    self.class_count = 0
    self.input_dims = []
    self.dropout_prob = None
    # self.kind = "" //TODO: Validate expected input according to model kind
  
  # --------------------------------------------------------------------------------------------------------------------
  @property
  def input_channels(self):
    '''
    :return: The channels from the dimensions of an image input sample
    '''
    return self.input_dims[-1]
  
  # --------------------------------------------------------------------------------------------------------------------
  @property
  def input_resolution(self):
    '''
    :return: The resolution from the dimensions of an image input sample
    '''
    return self.input_dims[:2]
  
  # --------------------------------------------------------------------------------------------------------------------
  @property
  def cnn_size_factor(self):
    '''
      Calculates the cnn size factor using the maximum dimension as log normalized where 0 is the size for MNIST input
      and 1 the size for ImageNet input.
    :return: 1  tiny images (MNIST, FMNIST, CIFAR10, CIFAR100)
             2  small images (ImageNet 64x64)
             3
             4
    '''
    
    def get_id(x):
      if 0.0 <= x < 0.1:
        return 1
      elif 0.1 <= x < 0.4:
        return 2
      elif 0.4 <= x < 0.8:
        return 3
      elif 0.8 <= x <= 1.0:
        return 4
      else:
        return None
    
    nHeight, nWidth = self.input_dims[:2]
    nDim = nHeight
    if nHeight < nWidth:
      Dim = nWidth
    nLogDim = np.log10(nDim)
    nMin = np.log10(28)
    nMax = np.log10(300)
    nLogNormalized = (nLogDim - nMin) / (nMax - nMin)
    nSizeFactor = CNNSizeFactor(get_id(nLogNormalized))
    return nSizeFactor
  
  # --------------------------------------------------------------------------------------------------------------------
  @classmethod
  def from_dict(cls, hyperparams):
    '''
    Deserializes a hyperparameters object from a dictionary
    
    :param hyperparams: A dictionary containing the architectural hyperparameters for the model
    :return: a new model hyperparams object
    '''
    oModelHyperparams = ModelHyperparams(hyperparams)
    oModelHyperparams.model_name = hyperparams.get("Model.Name", "?")
    
    oModelHyperparams.base_name = oModelHyperparams.model_name
    sParts = oModelHyperparams.base_name.split(".")
    oModelHyperparams.architecture = "base"
    if len(sParts) >= 2:
      oModelHyperparams.base_name = sParts[0]
      oModelHyperparams.architecture = sParts[1].lower()
    
    oModelHyperparams.variant = hyperparams.get("Model.Variant", "")
    oModelHyperparams.name = hyperparams.get("Model.Name", "?")
    oModelHyperparams.input_dims = hyperparams.get("Dataset.SampleDims", [])
    oModelHyperparams.class_count = hyperparams.get("Dataset.ClassCount", 0)
    nDropOutKeepProb = hyperparams.get("Training.Regularize.DropOut.KeepProb", None)
    if nDropOutKeepProb is None:
      oModelHyperparams.dropout_prob = hyperparams.get("Training.Regularize.DropOut.DropProb", 0.0)
    else:
      oModelHyperparams.dropout_prob = 1.0 - nDropOutKeepProb
    
    return oModelHyperparams
  # --------------------------------------------------------------------------------------------------------------------
