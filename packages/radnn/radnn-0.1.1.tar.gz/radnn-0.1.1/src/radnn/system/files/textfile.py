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
import numpy as np
import locale
from .fileobject import FileObject


class TextFile(FileObject):
  # --------------------------------------------------------------------------------------------------------------------
  def __init__(self, filename, parent_folder=None, error_template=None, is_verbose=False):
    super(TextFile, self).__init__(filename, parent_folder, error_template)
    self.is_verbose = is_verbose
    self._opened_filename = None
    self._encoding = None
  # ----------------------------------------------------------------------------------
  def open(self, filename, encoding=None):
    self._opened_filename = filename
    self._encoding = encoding
    return self

  # ----------------------------------------------------------------------------------
  def close(self):
    self._opened_filename = None
    self._encoding = None
  # ----------------------------------------------------------------------------------
  @property
  def rows(self):
    sFileName = self._useFileName(self._opened_filename)

    if os.path.isfile(sFileName):
      if self._encoding is not None:
        oEncodingToTry = [self._encoding]
      else:
        oEncodingToTry = ["utf-8", "utf-16", "latin1", "ascii"]  # Add more if needed
      bIsLoaded = False
      for sEnc in oEncodingToTry:
        try:
          with open(sFileName, "r", encoding=sEnc) as oFile:
            yield oFile.read()
          bIsLoaded = True
          break
        except (UnicodeDecodeError, UnicodeError):
          continue
      if not bIsLoaded:
        raise ValueError("Unsupported encoding")
  # ----------------------------------------------------------------------------------
  def load(self, filename=None, encoding=None):
    filename = self._useFileName(filename)

    sText = None
    if os.path.isfile(filename):
      if self._encoding is not None:
        oEncodingToTry = [encoding]
      else:
        oEncodingToTry = ["utf-8", "utf-16", "latin1", "ascii"]  # Add more if needed

      bIsLoaded = False
      for sEnc in oEncodingToTry:
        try:
          with open(filename, "r", encoding=sEnc) as oFile:
            sText = oFile.read()
          bIsLoaded = True
          break
        except (UnicodeDecodeError, UnicodeError):
          continue
      if not bIsLoaded:
        raise ValueError("Unsupported encoding")

    return sText
  # --------------------------------------------------------------------------------------------------------------------
  def save(self, text_obj, filename=None, encoding="utf-8"):
    sFilename = self._useFileName(filename)

    """
    Writes text to a file

    Parameters
        p_sFileName        : Full path to the text file
        p_sText            : Text to write
    """
    if self.is_verbose:
      print("  {.} Saving text to %s" % sFilename)

    bIsIterable = False
    if isinstance(text_obj, list):
      bIsIterable = True
    if isinstance(text_obj, np.ndarray):
      bIsIterable = text_obj.dtype = str

    if bIsIterable:
      with open(sFilename, "w", encoding=encoding) as oFile:
        for sLine in text_obj:
          print(sLine, file=oFile)
        oFile.close()
    else:
      with open(sFilename, "w", encoding=encoding) as oFile:
        print(text_obj, file=oFile)
        oFile.close()
    return True
  # --------------------------------------------------------------------------------------------------------------------