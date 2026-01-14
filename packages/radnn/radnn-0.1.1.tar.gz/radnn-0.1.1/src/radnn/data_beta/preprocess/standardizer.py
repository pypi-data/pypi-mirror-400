# ......................................................................................
# MIT License

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

# ......................................................................................
import numpy as np

'''
    Standardization for rank 3 and above tensors using numpy
'''
class Standardizer(object):
  # --------------------------------------------------------------------------------------------------------------------
  def __init__(self, name=None, filestore=None):
    # ................................................................
    # // Fields \\
    self.mean = None
    self.std = None
    self.name = name
    self.filestore = filestore
    # ................................................................
    self.load()
  # --------------------------------------------------------------------------------------------------------------------
  def load(self):
    if (self.name is not None) and (self.filestore is not None):
      dStats = self.filestore.obj.load("%s-meanstd.pkl" % self.name)
      if dStats is not None:
        self.mean = dStats["mean"]
        self.std = dStats["std"]
  # --------------------------------------------------------------------------------------------------------------------
  def save(self):
    if (self.name is not None) and (self.filestore is not None):
      dStats = {"mean": self.mean, "std": self.std}
      self.filestore.obj.save(dStats, "%s-meanstd.pkl" % self.name, is_overwriting=True)
  # --------------------------------------------------------------------------------------------------------------------
  def fit(self, data, axis_for_stats=None, is_recalculating=False, is_verbose=False):
    bIsCached = False
    if (self.name is not None) and (self.filestore is not None):
      if self.mean is not None:
        bIsCached = True

    if (not bIsCached) or is_recalculating:
      # Collect statistics with maximum precision
      data = data.astype(np.float64)
      nAxes = list(range(len(data.shape)))
      if axis_for_stats is None:
        nAxes = tuple(nAxes)
      else:
        if axis_for_stats == -1:
          axis_for_stats = nAxes[-1]

        nAxes.remove(axis_for_stats)
        if len(nAxes) == 1:
          nAxes = nAxes[0]
        else:
          nAxes = tuple(nAxes)

      self.mean = np.mean(data, axis=nAxes)
      self.std = np.std(data, axis=nAxes)
      if is_verbose:
        print("  Standardization: mean/std shape:%s" % str(self.mean.shape))
      self.save()

    return self
  # --------------------------------------------------------------------------------------------------------------------
  def fit_transform(self, data, axis_for_stats=-1, is_recalculating=False, is_verbose=False):
    self.fit(data, axis_for_stats, is_recalculating, is_verbose)
    return self.transform(data)
  # --------------------------------------------------------------------------------------------------------------------
  def standardize(self, data):
    return (data - self.mean) / self.std
  # --------------------------------------------------------------------------------------------------------------------
  def destandardize(self, data):
    return (data * self.std) + self.mean
  # --------------------------------------------------------------------------------------------------------------------
  def transform(self, data):
    nStandardizedData = (data - self.mean) / self.std
    return nStandardizedData.astype(data.dtype)
  # --------------------------------------------------------------------------------------------------------------------
  def inverse_transform(self, data):
    nNonStandardizedData = (data * self.std) + self.mean
    return nNonStandardizedData.astype(data.dtype)
  # --------------------------------------------------------------------------------------------------------------------
  def __str__(self):
    return f"Standardizer: mean={self.mean} std={self.std}"
  # --------------------------------------------------------------------------------------------------------------------
  def __repr__(self):
    return self.__str__()
  # --------------------------------------------------------------------------------------------------------------------