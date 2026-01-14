# ......................................................................................
# MIT License

# Copyright (c) 2022-2025 Pantelis I. Kaplanoglou

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

from .sample_set import SampleSet
from .dataset_base import DataSetBase, DataSetCallbacks


# ----------------------------------------------------------------------------------------------------------------------
def generate_sequence_clips(samples, labels, window_size, stride, is_padding_zeros=False):
  nSequenceIndex = 0
  while nSequenceIndex < samples.shape[0]:
    nLabel = labels[nSequenceIndex]
    nPosition = 0
    nSpanPoints = window_size
    if is_padding_zeros:
      nSpanPoints = window_size - 3 * stride

    nDataPointCount = samples.shape[1]
    while (nPosition + nSpanPoints) <= nDataPointCount:
      if is_padding_zeros and ((nPosition + window_size) >= nDataPointCount):
        nSeqSample = np.zeros((window_size, samples.shape[2]), np.float32)
        nSeqSample[nPosition + window_size - nDataPointCount:, :] = samples[nSequenceIndex, nPosition:, :]
      else:
        nSeqSample = samples[nSequenceIndex, nPosition:nPosition + window_size, :]

      yield (nSeqSample, nLabel)

      nPosition += stride
    nSequenceIndex += 1
# ----------------------------------------------------------------------------------------------------------------------





class SequenceDataSet(DataSetBase):
  # --------------------------------------------------------------------------------------------------------------------
  def __init__(self, name: str, variant: str|None=None, file_store=None, random_seed: int | None=None, callbacks: DataSetCallbacks | None = None):
    super().__init__(name, variant, file_store, random_seed, callbacks)

    #self, name,  fs, clip_window_size=None, clip_stride=None, is_padding_zeros=False, random_seed=None, is_classification=True):
    #super(SequenceDataSet, self).__init__(name, fs, random_seed, is_classification)

    self.clip_window_size: int|None = None
    self.clip_stride: int|None = None
    self.is_padding_zeros: bool|None = None
  # --------------------------------------------------------------------------------------------------------------------
  def do_read_hyperparams(self):
    self.clip_window_size = self.hparams.get("Data.Clip.WindowSize", None)
    self.clip_stride = self.hparams.get("Data.Clip.Stride", None)
    self.is_padding_zeros = self.hparams.get("Data.Clip.IsPaddingZeroes", None)
  # --------------------------------------------------------------------------------------------------------------------
  def generate_clips(self, subset: SampleSet):
    return generate_sequence_clips(self, subset.samples, subset.labels,
                                   self.clip_window_size, self.clip_stride, self.is_padding_zeros)
  # --------------------------------------------------------------------------------------------------------------------
  def convert_samples_to_clips(self, clip_window_size=None, clip_stride=None, is_padding_zeros=False):
    if clip_window_size is not None:
      self.clip_window_size = clip_window_size
    if clip_stride is not None:
      self.clip_stride = clip_stride
    if is_padding_zeros and (not self.is_padding_zeros):
      self.is_padding_zeros = is_padding_zeros

    # TODO: Reinstate dataset card
    '''
    self.card["clips.window_size"] = self.clip_window_size
    self.card["clips.stride"] = self.clip_stride
    self.card["clips.is_padding_zeros"] = self.is_padding_zeros
    '''

    # Create training set clips
    oSubsets = [self.ts, self.vs, self.us]
    nClips = []
    nClipLabels = []
    for (nClip, nClipLabel) in self.generate_clips():
      nClips.append(nClip)
      nClipLabels.append(nClipLabel)
    nClips = np.asarray(nClips)
    nClipLabels = np.asarray(nClipLabels)
    self.assign_training_set(nClips, nClipLabels)

    # Create validation set clips
    if self.vs_samples is not None:
      nClips = []
      nClipLabels = []
      for (nClip, nClipLabel) in self.vs_sequence_clips:
        nClips.append(nClip)
        nClipLabels.append(nClipLabel)
      nClips = np.asarray(nClips)
      nClipLabels = np.asarray(nClipLabels)
      self.assign_validation_set(nClips, nClipLabels)

    # Create unknown test set clips
    if self.ut_samples is not None:
      nClips = []
      nClipLabels = []
      for (nClip, nClipLabel) in self.ut_sequence_clips:
        nClips.append(nClip)
        nClipLabels.append(nClipLabel)
      nClips = np.asarray(nClips)
      nClipLabels = np.asarray(nClipLabels)
      self.assign_unknown_test_set(nClips, nClipLabels)

    return self
  # --------------------------------------------------------------------------------------