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
import json
import glob
from collections import OrderedDict

from .fileobject import FileObject

#TODO: jsonpickle
#https://stackoverflow.com/questions/3768895/how-to-make-a-class-json-serializable

class JSONFile(FileObject):
  # ----------------------------------------------------------------------------------
  def __init__(self, filename, parent_folder=None, error_template=None):
    super(JSONFile, self).__init__(filename, parent_folder, error_template, "json")
  # ----------------------------------------------------------------------------------
  def load(self, filename=None, encoding=None):
    filename = self._useFileName(filename)

    dResult = None
    if os.path.exists(filename):

      sJSON = None
      if os.path.isfile(filename):
        oEncodingToTry = ["utf-8", "utf-16", "latin1", "ascii"]  # Add more if needed
        if encoding is None:
          bIsLoaded = False
          for sEnc in oEncodingToTry:
            try:
              with open(filename, "r", encoding=sEnc) as oFile:
                sJSON = oFile.read()
              bIsLoaded = True
              break
            except (UnicodeDecodeError, UnicodeError):
              continue
          if not bIsLoaded:
            raise ValueError("Unsupported encoding")
        else:
          with open(filename, "r", encoding=encoding) as oFile:
            sJSON = oFile.read()
      if sJSON is not None:
        dResult = json.loads(sJSON, object_pairs_hook=OrderedDict)
    else:
      if self.error_template is not None:
        raise Exception(self.error_template % filename)

    return dResult
  # ----------------------------------------------------------------------------------
  def save(self, obj, filename=None, is_sorted_keys=False, is_utf8=False):
    filename = self._useFileName(filename)

    if obj is not None:
      if isinstance(obj, dict):
        sJSON = json.dumps(obj, sort_keys=is_sorted_keys, indent=4, ensure_ascii=is_utf8)
      else:
        sJSON = json.dumps(obj, default=lambda o: obj.__dict__, sort_keys=is_sorted_keys, indent=4, ensure_ascii=is_utf8)

      sEncoding = "utf-8"
      if not is_utf8:
        sEncoding = "utf-16"

      with open(filename, "w", encoding=sEncoding) as oFile:
        oFile.write(sJSON)
        oFile.close()
  # ----------------------------------------------------------------------------------
  @property
  def files(self, is_full_path=True):
    oResult = []
    if (self.parent_folder is not None):
      oJSONFiles = glob.glob(os.path.join(self.parent_folder, '*.json'))
      oJSONFiles = sorted(oJSONFiles, key=os.path.getmtime)

      for sJSONFile in oJSONFiles:
        if is_full_path:
          oResult.append(os.path.join(self.parent_folder, sJSONFile))
        else:
          oResult.append(sJSONFile)
    return oJSONFiles
  # ----------------------------------------------------------------------------------