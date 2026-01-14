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
import os
import random
import numpy as np
from .core import AIGridInfo, RequiredLibs
from .utils import classproperty
from radnn.system import FileSystem

class MLSystem(object):
  _instance = None
  
  @classproperty
  def instance(cls):
    if cls._instance is None:
      cls._instance = cls()
    return cls._instance

  # --------------------------------------------------------------------------------------
  def __init__(self):
    self._is_random_seed_initialized = False
    self._filesys = None
    self._seed = None
    self.switches = dict()
    self.switches["IsDebuggable"] = False
    self.req_libs: RequiredLibs = RequiredLibs()
    
    self.framework = "other"
    self.device = "CPU"
    
    # Ensure cuBLAS reproducibility for torch and/or tensorflow
    if self.req_libs.is_torch_installed:
      os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"  # https://docs.nvidia.com/cuda/cublas/index.html#cublasApi_reproducibility
      import torch
    if self.req_libs.is_tensorflow_installed:
      os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
      import tensorflow as tf
      
    
    if self.req_libs.is_tensorflow_installed:
      self.framework = "tensorflow"
    # By priority use torch for model trainers and data iterators (overrides co-existing tensorflow)
    if self.req_libs.is_torch_installed:
      self.framework = "torch"
    
    self._info = None

    # Initialize default device
    if self.framework == "torch":
      self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    elif self.framework == "tensorflow":
      gpus = tf.config.list_physical_devices("GPU")
      if gpus:
        tf.config.set_visible_devices(gpus[0], "GPU")
        tf.config.experimental.set_memory_growth(gpus[0], True)
        self.device = "/GPU:0"
      else:
        self.device = "/CPU:0"
  # --------------------------------------------------------------------------------------
  @property
  def info(self):
    if self._info is None:
      self._info = AIGridInfo()
      self.info.discover_devices(self.framework)
    return self._info
  # --------------------------------------------------------------------------------------
  @property
  def filesys(self) -> FileSystem:
    return self._filesys

  @filesys.setter
  def filesys(self, value):
    self._filesys = value
  # --------------------------------------------------------------------------------------
  @property
  def seed(self):
    return self._seed
  # --------------------------------------------------------------------------------------
  def random_seed_all(self, seed, is_done_once=False, is_parallel_deterministic=False):
    '''
    We are seeding the number generators to get some amount of determinism for the whole ML training process.
    For Tensorflow it is not ensuring 100% deterministic reproduction of an experiment that runs on the GPU.
    
    :param seed:
    :param is_done_once:
    :param is_parallel_deterministic:
    :return:
    '''
    self._seed = seed
    
    bContinue = True
    if is_done_once:
      bContinue = (not self._is_random_seed_initialized)
    
    if bContinue:
      random.seed(seed)
      os.environ['PYTHONHASHSEED'] = str(seed)
      np.random.seed(seed)
      if self.req_libs.is_tensorflow_installed:
        import tensorflow as tf
        tf.compat.v1.reset_default_graph()
        if is_parallel_deterministic:
          tf.config.experimental.enable_op_determinism()  # Enable determinism for num_parallel_calls
        tf.random.set_seed(seed)
        tf.keras.utils.set_random_seed(seed)
      if self.req_libs.is_torch_installed:
        import torch
        torch.manual_seed(seed)
        # GPU and multi-GPU
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        # For GPU determinism
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
        torch.use_deterministic_algorithms(True)
        
      self._is_random_seed_initialized = True
      print("(>) Random seed set to %d" % seed)
  # --------------------------------------------------------------------------------------


mlsys: MLSystem = MLSystem.instance




