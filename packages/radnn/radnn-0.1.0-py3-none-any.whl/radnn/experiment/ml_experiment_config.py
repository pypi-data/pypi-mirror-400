# ======================================================================================
#
#     Rapid Deep Neural Networks
#
#     Licensed under the MIT License
# ______________________________________________________________________________________
# ......................................................................................

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
import os
import json
import re
from datetime import datetime
from radnn.ml_system import mlsys
from radnn.system import FileSystem, FileStore

# --------------------------------------------------------------------------------------
def model_code_mllib(p_oDict):
  if "Experiment.BaseName" in p_oDict:
    sBaseName = p_oDict["Experiment.BaseName"]
    nNumber = int(p_oDict["Experiment.Number"])
    sVariation = None
    if "Experiment.Variation" in p_oDict:
      sVariation = p_oDict["Experiment.Variation"]
    nFoldNumber = None
    if "Experiment.FoldNumber" in p_oDict:
      nFoldNumber = p_oDict["Experiment.FoldNumber"]

    sCode = "%s_%02d" % (sBaseName, nNumber)
    if sVariation is not None:
      sCode += ".%s" % str(sVariation)
    if nFoldNumber is not None:
      sCode += "-%02d" % int(nFoldNumber)

  elif "ModelName" in p_oDict:
    sCode = p_oDict["ModelName"]
    if "ModelVariation" in p_oDict:
      sCode += "_" + p_oDict["ModelVariation"]
    if "ExperimentNumber" in p_oDict:
      sCode = sCode + "_%02d" % p_oDict["ExperimentNumber"]

  return sCode
# --------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------
def legacy_model_code(config_dict):
  if "ModelName" in config_dict:
    sCode = config_dict["ModelName"]
    if "ModelVariation" in config_dict:
      sCode += "_" + config_dict["ModelVariation"]
    if "ExperimentNumber" in config_dict:
      sCode = sCode + "_%02d" % config_dict["ExperimentNumber"]
  else:
    raise Exception("Invalid experiment configuration. Needs at least the key 'ModelName'.")
  return sCode
# --------------------------------------------------------------------------------------
def get_experiment_code(config_dict):
  if ("Experiment.BaseName" in config_dict) and ("Experiment.Number" in config_dict):
    sBaseName = config_dict["Experiment.BaseName"]
    nNumber = int(config_dict["Experiment.Number"])
    sVariation = None
    if "Experiment.Variation" in config_dict:
      sVariation = str(config_dict["Experiment.Variation"])
    nFoldNumber = None
    if "Experiment.FoldNumber" in config_dict:
      nFoldNumber = int(config_dict["Experiment.FoldNumber"])

    sCode = f"{sBaseName}_{nNumber:02d}"
    if sVariation is not None:
      sCode += "." + sVariation
    if nFoldNumber is not None:
      sCode += f"-{nFoldNumber:02d}"
  else:
    raise Exception("Invalid experiment configuration. Needs at least two keys 'Experiment.BaseName'\n"
                  + "and `Experiment.Number`.")

  return sCode
# --------------------------------------------------------------------------------------
def get_experiment_code_ex(base_name, number, variation=None, fold_number=None):
  if (base_name is not None) and (number is not None):
    nNumber = int(number)
    sVariation = None
    if variation is not None:
      sVariation = str(variation)
    nFoldNumber = None
    if fold_number is not None:
      nFoldNumber = int(fold_number)

    sCode = f"{base_name}_{nNumber:02d}"
    if variation is not None:
      sCode += "." + sVariation
    if nFoldNumber is not None:
      sCode += f"-{nFoldNumber:02d}"
  else:
    raise Exception("Invalid experiment code parts. Needs a base name and a number.")

  return sCode
# --------------------------------------------------------------------------------------
def experiment_number_and_variation(experiment_code):
  if type(experiment_code) == int:
    nNumber = int(experiment_code)
    sVariation = None
  else:
    sParts = experiment_code.split(".")
    nNumber = int(sParts[0])
    if len(sParts) > 1:
      sVariation = sParts[1]
    else:
      sVariation = None

  return nNumber, sVariation
# --------------------------------------------------------------------------------------
def experiment_code_and_timestamp(filename):
  sName, _ = os.path.splitext(os.path.split(filename)[1])
  sParts = re.split(r"_", sName, 2)
  sISODate = f"{sParts[0]}T{sParts[1][0:2]}:{sParts[1][2:4]}:{sParts[1][4:6]}"
  sExperimentCode = sParts[2]
  dRunTimestamp = datetime.fromisoformat(sISODate)
  return sExperimentCode, dRunTimestamp
