# ......................................................................................
# MIT License

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
from abc import ABC, abstractmethod


# ======================================================================================================================
class SamplePreprocessor(ABC):
  # --------------------------------------------------------------------------------------------------------------------
  def __init__(self, settings):
    self.settings = settings
    self.ts_transform_augment, self.vs_transform_augment, self.us_transform_augment = self.prepare_pipelines()
  # --------------------------------------------------------------------------------------------------------------------
  def __call__(self, samples, **kwargs):
    if self.us_transform_augment is None:
      return samples
    else:
      return self.input_for_inference(input)
  # --------------------------------------------------------------------------------------------------------------------
  @abstractmethod
  def input_for_inference(self, samples):
    pass
  # --------------------------------------------------------------------------------------------------------------------
  @abstractmethod
  def prepare_pipelines(self):
    pass
  # --------------------------------------------------------------------------------------------------------------------

# ======================================================================================================================
class VoidPreprocessor(SamplePreprocessor):
  # --------------------------------------------------------------------------------------------------------------------
  def input_for_inference(self, samples):
    return samples
  # --------------------------------------------------------------------------------------------------------------------
  def prepare_pipelines(self):
    return None, None, None
  # --------------------------------------------------------------------------------------------------------------------
