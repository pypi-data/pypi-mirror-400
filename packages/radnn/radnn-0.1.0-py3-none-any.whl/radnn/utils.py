# ======================================================================================
#
#     Rapid Deep Neural Networks
#
#     Licensed under the MIT License
# ______________________________________________________________________________________
# ......................................................................................

# Copyright (c) 2024-2026 Pantelis I. Kaplanoglou

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
import json
import time
import hashlib
import zlib
import contextlib

phi=(1.0+np.sqrt(5.0))/2.0

# ======================================================================================================================
class classproperty(property):
  def __get__(self, obj, owner):
    return self.fget(owner)
# ======================================================================================================================


# ----------------------------------------------------------------------------------------------------------------------
def to_json(obj, is_sorted_keys=False, is_utf8=False):
  if isinstance(obj, dict):
    sJSON = json.dumps(obj, sort_keys=is_sorted_keys, indent=4, ensure_ascii=is_utf8)
  else:
    sJSON = json.dumps(obj, default=lambda o: obj.__dict__, sort_keys=is_sorted_keys, indent=4, ensure_ascii=is_utf8)
  return sJSON
# ----------------------------------------------------------------------------------------------------------------------
'''
  Checks if the p_sSettingsName is inside the settings dictionary p_dConfig
  and returns its value, otherwise the p_oDefault value
'''
def default_value(dictionary, key, default_value=None):
  if key in dictionary:
    return dictionary[key]
  else:
    return default_value
# ----------------------------------------------------------------------------------------------------------------------
def camel_case(text: str):
  return "".join([sWord.capitalize() for sWord in text.split()])
# ----------------------------------------------------------------------------------------------------------------------
def snake_case(text):
  return "_".join(text.lower().split())
# ----------------------------------------------------------------------------------------------------------------------
def interactive_matplotlib():
  import matplotlib
  matplotlib.use('TkAgg')
# ----------------------------------------------------------------------------------------------------------------------
def print_method_execution_time(func, *args, **kwargs):
  start = time.perf_counter()  # High-resolution timer
  result = func(*args, **kwargs)
  end = time.perf_counter()
  print(f"{func.__name__} took {end - start:.6f} seconds")
  return result
# ----------------------------------------------------------------------------------------------------------------------
def data_hash(data: np.ndarray):
  nBytes = data.tobytes()
  return hashlib.sha256(nBytes).hexdigest()
# ----------------------------------------------------------------------------------------------------------------------
def data_crc32(data: np.ndarray):
  nBytes = data.tobytes()
  return zlib.crc32(nBytes)
# --------------------------------------------------------------------------------------
def set_float_format(decimal_digits):
  np.set_printoptions(decimal_digits, suppress=True)
  np.set_printoptions(edgeitems=10)
  np.core.arrayprint._line_width = 180
# ----------------------------------------------------------------------------------------------------------------------
@contextlib.contextmanager
def print_options(*args, **kwargs):
  original = np.get_printoptions()
  np.set_printoptions(*args, **kwargs)
  try:
    yield
  finally:
    np.set_printoptions(**original)
# ----------------------------------------------------------------------------------------------------------------------
@contextlib.contextmanager
def print_options_float(precision=6):
  original = np.get_printoptions()
  np.set_printoptions(precision=precision, suppress=True)
  try:
    yield
  finally:
      np.set_printoptions(**original)
# ----------------------------------------------------------------------------------------------------------------------
def print_tensor(tensor: np.ndarray, title=None, format="%+.3f", axes_descr=["Sample"]):
  # ................................................
  def printElement(p_nElement, p_bIsScalar):
    if p_bIsScalar:
      print(format % p_nElement, end=" ")
    else:
      print(np.array2string(p_nElement, separator=",", formatter={'float': lambda x: format % x}), end=" ")

  # ................................................
  def strBoxLeft(p_nIndex, p_nCount):
    if (p_nIndex == 0):
      return "┌ "
    elif (p_nIndex == (p_nCount - 1)):
      return "└ "
    else:
      return "│ "

  # ................................................
  def strBoxRight(p_nIndex, p_nCount):
    if (p_nIndex == 0):
      return "┐ "
    elif (p_nIndex == (p_nCount - 1)):
      return "┘ "
    else:
      return "│ "

  # ................................................

  if len(tensor.shape) == 3:
    tensor = tensor[np.newaxis, ...]
  elif len(tensor.shape) == 2:
    tensor = tensor[np.newaxis, ..., np.newaxis]
  elif len(tensor.shape) == 5:
    tensor = tensor[..., np.newaxis]
  else:
    raise Exception("Supported tensors are rank 2 to rank 5")

  nSampleIndex = 0
  nCount, nGridRows, nGridCols = tensor.shape[0:3]
  nSliceCoordDigits = len(str(nGridRows))
  if len(str(nGridCols)) > nSliceCoordDigits:
    nSliceCoordDigits = len(str(nGridCols))

  bIsGridOfTensors = (len(tensor.shape) == 6)
  if bIsGridOfTensors:
    nWindowRows, nWindowCols = tensor.shape[3:5]

  bIsScalar = (tensor.shape[-1] == 1)

  nSpaces = nSliceCoordDigits * 2 + 5
  sSliceHeaders = ["X" + " " * (nSpaces - 3) + "= ",
                   " %" + str(nSliceCoordDigits) + "d" ",%" + str(nSliceCoordDigits) + "d   ",
                   " " * nSpaces]

  print("-" * 70)
  if title is None:
    print(f"shape:{tensor.shape}")
  else:
    print(f"{title} shape:{tensor.shape}")
  while nSampleIndex < nCount:
    print(f"  {axes_descr[0]}:#{nSampleIndex}")
    for nRow in range(0, nGridRows):
      if bIsGridOfTensors:
        for nY in range(nWindowRows):
          for nCol in range(0, nGridCols):
            if (nY == 0):
              print(sSliceHeaders[0] + strBoxLeft(nY, nWindowRows), end="")
            elif (nY == 1):
              sBaseStr = sSliceHeaders[1] % (nRow, nCol)
              print(sBaseStr + strBoxLeft(nY, nWindowRows), end="")
            else:
              print(sSliceHeaders[2] + strBoxLeft(nY, nWindowRows), end="")
            for nX in range(nWindowCols):
              printElement(tensor[nSampleIndex, nRow, nCol, nY, nX, ...], bIsScalar)

            print(strBoxRight(nY, nWindowRows), end="")
          print("")
        print("")
      else:
        print(strBoxLeft(nRow, nGridRows), end="")
        for nCol in range(0, nGridCols):
          printElement(tensor[nSampleIndex, nRow, nCol, ...], bIsScalar)
        print(strBoxRight(nRow, nGridRows))
    print("." * 60)
    nSampleIndex += 1
# ----------------------------------------------------------------------------------------------------------------------
