# ======================================================================================
#
#     Rapid Deep Neural Networks
#
#     Licensed under the MIT License
# ______________________________________________________________________________________
# ......................................................................................

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
import os
import shutil
import sys
import re

from radnn.experiment import MLExperimentConfig
from radnn.experiment import get_experiment_code_ex, experiment_number_and_variation, experiment_code_and_timestamp
from radnn.core import now_iso
from radnn.system import FileSystem, FileStore
from radnn.system.tee_logger import TeeLogger








class MLExperimentEnv(dict):

  # --------------------------------------------------------------------------------------------------------------------
  @classmethod
  def experiment_filename_split(cls, filename):
    sTryFileName, sTryExt = os.path.splitext(filename)
    bIsVariationAndFold = "-" in sTryExt
    if bIsVariationAndFold:
      #LREXPLAINET22_MNIST_64.1-01
      sMainParts = filename.split("-")
      assert len(sMainParts) == 2, "Wrong experiment filename"
      sFoldNumber, _ = os.path.splitext(sMainParts[1])
      sParts = sMainParts[0].split("_")
      sModelName = f"{sParts[0]}_{sParts[1]}"
      sModelVar = sParts[2]
    else:
      sFileNameOnly, _ = os.path.splitext(filename)
      sMainParts = sFileNameOnly.split("-")
      if len(sMainParts) > 1:
        sFoldNumber = sMainParts[1]
      else:
        sFoldNumber = None
      sParts = sMainParts[0].split("_")
      sModelName = f"{sParts[0]}_{sParts[1]}"
      sModelVar = sParts[2]

    return sModelName, sModelVar, sFoldNumber
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  @classmethod
  def preload_config(cls, config_folder, experiment_group=None, experiment_base_name=None, experiment_variation=None, experiment_fold_number=None, experiment_filename=None):
    oPrintOutput = []
    oPrintOutput.append(f"[?] Experiment started at {now_iso()}")
    oPrintOutput.append(f" |__ {'model':<24}: {experiment_base_name}")

    dExperimentSpec = {"base_name": experiment_base_name, "variation": experiment_variation, "fold_number": experiment_fold_number}
    if experiment_filename is not None:
      # LREXPLAINET18_MNIST_08.1-01.json
      _, sFileNameFull = os.path.split(experiment_filename)
      experiment_base_name, experiment_variation, experiment_fold_number = cls.experiment_filename_split(sFileNameFull)
      experiment_fold_number = int(experiment_fold_number)
      dExperimentSpec = {"base_name": experiment_base_name, "variation": experiment_variation, "fold_number": experiment_fold_number}

    if experiment_group is not None:
      config_folder = os.path.join(config_folder, experiment_group)
    oConfigFS = FileStore(config_folder, must_exist=True)

    if "." in experiment_variation:
      sParts = experiment_variation.split(".")
      experiment_variation = f"{int(sParts[0]):02d}.{sParts[1]}"
    else:
      experiment_variation = f"{int(experiment_variation):02d}"
    sMessage = f" |__ {'variation':<24}: {experiment_variation}"

    if experiment_fold_number is not None:
      experiment_variation = f"{experiment_variation}-{experiment_fold_number:02d}"
      sMessage += f" fold: {experiment_fold_number}"
    oPrintOutput.append(sMessage)

    if experiment_filename is not None:
      sExperimentFileName = experiment_filename
    else:
      sExperimentFileName = oConfigFS.file(f"{experiment_base_name}_{experiment_variation}.json")
    oConfig = MLExperimentConfig(filename=sExperimentFileName, variation=experiment_variation)
    oPrintOutput.append(f" |__ {'configuration file':<24}: {sExperimentFileName}")

    return oConfig, oPrintOutput, dExperimentSpec
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

  # --------------------------------------------------------------------------------------------------------------------
  def __init__(self, config_fs, model_fs=None, base_name=None, number=None, variation=None, fold_number=None,
               experiment_filename=None, experiment_code=None, experiment_config=None, model_filestore=None):

    super(MLExperimentEnv, self).__init__()
    if isinstance(config_fs, FileSystem):
      oConfigFS = config_fs.configs
      oModelFS  = config_fs.models
    else:
      oConfigFS = config_fs
      oModelFS = model_fs
      if oModelFS is None:
        oModelFS = config_fs

    # ...................... | Fields | ......................
    self.config_fs = oConfigFS
    self.model_fs  = oModelFS
    self.base_name = base_name
    self.number = number
    self.variation  = variation
    self.fold_number = fold_number

    if (experiment_filename is not None) or (experiment_code is not None):
      self.base_name, self.number, self.variation, self.fold_number, _ = self.determine_code_parts(experiment_filename,
                                                                      experiment_code, number, variation, fold_number)

    self.experiment_filename = experiment_filename
    if self.experiment_filename is None:
      sExperimentCode = get_experiment_code_ex(self.base_name, self.number, self.variation, self.fold_number)
      if experiment_code is not None:
        assert sExperimentCode == experiment_code, "Re-created experiment code mismatch."
      self.experiment_filename = self.config_fs.file(f"{sExperimentCode}.json")


    self.is_debugable = False
    self.is_retraining = False

    self._config = experiment_config
    if self._config is None:
      self._config = MLExperimentConfig(self.experiment_filename, number=self.number)
    self.experiment_fs = self.model_fs.subfs(self.experiment_code)
    # ........................................................

  # --------------------------------------------------------------------------------------------------------------------
  def save_config(self):
    self._config.save(self.experiment_filename)
  # --------------------------------------------------------------------------------------------------------------------
  def determine_code_parts(self, experiment_filename, experiment_code, number, variation, fold_number):
    sExperimentCode = None
    if experiment_code is not None:
      sExperimentCode = experiment_code
    elif experiment_filename is not None:
      _, sFileNameFull = os.path.split(experiment_filename)
      sExperimentCode, _ = os.path.splitext(sFileNameFull)

    sISODate = None
    if sExperimentCode is not None:
      oMatch = re.match(r"^\d{4}-\d{2}-\d{2}_\d{6}_", sExperimentCode)
      if oMatch is not None:
        sISODate = oMatch.group()[:-1]
        sExperimentCode = sExperimentCode[18:]

      base_name, variation, sFoldNumber = MLExperimentEnv.experiment_filename_split(sExperimentCode)
      if sFoldNumber is not None:
        fold_number = int(sFoldNumber)

    if number is None:
      number, variation = experiment_number_and_variation(variation)

    return base_name, number, variation, fold_number, sISODate
  # --------------------------------------------------------------------------------------------------------------------
  @property
  def config(self):
    return self._config
  # --------------------------------------------------------------------------------------------------------------------
  @property
  def experiment_code(self):
    return get_experiment_code_ex(self.base_name, self.number, self.variation, self.fold_number)
  # --------------------------------------------------------------------------------------------------------------------
  def copy_config(self, start_timestamp):
    sOriginalFileName = self.experiment_filename
    sNewFileName = self.experiment_fs.file(f"{start_timestamp}_{self.experiment_code}.json")
    shutil.copy(sOriginalFileName, sNewFileName)
  # --------------------------------------------------------------------------------------------------------------------
  def move_log(self, start_timestamp, original_filename):
    self.copy_config(start_timestamp)
    _, original_filename_only = os.path.split(original_filename)
    sNewFileName = f"{start_timestamp}_{self.experiment_code}.{original_filename_only}"
    shutil.move(original_filename, self.experiment_fs.file(sNewFileName))
    sys.stdout = TeeLogger(self.experiment_fs.file(sNewFileName))
  # --------------------------------------------------------------------------------------------------------------------
  '''
  def AssignSystemParams(self, p_oParamsDict):
    self.number = p_oParamsDict["ModelNumber"]
    self.is_debugable = p_oParamsDict["IsDebuggable"]
    self.is_retraining = p_oParamsDict["IsRetraining"]

    self._config = MLExperimentConfig(self.model_fs.file(self.experiment_code + ".json"), number=self.number)
  '''
  # --------------------------------------------------------------------------------------------------------------------
  def __str__(self)->str:
    sResult  = f"Experiment Code: {self.experiment_code} | Debugable: {self.is_debugable} | Retraining: {self.is_retraining}\n"
    sResult += f" |___ base name: {self.base_name} , number:{self.number} , variation:{self.variation}, fold_number: {self.fold_number}\n"
    sResult += f" |___ file name: {self.experiment_filename}\n"
    sResult += f"Models FileStore    : {self.model_fs}\n"
    sResult += f"Configs FileStore   : {self.config_fs}\n"
    sResult += f"Experiment FileStore: {self.experiment_fs}\n"
    sResult += f"Experiment Filename : {self.experiment_filename}\n"
    sResult += f"Configuration\n"
    sResult += "-"*40 + "\n"
    sResult += str(self._config) + "\n"
    return sResult
  # --------------------------------------------------------------------------------------------------------------------
  def __repr__(self)->str:
    return self.__str__()
  # --------------------------------------------------------------------------------------------------------------------


