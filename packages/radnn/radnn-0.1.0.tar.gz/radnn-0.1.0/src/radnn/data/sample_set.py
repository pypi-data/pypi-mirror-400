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
from .errors import *
from sklearn.utils.class_weight import compute_class_weight
from .sample_set_kind import SampleSetKindInfo

from radnn.core import RequiredLibs
oReqs = RequiredLibs()
if oReqs.is_torch_installed:
  # [TODO] Additional coupling to torch (+)->MANOLO
  import platform
  import torch
  from torch.utils.data import DataLoader


class SampleSet(object):
  LOADER_NUM_WORKERS = 8

  # --------------------------------------------------------------------------------------------------------------------
  def __init__(self, parent_dataset, subset_kind: str, **kwargs):
    '''
    Create a sample subset on a dataset

    :param parent_dataset: The parent dataset that implements the composition relationship.
    :param subset_kind: The kind of the subset. Can be one of:
            training/train/ts  for the known samples that are presented to an algorithm
            validation/val/vs  for the known samples that are not presented to an algorithm, used to validate during its execution
            testing/test/ut    for the unknown samples that are not given to the researcher that develops the algorithm

    :**param sample_file_records: A Pandas dataframe that contains two columns: 1) The list of sample file absolute paths and 2) Correspondng labels.
    :**param is_classification: True if the dataset used for a classification task.
    :**param batch_size: The count of samples in a minibatch.
    :**param sample_transform_augment: A callback method that performs a single sample preprocessing task.
    '''
    self.parent_dataset = parent_dataset
    self.info = SampleSetKindInfo(subset_kind)
    self.info.is_classification = kwargs.get("is_classification", False)
    self.batch_size = kwargs.get("batch_size", None)
    self.transform_augment = kwargs.get("sample_transform_augment", None)
    self._sample_count                      = 0

    self.ids                                = None
    self.samples: list|np.ndarray|None      = kwargs.get("samples", None)
    if (self.samples is not None) and isinstance(self.samples, list):
      self.samples = np.array(self.samples, np.float32)
    self._sample_count = self.samples.shape[0]
    self.labels: list|np.ndarray|None       = kwargs.get("labels", None)

    self.files                              = None
    self._sample_directory: pd.DataFrame | None  = kwargs.get("sample_file_records", None)
    if self._sample_directory is not None:
      self.files = self._sample_directory.iloc[:, 0].to_list()
      self._sample_count = len(self.files)
      self.labels       = self._sample_directory.iloc[:, 1].to_list()

    assert self._sample_count > 0, ERR_SUBSET_MUST_HAVE_SAMPLES
    self._step = 1
    self._iter_start_pos = 0
    self._iter_counter = 0
    self._are_samples_in_memory = self.samples is not None

    self.has_sample_ids = self.ids is not None

    self.minibatch_count = self._sample_count
    if self.batch_size is not None:
      self.loader = DataLoader(self, batch_size=self.batch_size, shuffle=self.info.must_shuffle,
                               num_workers=self.LOADER_NUM_WORKERS)
      self.minibatch_count = len(self.loader)
    else:
      self.loader = DataLoader(self, shuffle=self.info.must_shuffle, num_workers=self.LOADER_NUM_WORKERS)

    if self.info.is_classification:
      self.info.class_indices = np.sort(np.unique(self.labels))
      self.info.class_weights = compute_class_weight(class_weight='balanced', classes=self.info.class_indices, y=np.array(self.labels))
  # --------------------------------------------------------------------------------------------------------------------
  @property
  def sample_count(self):
    return self._sample_count
  # --------------------------------------------------------------------------------------------------------------------
  @property
  def has_labels(self):
    return self.labels is not None
  # --------------------------------------------------------------------------------------------------------------------
  @property
  def data_tuple(self):
    '''
    :return: For in-memory samples: A tuple with the samples, their respective labels and their ids.
             For file-based dataiterators: None
    '''
    if self._are_samples_in_memory:
      if self.has_sample_ids:
        if self.labels is None:
          return (self.ids, self.samples)
        else:
          return (self.ids, self.samples, self.labels)
      else:
        if self.labels is None:
          return self.samples
        else:
          return (self.ids, self.samples, self.labels)
    else:
      return None
  # --------------------------------------------------------------------------------------------------------------------
  def __len__(self):
    return self._sample_count
  # --------------------------------------------------------------------------------------------------------------------
  def __getitem__(self, index):
    if self._are_samples_in_memory:
      tSample = self.do_load_sample(index)
    else:
      tSample = self.do_load_sample_from_file(index)
    if self.transform_augment is not None:
      tSample = self.transform_augment(tSample)

    if self.ids is not None:
      if self.labels is not None:
        # Supervised with ids
        return self.ids[index], tSample, self.do_load_target(index)
      else:
        # Unsupervised with ids
        return self.ids[index], tSample
    else:
      if self.labels is not None:
        # Supervised
        return tSample, self.do_load_target(index)
      else:
        # Unsupervised
        return tSample
  # --------------------------------------------------------------------------------------------------------------------
  def __iter__(self):
    self._iter_counter = 0

    if self._are_samples_in_memory:
      if self.ids is not None:
        if self.labels is not None:
          yield from self._numpy_generator_for_supervised_with_ids()
        else:
          yield from self._numpy_generator_for_unsupervised_with_ids()
      else:
        if self.labels is not None:
          yield from self._numpy_generator_for_supervised()
        else:
          yield from self._numpy_generator_for_unsupervised()
    else:
      if self.labels is not None:
        yield from self._file_generator_for_supervised()
      else:
        yield from self._file_generator_for_unsupervised()
  # --------------------------------------------------------------------------------------------------------------------
  def do_load_sample_from_file(self, index):
    '''
    Override this method with the custom code of loading a single sample file
    :param index: The index of the sample in the sample file list
    '''
    pass
  # --------------------------------------------------------------------------------------------------------------------
  def do_load_sample(self, index):
    '''
    Override this method with the custom code of getting a single sample file from a numpy array
    :param index: The index of the sample in the sample subset
    :return:
    '''
    return torch.tensor(self.samples[index, ...], dtype=torch.float32)
  # --------------------------------------------------------------------------------------------------------------------
  def do_load_target(self, index):
    '''
    Override this method with some custom code that loads sample label(s) or transforms them into a training target (e.g. one-hot encoding)
    :param index: The index of the sample in the sample subset
    '''
    return torch.tensor(self.labels[index, ...], dtype=torch.long)
  # --------------------------------------------------------------------------------------------------------------------
  def _file_generator_for_supervised(self):
    nIndex = self._iter_start_pos
    while self._iter_counter < self.sample_count:
      tSample = self.do_load_sample_from_file(nIndex)
      if self.transform_augment is not None:
        tSample = self.transform_augment(tSample)
      yield (tSample, self.do_load_target(nIndex))
      nIndex += self._step
  # --------------------------------------------------------------------------------------------------------------------
  def _file_generator_for_unsupervised(self):
    nIndex = self._iter_start_pos
    while self._iter_counter < self.sample_count:
      tSample = self.do_load_sample_from_file(nIndex)
      if self.transform_augment is not None:
        tSample = self.transform_augment(tSample)
      yield (tSample)
      nIndex += self._step
  # --------------------------------------------------------------------------------------------------------------------
  def _numpy_generator_for_supervised(self):
    nIndex = self._iter_start_pos
    while self._iter_counter < self.sample_count:
      tSample = self.do_load_sample(nIndex)
      if self.transform_augment is not None:
        tSample = self.transform_augment(tSample)
      yield (tSample, self.do_load_target(nIndex))
      nIndex += self._step
  # --------------------------------------------------------------------------------------------------------------------
  def _numpy_generator_for_supervised_with_ids(self):
    nIndex = self._iter_start_pos
    while self._iter_counter < self.sample_count:
      tSample = self.do_load_sample(nIndex)
      if self.transform_augment is not None:
        tSample = self.transform_augment(tSample)
      yield (self.ids[nIndex], tSample, self.do_load_target(nIndex))
      nIndex += self._step
  # --------------------------------------------------------------------------------------------------------------------
  def _numpy_generator_for_unsupervised(self):
    nIndex = self._iter_start_pos
    while self._iter_counter < self.sample_count:
      tSample = self.do_load_sample(nIndex)
      if self.transform_augment is not None:
        tSample = self.transform_augment(tSample)
      yield tSample
      nIndex += self._step
  # --------------------------------------------------------------------------------------------------------------------
  def _numpy_generator_for_unsupervised_with_ids(self):
    nIndex = self._iter_start_pos
    while self._iter_counter < self.sample_count:
      tSample = self.do_load_sample(nIndex)
      if self.transform_augment is not None:
        tSample = self.transform_augment(tSample)
      yield (self.ids[nIndex], tSample)
      nIndex += self._step
  # --------------------------------------------------------------------------------------------------------------------
  def print_info(self):
    sDescription = self.info.kind_description
    sDescription = sDescription[0].upper() + sDescription[1:]
    sMinibatches = ""
    if self.minibatch_count is not None:
      sMinibatches = f" minbatches: {self.minibatch_count}"
    if (self.samples is not None) and isinstance(self.samples, np.ndarray):
      print(f"  |__ {sDescription} set samples: {self.sample_count}   shape: {self.samples.shape}{sMinibatches}")
      print(f"          |__ {sDescription} set labels: {self.sample_count}   shape: {self.labels.shape}")
    else:
      print(f"  |__ {sDescription} set samples: {self.sample_count} {sMinibatches}")

    if (self.labels is not None) and isinstance(self.labels, np.ndarray):
        print(f"      |__ Labels: {self.sample_count}   shape:{self.labels.shape}")
    else:
      print(f"      |__ Labels: {self.sample_count}")
  # --------------------------------------------------------------------------------------------------------------------
  def __str__(self):
    return f"{self.info.kind_description} samples:{self.sample_count} minibatches:{self.minibatch_count}"
  # --------------------------------------------------------------------------------------------------------------------
  def __repr__(self):
    return self.__str__()
  # --------------------------------------------------------------------------------------------------------------------


# Fix for torch on Windows
if platform.system().lower() == "windows":
  SampleSet.LOADER_NUM_WORKERS = 0
else:
  SampleSet.LOADER_NUM_WORKERS = 8
