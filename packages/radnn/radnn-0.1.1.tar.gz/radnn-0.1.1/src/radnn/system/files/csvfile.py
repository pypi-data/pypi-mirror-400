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
import pandas as pd
import numpy as np

from .fileobject import FileObject

class CSVFile(FileObject):
  # ----------------------------------------------------------------------------------
  def __init__(self, filename, parent_folder=None, error_template=None):
    super(CSVFile, self).__init__(filename, parent_folder, error_template, "txt")
  # ----------------------------------------------------------------------------------
  def load(self, filename=None, delimiter=",", encoding="utf-8"):
    sFileName = self._useFileName(filename)
    dResult = pd.read_csv(sFileName, delimiter=delimiter, encoding=encoding)
    return dResult
  # ----------------------------------------------------------------------------------
  # TODO: Iterate large csv files row by row as done in TextFile
  #@property
  #def rows(self):
  # ----------------------------------------------------------------------------------
  def save(self, obj, filename=None, headers=None, delimiter=",", encoding="utf-8"):
    sFileName = self._useFileName(filename)

    if isinstance(obj, dict):
      nMaxRowCols = 0
      oList = []
      for k, v in obj.items():
        oRow = [k]
        if isinstance(v, list):
          oRow.extend(v)
        else:
          oRow.append(v)
        if len(oRow) > nMaxRowCols:
          nMaxRowCols = len(oRow)
        oList.append(oRow)

      obj = []
      for oRow in oList:
        oRowToAdd = oRow + [None]*(nMaxRowCols - len(oRow))
        obj.append(oRowToAdd)
      if len(headers) < nMaxRowCols:
        headers = headers + [None]*(nMaxRowCols - len(headers))

    if isinstance(obj, list):
      df = pd.DataFrame(obj, columns=headers)
      df.to_csv(sFileName, index=False, header=(headers is not None), sep=delimiter, encoding=encoding)

    elif isinstance(obj, np.ndarray):
      if len(headers) < obj.shape[1]:
        headers = headers + [None]*(obj.shape[1] - len(headers))
      df = pd.DataFrame(obj, columns=headers)
      df.to_csv(sFileName, index=False, header=(headers is not None), sep=delimiter, encoding=encoding)
  # ----------------------------------------------------------------------------------