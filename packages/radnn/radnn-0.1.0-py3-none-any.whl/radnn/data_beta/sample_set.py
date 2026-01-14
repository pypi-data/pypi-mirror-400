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
from .dataset_base import DataSetBase
from .subset_type import SubsetType



class SampleSet(object):
  # --------------------------------------------------------------------------------------------------------------------
  def __init__(self, subset_type="custom", has_ids=False):
    self.subset_type: SubsetType = SubsetType(subset_type)
    self.parent_dataset = None

    self.has_ids = has_ids

    self.ids    = None
    self.samples = None
    self.sample_count = None
    self.labels = None

    self._step = 1
    self._iter_start_pos = 0
    self._iter_counter = 0

    self.feed = None

  # --------------------------------------------------------------------------------------------------------------------
  @property
  def has_labels(self):
    return self.labels is not None
  # --------------------------------------------------------------------------------------------------------------------
  @property
  def data_tuple(self):
    if self.has_ids:
      if self.labels is None:
        return (self.ids, self.samples)
      else:
        return (self.ids, self.samples, self.labels)
    else:
      if self.labels is None:
        return self.samples
      else:
        return (self.ids, self.samples, self.labels)
  # --------------------------------------------------------------------------------------------------------------------
  def subset_of(self, parent_dataset: DataSetBase):
    self.parent_dataset = parent_dataset
    if self.parent_dataset is not None:
      if self.subset_type.is_training_set:
        if self.parent_dataset.ts_samples is not None:
          self.parent_dataset.ts = self
          self.ids = self.parent_dataset.ts_sample_ids
          self.samples = self.parent_dataset.ts_samples
          self.sample_count = self.parent_dataset.ts_sample_count
          self.labels = self.parent_dataset.ts_labels
      elif self.subset_type.is_validation_set:
        if self.parent_dataset.vs_samples is not None:
          self.parent_dataset.vs = self
          self.ids = self.parent_dataset.vs_sample_ids
          self.samples = self.parent_dataset.vs_samples
          self.sample_count = self.parent_dataset.vs_sample_count
          self.labels = self.parent_dataset.vs_labels
      elif self.subset_type.is_unknown_test_set:
        if self.parent_dataset.ut_samples is not None:
          self.parent_dataset.ut = self
          self.ids = self.parent_dataset.ut_sample_ids
          self.samples = self.parent_dataset.ut_samples
          self.sample_count = self.parent_dataset.ut_sample_count
          self.labels = self.parent_dataset.ut_labels

      self.has_ids = self.ids is not None
  # --------------------------------------------------------------------------------------------------------------------
  '''
  def create_feed(self, has_ids=False):
    self.has_ids = has_ids
    if is_tensorflow_installed:
      import tensorflow as tf

      if has_ids:
        self.feed = tf.data.Dataset.from_tensor_slices((self.ids, self.samples, self.labels))
      else:
        self.feed = tf.data.Dataset.from_tensor_slices((self.samples, self.labels))

      self.feed = self.feed.map(preprocess_tf, num_parallel_calls=8)

      if (self.subset_type == "training") or (self.subset_type == "train") or (self.subset_type == "ts"):
  # -----------------------------------------------------------------------------------
  def preprocess_tf(self, sample_pack):

    import tensorflow as tf

    if self.has_ids:
      nId, nSample, nLabel = sample_pack
    else:
      nSample, nLabel = sample_pack

    tImage = tf.cast(p_tImageInVS, tf.float32)  # //[BF] overflow of standardization
    tNormalizedImage = self.normalizeImage(tImage)

    tTargetOneHot = tf.one_hot(p_tLabelInVS, self.ClassCount)

    return tNormalizedImage, tTargetOneHot
  '''

  # --------------------------------------------------------------------------------------------------------------------
  def __iter__(self):
    self._iter_counter = 0
    if self.ids is not None:
      if self.labels is not None:
        yield from self._generator_for_supervised_with_ids()
      else:
        yield from self._generator_for_unsupervised_with_ids()
    else:
      if self.labels is not None:
        yield from self._generator_for_supervised()
      else:
        yield from self._generator_for_unsupervised()
  # --------------------------------------------------------------------------------------------------------------------
  def _generator_for_supervised(self):
    nIndex = self._iter_start_pos
    while self._iter_counter < self.sample_count:
      yield (self.samples[nIndex, ...], self.labels[nIndex, ...])
      nIndex += self._step
  # --------------------------------------------------------------------------------------------------------------------
  def _generator_for_unsupervised(self):
    nIndex = self._iter_start_pos
    while self._iter_counter < self.sample_count:
      yield self.samples[nIndex, ...]
      nIndex += self._step
  # --------------------------------------------------------------------------------------------------------------------
  def _generator_for_supervised_with_ids(self):
    nIndex = self._iter_start_pos
    while self._iter_counter < self.sample_count:
      yield (self.ids[nIndex], self.samples[nIndex, ...], self.labels[nIndex, ...])
      nIndex += self._step
  # --------------------------------------------------------------------------------------------------------------------
  def _generator_for_unsupervised_with_ids(self):
    nIndex = self._iter_start_pos
    while self._iter_counter < self.sample_count:
      yield (self.ids[nIndex], self.samples[nIndex, ...])
      nIndex += self._step
  # --------------------------------------------------------------------------------------------------------------------



