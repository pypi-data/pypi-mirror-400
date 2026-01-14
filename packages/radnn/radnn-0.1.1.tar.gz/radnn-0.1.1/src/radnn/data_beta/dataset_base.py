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
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from radnn import FileSystem, FileStore, MLSystem, Errors


class DataSetBase(object):
  # --------------------------------------------------------------------------------------------------------------------
  # Constructor
  def __init__(self, fs=None, name=None, variant=None, random_seed=None, is_classification=False):
    # ..................// Instance Fields \\.........................
    self.name                = name
    self.fs                  = fs
    self.variant             = variant
    self.ts = None
    self.vs = None
    self.ut = None

    if self.fs is None:
      if MLSystem.Instance().filesys is not None:
        self.fs = MLSystem.Instance().filesys
      else:
        raise Exception(Errors.MLSYS_NO_FILESYS)

    if self.fs is not None:
      if isinstance(self.fs, FileSystem):
        if variant is not None:
          name = name + "_" + variant
        self.filestore = self.fs.datasets.subfs(name.upper())
      elif isinstance(self.fs, FileStore):
        self.filestore = self.fs
      elif isinstance(self.fs, str):
        self.filestore = FileStore(self.fs)
      else:
        raise Exception("The parameter fs could be a path, a filestore or a filesystem")
    else:
      raise Exception("Could not determine the filestore for the dataset")

    self.random_seed         = random_seed
    self.is_classification   = is_classification
    
    self.feature_count       = None
    self.class_count         = None
    self.class_names         = None
    self.sample_count        = None
    
    self.samples             = None
    self.labels              = None
    
    self.ts_sample_ids       = None
    self.ts_samples          = None
    self.ts_labels           = None
    self.ts_sample_count     = 0
    
    self.vs_sample_ids       = None
    self.vs_samples          = None
    self.vs_labels           = None
    self.vs_sample_count     = 0
    
    self.ut_sample_ids       = None
    self.ut_samples          = None
    self.ut_labels           = None
    self.ut_sample_count     = None

    self.sample_shape = None

    self.card = dict()
    self.card["name"] = name
    # ................................................................
    if self.random_seed is not None:
      MLSystem.Instance().random_seed_all(self.random_seed)

  # --------------------------------------------------------------------------------------------------------------------
  def open(self):
    pass
  # --------------------------------------------------------------------------------------------------------------------
  def close(self):
    pass
  # --------------------------------------------------------------------------------------------------------------------
  def for_classification(self, class_count, class_names=None):
    self.is_classification = True
    self.class_count = class_count
    if class_names is not None:
      # We assume class_names is a dictionary, in other cases we turn it into a dictionary
      if isinstance(class_names, set) or isinstance(class_names, list):
        dClassNames = dict()
        for nIndex, sClassName in enumerate(class_names):
          dClassNames[nIndex] = sClassName
        class_names = dClassNames
      self.class_names = class_names
    return self
  # --------------------------------------------------------------------------------------------------------------------
  def count_samples(self):
    if self.ts_samples is not None:
      self.ts_sample_count = int(self.ts_samples.shape[0])
      self.sample_count = self.ts_sample_count + self.vs_sample_count

    if self.vs_samples is not None:
      self.vs_sample_count = int(self.vs_samples.shape[0])
      self.sample_count = self.ts_sample_count + self.vs_sample_count

    # The test set samples are not included in the available sample count
    if self.ut_samples is not None:
      self.ut_sample_count = int(self.ut_samples.shape[0])
  # --------------------------------------------------------------------------------------------------------------------
  def assign(self, data, label_start_column=None, label_end_column=None):
    if isinstance(data, tuple):
      self.samples, self.labels = data
    elif isinstance(data, np.ndarray):
      self.samples = data
    elif isinstance(data, dict):
      if ("samples" in dict) and ("labels" in dict):
        self.samples = data["samples"]
        self.labels = data["labels"]
      else:
        pass # Support other formats
    elif isinstance(data, pd.DataFrame):
      if isinstance(data.columns, pd.Index):
        nData = data.iloc[1:].to_numpy()
      else:
        nData = data.to_numpy()

      if label_start_column is None:
        self.samples = nData
      else:
        if label_start_column >= 0:
          if label_end_column is None:
            self.labels = nData[:, label_start_column]
            self.samples = nData[:, label_start_column + 1:]
          else:
            self.labels = nData[:, label_start_column:label_end_column + 1]
            self.samples = nData[:, label_end_column + 1:]
        else:
          self.samples = nData[:, :label_start_column]
          self.labels  = nData[:, label_start_column:]
    return self
  # --------------------------------------------------------------------------------------------------------------------
  def assign_training_set(self, samples, labels):
    self.ts_samples = samples
    self.ts_labels = labels
    self.count_samples()
    self.ts_sample_ids = np.arange(0, self.ts_sample_count)
        
    # Feature count is calculated on samples that are flattened as vectors
    if self.feature_count is None:
      self.feature_count = np.prod(self.ts_samples.shape[1:])
      
    if self.class_count is None:
      if self.is_classification:
        self.class_count = len(np.unique(self.ts_labels))
      else:
        self.class_count = 0
    return self
  # --------------------------------------------------------------------------------------------------------------------
  def assign_validation_set(self, samples, labels):
    self.vs_samples = samples
    self.vs_labels = labels
    self.count_samples()
    self.vs_sample_ids = np.arange(0, self.vs_sample_count)

    return self
  # --------------------------------------------------------------------------------------------------------------------
  def assign_unknown_test_set(self, samples, labels):
    self.ut_samples = samples
    self.ut_labels = labels
    self.count_samples()
    self.ut_sample_ids = np.arange(0, self.ut_sample_count)

    return self
  # --------------------------------------------------------------------------------------------------------------------
  def infox(self):
    self.print_info()
  # --------------------------------------------------------------------------------------------------------------------
  def print_info(self):
    print("Dataset [%s]" % self.name)
    print("  |__ FeatureCount:", self.feature_count)
    if self.is_classification:
      print("  |__ ClassCount:", self.class_count)
      if self.class_names is not None:
        print("        |__ Classes:", self.class_names)
    
    if self.ts_samples is not None:
      print("  |__ Training set samples  : %d   shape:%s" % (self.ts_sample_count, self.ts_samples.shape))
    if self.ts_labels is not None:
      print("  |__ Training set targets  : %d   shape:%s" % (self.ts_sample_count, self.ts_labels.shape))
      
    if self.vs_samples is not None:
      print("  |__ Validation set samples: %d   shape:%s" % (self.vs_sample_count, self.vs_samples.shape))
    if self.vs_labels is not None:
      print("  |__ Validation set targets: %d   shape:%s" % (self.vs_sample_count, self.vs_labels.shape))
      
    if self.ut_samples is not None:
      print("  |__ MemoryTest set samples      : %d   shape:%s" % (self.ut_sample_count, self.ut_samples.shape))
    if self.ut_labels is not None:
      print("  |__ MemoryTest set targets      : %d   shape:%s" % (self.ut_sample_count, self.ut_labels.shape))
  # --------------------------------------------------------------------------------------------------------------------
  def split(self, training_samples_pc, random_seed=None):
    if random_seed is None:
      random_seed = self.random_seed

    nTSSamples, nVSSamples, nTSTargets, nVSTargets = train_test_split(self.samples, self.labels
                                                                      , test_size=1.0 - training_samples_pc
                                                                      , random_state=random_seed
                                                                      , shuffle=True
                                                                      , stratify=self.labels
                                                                      )
    self.assign_training_set(nTSSamples, nTSTargets)
    self.assign_validation_set(nVSSamples, nVSTargets)
    self.count_samples()
    return self
  # --------------------------------------------------------------------------------------------------------------------
  def has_cache(self, samples_file_prefix="Samples"):
    return self.filestore.exists("%s.pkl" % samples_file_prefix) or self.filestore.exists("%s.TS.pkl" % samples_file_prefix)
  # --------------------------------------------------------------------------------------------------------------------
  def load_cache(self, filestore: FileStore = None, samples_file_prefix="Samples", targets_file_prefix="Labels", ids_file_prefix="Ids", is_verbose=False):
    if filestore is None:
      filestore = self.filestore
    if filestore is None:
      raise Exception("To use load_cache() without providing a filestore, you should provide a filesystem or filestore during instantiation.")

    bResult = filestore.exists("%s.pkl" % samples_file_prefix) or filestore.exists("%s.TS.pkl" % samples_file_prefix)
    
    if bResult:
      if is_verbose:
        print("Loading known data set ...")

      dInfo = filestore.json.load(f"{self.name}_info.json")
      if dInfo is not None:
        if "class_names" in dInfo:    self.class_names = dInfo["class_names"]
        if "feature_count" in dInfo:  self.feature_count = dInfo["feature_count"]
        if "class_count" in dInfo:
          self.is_classification = True
          self.class_count = dInfo["class_count"]

      self.samples   = filestore.obj.load("%s.pkl" % samples_file_prefix)
      self.labels    = filestore.obj.load("%s.pkl" % targets_file_prefix)

      if is_verbose:
        print("Loading training set ...")      
      nTSSamples  = filestore.obj.load("%s.TS.pkl" % samples_file_prefix)
      nTSTargets   = filestore.obj.load("%s.TS.pkl" % targets_file_prefix)
      self.assign_training_set(nTSSamples, nTSTargets)
      nTSIDs = filestore.obj.load("%s.TS.pkl" % ids_file_prefix)
      if nTSIDs is not None:
        self.ts_sample_ids = nTSIDs

      if is_verbose:
        print("Loading validation set ...")            
      nVSSamples  = filestore.obj.load("%s.VS.pkl" % samples_file_prefix)
      nVSTargets  = filestore.obj.load("%s.VS.pkl" % targets_file_prefix)
      self.assign_validation_set(nVSSamples, nVSTargets)
      nVSIds = filestore.obj.load("%s.VS.pkl" % ids_file_prefix)
      if nVSIds is not None:
        self.vs_sample_ids = nVSIds

      if is_verbose:
        print("Loading unknown test data set ...")            
      nUTSamples  = filestore.obj.load("%s.UT.pkl" % samples_file_prefix)
      if nUTSamples is not None:
        nUTTargets   = filestore.obj.load("%s.UT.pkl" % targets_file_prefix)
        self.assign_unknown_test_set(nUTSamples, nUTTargets)
      nUTIds = filestore.obj.load("%s.UT.pkl" % ids_file_prefix)
      if nUTIds is not None:
        self.ut_sample_ids = nUTIds


    return bResult
  # --------------------------------------------------------------------------------------------------------------------
  def save_cache(self, filestore: FileStore = None, samples_file_prefix="Samples", targets_file_prefix="Labels", ids_file_prefix="Ids"):
    if filestore is None:
      filestore = self.filestore
    if filestore is None:
      raise Exception("To use save_cache() without providing a filestore, you should provide a filesystem or filestore during instantiation.")

    if self.samples is not None:
      filestore.obj.save(self.samples, "%s.pkl" % samples_file_prefix, is_overwriting=True)
      filestore.obj.save(self.labels, "%s.pkl" % targets_file_prefix, is_overwriting=True)

    filestore.obj.save(self.ts_samples, "%s.TS.pkl" % samples_file_prefix, is_overwriting=True)
    filestore.obj.save(self.ts_labels, "%s.TS.pkl" % targets_file_prefix, is_overwriting=True)
    filestore.obj.save(self.ts_sample_ids, "%s.TS.pkl" % ids_file_prefix, is_overwriting=True)

    filestore.obj.save(self.vs_samples, "%s.VS.pkl" % samples_file_prefix, is_overwriting=True)
    filestore.obj.save(self.vs_labels, "%s.VS.pkl" % targets_file_prefix, is_overwriting=True)
    filestore.obj.save(self.vs_sample_ids, "%s.VS.pkl" % ids_file_prefix, is_overwriting=True)

    if self.ut_samples is not None:
      filestore.obj.save(self.ut_samples, "%s.UT.pkl" % samples_file_prefix, is_overwriting=True)
      filestore.obj.save(self.ut_labels, "%s.UT.pkl" % targets_file_prefix, is_overwriting=True)
      filestore.obj.save(self.ut_sample_ids, "%s.UT.pkl" % ids_file_prefix, is_overwriting=True)

    self.card["name"] = self.name
    if self.feature_count is not None:
      self.card["feature_count"] = int(self.feature_count)
    else:
      self.card["feature_count"] = self.feature_count

    if self.random_seed is not None:
      self.card["random_seed"] = int(self.random_seed)
    else:
      self.card["random_seed"] = self.random_seed

    if self.is_classification:
      if self.class_count is not None:
        self.card["class_count"] = int(self.class_count)
      else:
        self.card["class_count"] = self.class_count
      self.card["class_names"] = self.class_names

    filestore.json.save(self.card, f"{self.name}_card.json", is_sorted_keys=False)
  # --------------------------------------------------------------------------------------------------------------------

  
