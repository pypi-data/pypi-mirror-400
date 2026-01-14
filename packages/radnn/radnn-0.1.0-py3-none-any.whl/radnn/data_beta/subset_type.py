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
class SubsetType(object):
  def __init__(self, name):
    self.name = name.lower()
    self.type = -1 # Unknown
    if self.is_training_set:
      self.type = 0
    elif self.is_validation_set:
      self.type = 1
    elif self.is_unknown_test_set:
      self.type = 2
  @property
  def is_training_set(self):
    return (self.name == "training") or (self.name == "train") or (self.name == "ts")

  @property
  def is_validation_set(self):
    return (self.name == "validation") or (self.name == "val") or (self.name == "vs")

  @property
  def is_unknown_test_set(self):
    return (self.name == "testing") or (self.name == "test") or (self.name == "ut")