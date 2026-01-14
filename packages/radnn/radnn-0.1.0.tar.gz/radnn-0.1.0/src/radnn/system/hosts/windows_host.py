# ======================================================================================
#
#     Rapid Deep Neural Networks
#
#     Licensed under the MIT License
# ______________________________________________________________________________________
# ......................................................................................

# Copyright (c) 2024-2025 Pantelis I. Kaplanoglou

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
import win32api
import ctypes
class WindowsHost(object):
  # --------------------------------------------------------------------------------------------------------------------
  @classmethod
  def dll_info_root(self, dll_filename):
    dInfo = dict()
    ver_strings = ('Comments', 'InternalName', 'ProductName',
                   'CompanyName', 'LegalCopyright', 'ProductVersion',
                   'FileDescription', 'LegalTrademarks', 'PrivateBuild',
                   'FileVersion', 'OriginalFilename', 'SpecialBuild')
    # fname = os.environ["comspec"]
    dFileVersionInfo = win32api.GetFileVersionInfo(dll_filename, '\\')
    ## backslash as parm returns dictionary of numeric info corresponding to VS_FIXEDFILEINFO struc

    for sKey, oValue in dFileVersionInfo.items():
      dInfo[sKey] = oValue
    return dInfo
  # --------------------------------------------------------------------------------------------------------------------
  @classmethod
  def dll_info(cls, dll_filename):
    dInfo = dict()

    dFileVersionsInfo = win32api.GetFileVersionInfo(dll_filename, '\\VarFileInfo\\Translation')
    ## \VarFileInfo\Translation returns list of available (language, codepage) pairs that can be used to retreive string info
    ## any other must be of the form \StringfileInfo\%04X%04X\parm_name, middle two are language/codepage pair returned from above
    dInfo = dict()
    for sLanguageCode, sCodePage in dFileVersionsInfo:
      dInfo["lang"] = sLanguageCode
      dInfo["codepage"] = sCodePage

      #print('lang: ', lang, 'codepage:', codepage)
      oVersionStrings = ('Comments', 'InternalName', 'ProductName',
                     'CompanyName', 'LegalCopyright', 'ProductVersion',
                     'FileDescription', 'LegalTrademarks', 'PrivateBuild',
                     'FileVersion', 'OriginalFilename', 'SpecialBuild')
      for sVersionString in oVersionStrings:
        str_info = u'\\StringFileInfo\\%04X%04X\\%s' % (sLanguageCode, sCodePage, sVersionString)
        dInfo[sVersionString] = repr(win32api.GetFileVersionInfo(dll_filename, str_info))
    return dInfo
  # --------------------------------------------------------------------------------------------------------------------
  @classmethod
  def set_windows_sleep_resolution(cls, msecs=1):
    """
    Requests a minimum resolution for periodic timers. This increases accuracy
    for the waiting interval of the time.sleep function
    """
    oWinMM = ctypes.WinDLL('oWinMM')
    oWinMM.timeBeginPeriod(msecs)
  # --------------------------------------------------------------------------------------------------------------------