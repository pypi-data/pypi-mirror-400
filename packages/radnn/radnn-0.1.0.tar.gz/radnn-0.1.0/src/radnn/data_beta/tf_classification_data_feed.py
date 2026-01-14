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

from radnn.core import RequiredLibs
oReqs = RequiredLibs()
if oReqs.is_tensorflow_installed:
  import tensorflow as tf
from radnn import mlsys
from radnn.data_beta.preprocess import Normalizer, Standardizer
from .data_feed import DataFeed

class TFClassificationDataFeed(DataFeed):
  # --------------------------------------------------------------------------------------------------------------------
  def do_random_crop(self, samples, labels):
    tPaddedImage = tf.image.pad_to_bounding_box(samples, self.padding_offset, self.padding_offset
                                                      , self.padding_target, self.padding_target)
    tResult = tf.image.random_crop(tPaddedImage, self.input_shape, seed=mlsys.seed)
    print("crop", tResult)
    return tResult, labels
  # --------------------------------------------------------------------------------------------------------------------
  def do_flip_left_right(self, samples, labels):
    tResult = tf.image.random_flip_left_right(samples, seed=mlsys.seed)
    print("flip", tResult)
    return tResult, labels
  # --------------------------------------------------------------------------------------------------------------------
  def build_augmentation(self, feed, augmentation_kind):
    if augmentation_kind == "random_crop":
      feed = feed.map(self.do_random_crop, num_parallel_calls=8)
    elif augmentation_kind == "random_flip_left_right":
      feed = feed.map(self.do_flip_left_right, num_parallel_calls=8)
    elif augmentation_kind == "random_cutout":
      pass # //TODO: Cutout
    return feed
  # --------------------------------------------------------------------------------------------------------------------
  def build_iterator(self):
    feed = None
    if self.subset_type.is_training_set:
      feed = tf.data.Dataset.from_tensor_slices((self.dataset.ts_samples, self.dataset.ts_labels))
    elif self.subset_type.is_validation_set:
      feed = tf.data.Dataset.from_tensor_slices((self.dataset.vs_samples, self.dataset.vs_labels))
    elif self.subset_type.is_unknown_test_set:
      feed = tf.data.Dataset.from_tensor_slices((self.dataset.ut_samples, self.dataset.ut_labels))
    return feed
  # --------------------------------------------------------------------------------------------------------------------
  def preprocess_normalize_onehot(self, samples, labels):
    tSamples = tf.cast(samples, tf.float32)
    tSamples = (tSamples - self.value_preprocessor.min) / (self.value_preprocessor.max - self.value_preprocessor.min)
    tTargetsOneHot = tf.one_hot(labels, self.dataset.class_count)
    return tSamples, tTargetsOneHot
  # --------------------------------------------------------------------------------------------------------------------
  def preprocess_standardize_onehot(self, samples, labels):
    tSamples = tf.cast(samples, tf.float32)
    tSamples = (tSamples - self.value_preprocessor.mean) / self.value_preprocessor.std
    tTargetsOneHot = tf.one_hot(labels, self.dataset.class_count)
    return tSamples, tTargetsOneHot
  # --------------------------------------------------------------------------------------------------------------------
  def preprocess_normalize(self, samples, labels):
    tSamples = tf.cast(samples, tf.float32)
    tSamples = (tSamples - self.value_preprocessor.min) / (self.value_preprocessor.max - self.value_preprocessor.min)
    return tSamples, labels
  # --------------------------------------------------------------------------------------------------------------------
  def preprocess_standardize(self, samples, labels):
    tSamples = tf.cast(samples, tf.float32)
    tSamples = (tSamples - self.value_preprocessor.mean) / self.value_preprocessor.std
    return tSamples, labels
  # --------------------------------------------------------------------------------------------------------------------
  def build_preprocessor(self, feed):
    if self._is_multiclass:
      if isinstance(self.value_preprocessor, Standardizer):
        feed = feed.map(self.preprocess_standardize_onehot, num_parallel_calls=8)
      elif isinstance(self.value_preprocessor, Normalizer):
        feed = feed.map(self.preprocess_normalize_onehot, num_parallel_calls=8)
    else:
      if isinstance(self.value_preprocessor, Standardizer):
        feed = feed.map(self.preprocess_standardize, num_parallel_calls=8)
      elif isinstance(self.value_preprocessor, Normalizer):
        feed = feed.map(self.preprocess_normalize, num_parallel_calls=8)
    return feed
  # --------------------------------------------------------------------------------------------------------------------
  def build_random_shuffler(self, feed):
    feed = feed.shuffle(self.sample_count_to_shuffle, seed=mlsys.seed)
    return feed
  # --------------------------------------------------------------------------------------------------------------------
  def build_minibatch_maker(self, feed):
    feed = feed.batch(self.batch_size)
    return feed
  # --------------------------------------------------------------------------------------------------------------------


