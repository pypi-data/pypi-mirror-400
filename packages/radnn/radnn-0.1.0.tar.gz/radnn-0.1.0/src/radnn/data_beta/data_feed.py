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
from radnn.data_beta.preprocess import Normalizer, Standardizer

class DataFeed(object):
  def __init__(self, dataset: DataSetBase, subset_type):
    self.subset_type: SubsetType = None
    if isinstance(subset_type, SubsetType):
      self.subset_type = subset_type
    elif isinstance(subset_type, str):
      self.subset_type = SubsetType(subset_type)
    else:
      self.subset_type = None

    self.dataset = dataset
    self.feed = None
    self.pipeline_objects = []
    self.method_actions = []
    self.augmentations = []

    self.value_preprocessor = None
    self.padding_offset = None
    self.padding_target = None

    self.input_shape = self.dataset.sample_shape
    self.sample_count_to_shuffle = None
    if self.subset_type.is_training_set:
      self.sample_count_to_shuffle = self.dataset.ts_sample_count
    elif self.subset_type.is_validation_set:
      self.sample_count_to_shuffle = self.dataset.vs_sample_count
    elif self.subset_type.is_unknown_test_set:
      self.sample_count_to_shuffle = self.dataset.ut_sample_count
    self.batch_size  = None

    self._has_mapped_preprocessing_method = False
    self._is_multiclass = False

    self.feed = self.build_iterator()
    self.pipeline_objects.append(self.feed)
  # --------------------------------------------------------------------------------------------------------------------
  def multiclass(self):
    self._is_multiclass = True
    return self
  # --------------------------------------------------------------------------------------------------------------------
  def normalize(self):
    self.value_preprocessor = Normalizer(self.dataset.name, self.dataset.filestore)
    if self.value_preprocessor.min is None:
      self.value_preprocessor.fit(self.dataset.ts_samples)
    self.method_actions.append("normalize")
    if not self._has_mapped_preprocessing_method:
      self.feed = self.build_preprocessor(self.feed)
      self.pipeline_objects.append(self.feed)
      self._has_mapped_preprocessing_method = True
    return self
  # --------------------------------------------------------------------------------------------------------------------
  def map_preprocessing(self):
    if not self._has_mapped_preprocessing_method:
      self.feed = self.build_preprocessor(self.feed)
      self.pipeline_objects.append(self.feed)
      self._has_mapped_preprocessing_method = True
  # --------------------------------------------------------------------------------------------------------------------
  def standardize(self, axis_for_stats=None):
    self.value_preprocessor = Standardizer(self.dataset.name, self.dataset.filestore)
    if self.value_preprocessor.mean is None:
      self.value_preprocessor.fit(self.dataset.ts_samples, axis_for_stats=axis_for_stats)
    self.method_actions.append("standardize")
    self.map_preprocessing()
    return self
  # --------------------------------------------------------------------------------------------------------------------
  def random_shuffle(self):
    self.feed = self.build_random_shuffler(self.feed)
    self.pipeline_objects.append(self.feed)
    return self
  # --------------------------------------------------------------------------------------------------------------------
  def batch(self, batch_size):
    self.batch_size = batch_size
    self.feed = self.build_minibatch_maker(self.feed)
    self.pipeline_objects.append(self.feed)
    return self
# --------------------------------------------------------------------------------------------------------------------
  def augment_crop(self, padding_offset):
    self.padding_offset = padding_offset
    assert self.dataset.sample_shape is not None, "You should define the images input shape on the dataset"
    self.padding_target = self.dataset.sample_shape[0] + self.padding_offset
    self.map_preprocessing()
    self.feed = self.build_augmentation(self.feed, "random_crop")
    self.pipeline_objects.append(self.feed)
    return self
  # --------------------------------------------------------------------------------------------------------------------
  def augment_flip_left_right(self):
    self.map_preprocessing()
    self.feed = self.build_augmentation(self.feed, "random_flip_left_right")
    self.pipeline_objects.append(self.feed)
    return self
  # --------------------------------------------------------------------------------------------------------------------
  def augment_cutout(self):
    self.map_preprocessing()
    self.feed = self.build_augmentation(self.feed, "random_cutout")
    self.pipeline_objects.append(self.feed)
    return self
  # --------------------------------------------------------------------------------------------------------------------

  #// To be overrided \\
  # --------------------------------------------------------------------------------------------------------------------
  def build_iterator(self):
    return None
  # --------------------------------------------------------------------------------------------------------------------
  def build_preprocessor(self, feed):
    return feed
  # --------------------------------------------------------------------------------------------------------------------
  def add_augmentation(self, augmentation_kind):
    self.method_actions.add(augmentation_kind)
  # --------------------------------------------------------------------------------------------------------------------
  def build_random_shuffler(self, feed):
    return feed
# --------------------------------------------------------------------------------------------------------------------
  def build_minibatch_maker(self, feed):
    return feed
  # --------------------------------------------------------------------------------------------------------------------




