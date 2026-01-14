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
import os
import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
from .sample_set import SampleSet
from .sample_set_kind import SampleSetKind
from .sample_preprocessor import SamplePreprocessor, VoidPreprocessor
from .errors import *
from radnn import FileStore

# ======================================================================================================================
class DataSetCallbacks(object):
  # --------------------------------------------------------------------------------------------------------------------
  def __init__(self, lazy_loader=None, random_seeder=None):
    self.lazy_loader = lazy_loader
    self.random_seeder = random_seeder
  # --------------------------------------------------------------------------------------------------------------------
  def lazy_load(self):
    self.lazy_loader()
  # --------------------------------------------------------------------------------------------------------------------
  def initialize_random_seed(self, seed: int):
    self.random_seeder(seed)
  # --------------------------------------------------------------------------------------------------------------------


# ======================================================================================================================
class DataSetBase(ABC):
  # --------------------------------------------------------------------------------------------------------------------
  # Constructor
  def __init__(self, name: str, variant: str|None=None, file_store=None, random_seed: int | None=None, callbacks: DataSetCallbacks | None = None):
    # ..................// Instance Fields \\.........................
    self.fs: FileStore|None = file_store
    if (file_store is not None) and isinstance(file_store, str):
      if not os.path.exists(file_store):
        raise Exception(ERR_DATASET_FOLDER_NOT_FOUND % file_store)
      self.fs = FileStore(file_store)
    assert self.fs is not None, ERR_DATASET_MUST_PROVIDE_LOCAL_FILESTORE

    self.name                 = name
    self.variant              = variant
    self.random_seed          = random_seed
    self.callbacks: DataSetCallbacks = callbacks

    self.hparams :dict|None = None
    self.ts: SampleSet|None = None
    self.vs: SampleSet|None = None
    self.ut: SampleSet|None = None
    self.preprocessor: SamplePreprocessor = VoidPreprocessor(self)
    # ................................................................
    if (self.random_seed is not None):
      assert self.callbacks is not None, ERR_NO_CALLBACKS
      assert self.callbacks.random_seeder is not None, ERR_NO_RANDOM_SEED_INITIALIZER_CALLBACK
      self.callbacks.initialize_random_seed(self.random_seed)

  # --------------------------------------------------------------------------------------------------------------------
  @property
  def filesystem_folder(self):
      return self.fs.absolute_path
  # --------------------------------------------------------------------------------------------------------------------
  @abstractmethod
  def do_read_hyperparams(self):
    pass # must implement concrete method
  # --------------------------------------------------------------------------------------------------------------------
  @abstractmethod
  def do_import_data(self):
    pass # must implement concrete method
  # --------------------------------------------------------------------------------------------------------------------
  @abstractmethod
  def do_prepare_data(self):
    pass # could optionally override
  # --------------------------------------------------------------------------------------------------------------------
  @abstractmethod
  def do_create_sample_sets(self):
    pass # must implement concrete method
  # --------------------------------------------------------------------------------------------------------------------
  def prepare(self, hyperparams: dict|None = None):
    self.hparams = hyperparams
    if self.hparams is not None:
      self.do_read_hyperparams()

    if (self.callbacks is not None):
      if self.callbacks.lazy_loader is not None:
        self.callbacks.lazy_loader()
    self.do_import_data()
    self.do_prepare_data()

    self.ts = None
    self.vs = None
    self.us = None
    self.do_create_sample_sets()

    assert self.ts is not None, ERR_SUBSET_MUST_HAVE_TS
    assert self.ts.info.kind == SampleSetKind.TRAINING_SET.value, ERR_SUBSET_INVALID_SETUP
    if self.vs is not None:
      assert self.ts.info.kind == SampleSetKind.TRAINING_SET.value, ERR_SUBSET_INVALID_SETUP
    if self.us is not None:
      assert self.ts.info.kind == SampleSetKind.TRAINING_SET.value, ERR_SUBSET_INVALID_SETUP
  # --------------------------------------------------------------------------------------------------------------------
  def assign(self, data, label_columns: range):
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

      if label_columns is None:
        self.samples = nData
      else:
        if label_columns.start >= 0:
          if label_columns.stop is None:
            self.labels = nData[:, label_columns.start]
            self.samples = nData[:, label_columns.start + 1:]
          else:
            self.labels = nData[:, label_columns.start:label_columns.stop + 1]
            self.samples = nData[:, label_columns.stop + 1:]
        else:
          self.samples = nData[:, :label_columns.start]
          self.labels  = nData[:, label_columns.start:]
    return self
  # --------------------------------------------------------------------------------------------------------------------
  def print_info(self):
    if self.variant is not None:
      print(f"Dataset [{self.name}] {self.variant}")
    else:
      print(f"Dataset [{self.name}]")
    self.ts.print_info()
    if self.vs is not None:
      self.vs.print_info()
    if self.ut is not None:
      self.ut.print_info()
  # --------------------------------------------------------------------------------------------------------------------
