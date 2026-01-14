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
from radnn import FileStore
from .dataset_base import DataSetBase

class ImageDataSet(DataSetBase):
  # --------------------------------------------------------------------------------------------------------------------
  def __init__(self, fs, name=None, variant=None, image_shape=None, random_seed=None, is_classification=True):
    super(ImageDataSet, self).__init__(fs, name, variant, random_seed, is_classification)

    self.image_shape = None
    self.feature_count = None
    if image_shape is not None:
      self.image_shape = image_shape
      self.feature_count = int(np.prod(list(image_shape)))

    self.source_fs = None
    self.source_class_subfs_list = None
    self.image_file_list = None
  # --------------------------------------------------------------------------------------------------------------------
  def build(self, source_fs):
    self.source_fs = source_fs
    # If a path is supplied init the file store
    if isinstance(source_fs, str):
      self.source_fs = FileStore(source_fs)

    if self.is_classification:
      self._determine_classes()
      self._detect_class_subfilestores()

    self._generate_image_file_list()
    #TODO: Image preprocess / resize / save shard

    return self
  # --------------------------------------------------------------------------------------------------------------------
  def _determine_classes(self):

    if self.class_names is None:
      # TODO: Detect a JSON file that has the class names dictionary on the source filestore
      pass
      # TODO: Enumerate all subfolder in the source filestore

  # --------------------------------------------------------------------------------------------------------------------
  def _detect_class_subfilestores(self):
    self.source_class_subfs_list = []
  # --------------------------------------------------------------------------------------------------------------------
  def _generate_image_file_list(self):
    self.image_file_list = []
  # --------------------------------------------------------------------------------------------------------------------
  def preview_images(self):
    import matplotlib.pyplot as plt

    # Look at some sample images from dataset
    plt.figure(figsize=(10, 10))
    for i in range(25):
      plt.subplot(5, 5, i + 1)
      if self.ts_samples.shape[2] == 2:
        plt.imshow(self.ts_samples[i].squeeze().astype(np.uint8), cmap='gray')
      else:
        plt.imshow(self.ts_samples[i].squeeze().astype(np.uint8))

      nClassIndex = self.ts_labels[i]
      sClassDescr = str(nClassIndex)
      if isinstance(self.class_names, dict):
        if nClassIndex in self.class_names:
          sClassName = self.class_names[nClassIndex]
          sClassDescr += " `" + sClassName + "`"
      elif isinstance(self.class_names, list):
        sClassName = self.class_names[nClassIndex]
        sClassDescr += " `" + sClassName + "` "

      plt.title(f"Label: {sClassDescr}")
      plt.axis('off')
    plt.show()
  # --------------------------------------------------------------------------------------------------------------------
