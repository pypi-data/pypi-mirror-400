# ======================================================================================
#
#     Rapid Deep Neural Networks
#
#     Licensed under the MIT License
# ______________________________________________________________________________________
# ......................................................................................

# Copyright (c) 2018-2026 Pantelis I. Kaplanoglou

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

# .......................................................................................
class Errors:
  MLSYS_NO_FILESYS = "No file system defined for the machine learning system. Create the object and assign the mlsys.filesys property."
  
  
HPARAMS_DATA_INPUT_DIMS = "Invalid data hyperparameters: The sample rank dimensions for the model's input tensor have not been defined."

FILESTORE_DATAFILE_KIND_NOT_SUPPORTED = "Data file kind {%s} is not supported."
TRAINER_LR_SCHEDULER_INVALID_SETUP = "The learning rate scheduler step list is missing or invalid."
TRAINER_LR_SCHEDULER_INVALID_MILESTONE_SETUP = "The learning rate change milestone list is missing or invalid."
TRAINER_LR_SCHEDULER_UNSUPPORTED = "The learning rate scheduler is not supported."
