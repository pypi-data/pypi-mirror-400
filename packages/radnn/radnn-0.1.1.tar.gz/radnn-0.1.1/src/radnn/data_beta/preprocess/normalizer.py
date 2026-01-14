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
    Normalization for rank 3 and above tensors using numpy
'''
class Normalizer(object):
  # --------------------------------------------------------------------------------------------------------------------
  def __init__(self, name=None, filestore=None):
    # ................................................................
    # // Fields \\
    self.min = None
    self.max = None
    self._small_e = 1e-7
    self.name = name
    self.filestore = filestore
    # ................................................................
    self.load()
  # --------------------------------------------------------------------------------------------------------------------
  @property
  def small_e(self):
    return self._small_e
  # --------------------------------------------------------------------------------------------------------------------
  def load(self):
    if (self.name is not None) and (self.filestore is not None):
      dStats = self.filestore.obj.load("%s-minmax.pkl" % self.name)
      if dStats is not None:
        self.min = dStats["min"]
        self.max = dStats["max"]

      if np.any((self.max - self.min) <= self._small_e):
        self.max += self._small_e
  # --------------------------------------------------------------------------------------------------------------------
  def save(self):
    if (self.name is not None) and (self.filestore is not None):
      dStats = {"min": self.min, "max": self.max}
      self.filestore.obj.save(dStats, "%s-minmax.pkl" % self.name, is_overwriting=True)
  # --------------------------------------------------------------------------------------------------------------------
  def fit(self, data, axis_for_stats=-1, is_recalculating=False, is_verbose=False):
    bIsCached = False
    if (self.name is not None) and (self.filestore is not None):
      if self.min is not None:
        bIsCached = True

    if (not bIsCached) or is_recalculating:
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

      # Calculate min max difference with maximum precision
      self.min = np.min(data, axis=nAxes)
      self.max = np.max(data, axis=nAxes)
      if np.any((self.max - self.min) <= self._small_e):
        self.max += self._small_e

      if is_verbose:
        print("  Normalization: min/max shape:%s" % str(self.min.shape))
      self.save()
    return self
  # --------------------------------------------------------------------------------------------------------------------
  def fit_transform(self, data, axis_for_stats=-1, is_recalculating=False, is_verbose=False):
    self.fit(data, axis_for_stats, is_recalculating, is_verbose)
    return self.transform(data)
  # --------------------------------------------------------------------------------------------------------------------
  def normalize(self, data):
    return (data - self.min) / (self.max - self.min)
  # --------------------------------------------------------------------------------------------------------------------
  def denormalize(self, data):
    return (data * (self.max - self.min)) + self.min
  # --------------------------------------------------------------------------------------------------------------------
  def transform(self, data):
    nNormalizedData = (data - self.min) / (self.max - self.min)
    return nNormalizedData.astype(data.dtype)
  # --------------------------------------------------------------------------------------------------------------------
  def inverse_transform(self, data):
    nDenormalizedData = (data * (self.max - self.min)) + self.min
    return nDenormalizedData.astype(data.dtype)
  # --------------------------------------------------------------------------------------------------------------------
  def __str__(self):
    return f"Normalizer: min={self.min} max={self.max}"
  # --------------------------------------------------------------------------------------------------------------------
  def __repr__(self):
    return self.__str__()
  # --------------------------------------------------------------------------------------------------------------------
