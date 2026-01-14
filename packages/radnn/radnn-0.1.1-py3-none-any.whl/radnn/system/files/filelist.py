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

import os


# ======================================================================================================================
class FileListFullPathIterator(object):
  # --------------------------------------------------------------------------------------------------------------------
  def __init__(self, filelist):
    self.filelist = filelist
    self.index = 0
  # --------------------------------------------------------------------------------------------------------------------
  def __iter__(self):
    return self
  # --------------------------------------------------------------------------------------------------------------------
  def __next__(self):
    if self.index >= len(self.filelist):
      raise StopIteration
    sFileFullPath = os.path.join(self.filelist.parent_folder_path, self.filelist[self.index])
    self.index += 1
    return sFileFullPath
  # --------------------------------------------------------------------------------------------------------------------
# ======================================================================================================================





# ======================================================================================================================
class FileList(list):
  # --------------------------------------------------------------------------------------------------------------------
  def __init__(self, parent_folder_path=None):
    self.parent_folder_path = parent_folder_path
  # --------------------------------------------------------------------------------------------------------------------
  @property
  def full_paths(self):
    if self.parent_folder_path is not None:
      return FileListFullPathIterator(self)
    else:
      return None
  # --------------------------------------------------------------------------------------------------------------------
# ======================================================================================================================