# --------------------------------------------------------------------------------------






# =========================================================================================================================
class MLExperimentConfig(object):
  # --------------------------------------------------------------------------------------
  def __init__(self, filename=None, base_name=None, number=None, variation=None, fold_number=None, hyperparams=None):
    self._kv = dict()

    self["Experiment.BaseName"] = base_name
    self.filename = filename
    if self.filename is not None:
      self.load()

    if number is not None:
      self["Experiment.Number"] = number
    if variation is not None:
      self["Experiment.Variation"] = variation
    if fold_number is not None:
      self["Experiment.FoldNumber"] = fold_number

    if hyperparams is not None:
      self.assign(hyperparams)
  # --------------------------------------------------------------------------------------
  def __getitem__(self, key):
    return self._kv[key]
  # --------------------------------------------------------------------------------------
  def __setitem__(self, key, value):
    self._kv[key] = value
  # --------------------------------------------------------------------------------------
  def __contains__(self, key):
      return key in self._kv
  # --------------------------------------------------------------------------------------
  @property
  def experiment_code(self):
    return get_experiment_code(self)
  # --------------------------------------------------------------------------------------
  def assign(self, config_dict):
    for sKey in config_dict.keys():
      self[sKey] = config_dict[sKey]

    if (self["Experiment.BaseName"] is None) and ("ModelName" in config_dict):
      self["Experiment.BaseName"] = config_dict["ModelName"]
    if ("DatasetName" in config_dict):
      self["Experiment.BaseName"] += "_" + config_dict["DatasetName"]
    return self
  # --------------------------------------------------------------------------------------
  def save_to_json(self, filename=None):
    if filename is not None:
      self.filename = filename

    sJSON = json.dumps(self._kv, sort_keys=False, indent=4)
    with open(self.filename, "w") as oFile:
      oFile.write(sJSON)
      oFile.close()
    return self
  # --------------------------------------------------------------------------------------
  def save(self, fs=None, filename_only=None):
    if fs is None:
      fs = mlsys.filesys.configs
    elif isinstance(fs, FileSystem):
      fs = fs.configs
    elif not isinstance(fs, FileStore):
      raise Exception("Unsupporting persistent storage")

    if filename_only is None:
      filename_only = get_experiment_code(self)

    sFileName = fs.file(filename_only + ".json")
    return self.save_to_json(sFileName)
  # --------------------------------------------------------------------------------------
  def save_config(self, fs, filename_only):
    # Backwards compatibility 0.6.0
    return self.save()
  # --------------------------------------------------------------------------------------
  def load_from_json(self, filename=None, must_exist=False):
    if filename is None:
      filename = self.filename

    # reading the data from the file
    if os.path.exists(filename):
      with open(filename) as oFile:
        sConfig = oFile.read()
        self.setDefaults()
        dConfigDict = json.loads(sConfig)

      for sKey in dConfigDict.keys():
        self._kv[sKey] = dConfigDict[sKey]
    else:
      if must_exist:
        raise Exception("Experiment configuration file %s is not found." % filename)
    return self
  # --------------------------------------------------------------------------------------
  def load(self, fs=None, filename_only=None):
    if fs is None:
      fs = mlsys.filesys.configs
    elif isinstance(fs, FileSystem):
      fs = fs.configs
    elif not isinstance(fs, FileStore):
      raise Exception("Unsupporting persistent storage")

    if filename_only is None:
      filename_only = get_experiment_code(self)

    sFileName = fs.file(filename_only + ".json")
    return self.load_from_json(sFileName)
  # --------------------------------------------------------------------------------------
  def load_config(self, fs, filename_only):
    # Backwards compatibility 0.6.0
    return self.load(fs, filename_only)
  # --------------------------------------------------------------------------------------
  def setDefaults(self):
    pass
  # --------------------------------------------------------------------------------------
  def __str__(self)->str:
    sResult = ""
    for sKey in self._kv.keys():
      sResult += f'  {sKey}: \"{self[sKey]}\",\n'

    sResult = "{\n" + sResult + "}"
    return sResult
  # --------------------------------------------------------------------------------------------------------
  def __repr__(self)->str:
    return self.__str__()
  # --------------------------------------------------------------------------------------------------------

# =========================================================================================================================        


  