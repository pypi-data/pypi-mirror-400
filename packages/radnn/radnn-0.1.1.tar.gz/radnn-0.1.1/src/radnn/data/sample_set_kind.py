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
from enum import Enum


# ======================================================================================================================
class SampleSetKind(Enum):
  TRAINING_SET = 0
  VALIDATION_SET = 1
  UNKNOWN_TEST_SET = 2


# ======================================================================================================================
class SampleSetKindInfo(dict):
  # --------------------------------------------------------------------------------------------------------------------
  def __init__(self, kind_str: str|None=None, kind: int | None=None, **kwargs):
    super().__init__(**kwargs)
    self._kind: int | None = kind
    self._kind_str: str | None = None
    if kind_str is not None:
      self._kind_str = kind_str.lower()

    # Invoke the property getters
    self["kind"]      = self.kind
    self["kind_str"]  = self.kind_description
  # --------------------------------------------------------------------------------------------------------------------
  @property
  def kind_description(self):
    if (self._kind_str is None):
      nKind = self.get("type", -1)
      if nKind == SampleSetKind.TRAINING_SET.value:
        self._kind_str = "training"
      elif nKind == SampleSetKind.value:
        self._kind_str = "validation"
      elif nKind == SampleSetKind.value:
        self._kind_str = "training"
    return self._kind_str
  # --------------------------------------------------------------------------------------------------------------------
  @property
  def kind(self):
    if (self._kind is None):
      nKind = -1 # Unknown
      if self.is_training_set:
        nKind = SampleSetKind.TRAINING_SET.value
      elif self.is_validation_set:
        nKind = SampleSetKind.VALIDATION_SET.value
      elif self.is_unknown_test_set:
        nKind = SampleSetKind.UNKNOWN_TEST_SET.value
      self._kind = nKind
    return self._kind
  # --------------------------------------------------------------------------------------------------------------------
  @property
  def must_shuffle(self):
    return self.kind == SampleSetKind.TRAINING_SET.value
  # --------------------------------------------------------------------------------------------------------------------
  @property
  def is_training_set(self):
    return (self._kind_str == "training") or (self._kind_str == "train") or (self._kind_str == "ts")
  # --------------------------------------------------------------------------------------------------------------------
  @property
  def is_validation_set(self):
    return (self._kind_str == "validation") or (self._kind_str == "val") or (self._kind_str == "vs")
  # --------------------------------------------------------------------------------------------------------------------
  @property
  def is_unknown_test_set(self):
    return (self._kind_str == "testing") or (self._kind_str == "test") or (self._kind_str == "ut")
  # --------------------------------------------------------------------------------------------------------------------
  @property
  def is_classification(self):
    return self["Task"] == "classification"
  # --------------------------------------------------------------------------------------------------------------------
  @is_classification.setter
  def is_classification(self, value):
    if value:
      self["Task"] = "classification"
      self["Classes.Count"] = None
      self["Classes.Indices"] = None
      self["Classes.Weights"] = None
  # --------------------------------------------------------------------------------------------------------------------
  @property
  def class_count(self):
    return self["Classes.Count"]
  # --------------------------------------------------------------------------------------------------------------------
  @class_count.setter
  def class_count(self, value):
    self["Classes.Count"] = value
  # --------------------------------------------------------------------------------------------------------------------
  @property
  def class_indices(self):
    return self["Classes.Indices"]
  # --------------------------------------------------------------------------------------------------------------------
  @class_indices.setter
  def class_indices(self, value):
    self["Classes.Indices"] = value
  # --------------------------------------------------------------------------------------------------------------------
  @property
  def class_weights(self):
    return self["Classes.Weights"]
  # --------------------------------------------------------------------------------------------------------------------
  @class_weights.setter
  def class_weights(self, value):
    self["Classes.Weights"] = value
  # --------------------------------------------------------------------------------------------------------------------
