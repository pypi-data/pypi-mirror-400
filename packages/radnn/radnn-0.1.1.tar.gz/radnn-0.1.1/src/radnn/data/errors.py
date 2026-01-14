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
ERR_NO_CALLBACKS = "You should assign callbacks to the dataset perform proper random seed initialization for your framework."
ERR_NO_RANDOM_SEED_INITIALIZER_CALLBACK = "Callback method for random seed initialization has not been defined."

ERR_SUBSET_MUST_HAVE_TS = "A dataset must have at least a training subset."
ERR_SUBSET_INVALID_SETUP = "Invalid sample subset setup. Please use one of the valid kinds: 'training/train/ts', 'validation/val/vs', 'testing/test/us'."
ERR_SUBSET_MUST_HAVE_SAMPLES = "The subset has no samples, check the implementation of your dataset class."
ERR_DATASET_FOLDER_NOT_FOUND = "The dataset was not found under the folder %s"
ERR_DATASET_MUST_PROVIDE_LOCAL_FILESTORE = "You must provide a local filestore/path for the dataset"