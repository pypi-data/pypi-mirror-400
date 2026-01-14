import hashlib
import numpy as np
from radnn import mlsys, FileStore

if mlsys.framework == "torch":
  import torch
elif mlsys.framework == "tensorflow":
  import tensorflow as tf
  

class TensorHash(object):
  def __init__(self, test_fs, filename):
    self.fs: FileStore = test_fs
    self.filename = filename
    self.hashes = []
    self.loaded_hashes = None
    self.is_loaded = False
  
  def collect_model_params(self, model):
    if mlsys.framework == "torch":
      for key, value in model.state_dict().items():
        # print(key, value.shape)
        self.collect_hash(value)
    return self
  
  def end_collection(self):
    if self.is_loaded:
      if self.compare():
        print(f"[v] {self.filename} Reproducibility for {len(self.hashes)} collected values")
      else:
        print(f"[x] {self.filename} Non deterministic behaviour!")
    else:
      self.save()
      
  def collect_hash(self, x: torch.Tensor, normalize_shape=True) -> str:
    if mlsys.framework == "torch":
      return self.calculate_hash_torch(x, normalize_shape)
    elif mlsys.framework == "tensorflow":
      return self.calculate_hash_tf(x, normalize_shape)
    else:
      return ""
  
  def calculate_hash_tf(self, x, normalize_shape: bool = True) -> str:
    if not tf.is_tensor(x):
      # allow numpy arrays too if you want:
      if isinstance(x, np.ndarray):
        x = tf.convert_to_tensor(x)
      else:
        raise TypeError("x must be a tf.Tensor (or numpy.ndarray)")
    
    t = x  # keep as tf.Tensor
    
    # Canonicalize shape to (28, 28, 1) if requested
    if normalize_shape:
      if t.shape.rank == 2:
        # (28, 28) -> (28, 28, 1)
        t = tf.expand_dims(t, axis=-1)
      elif t.shape.rank == 3:
        # (1, 28, 28) -> (28, 28, 1)  (common in CHW)
        # Only do this if first dim is 1.
        if t.shape[0] == 1:
          t = tf.transpose(t, perm=[1, 2, 0])
    
    # Canonicalize dtype
    if t.dtype.is_floating:
      t = tf.clip_by_value(t, 0.0, 1.0)
      t = tf.round(t * 255.0)
      t = tf.cast(t, tf.uint8)
    else:
      t = tf.cast(t, tf.uint8)
    
    # Hash raw bytes (ensure deterministic C-order bytes)
    # tf.io.serialize_tensor includes dtype/shape metadata, so we avoid it.
    b = t.numpy().tobytes(order="C")
    sResult = hashlib.sha256(b).hexdigest()
    self.hashes.append(sResult)
    return sResult
  
  def calculate_hash_torch(self, x: torch.Tensor, normalize_shape=True) -> str:
    if not isinstance(x, torch.Tensor):
      raise TypeError("x must be a torch.Tensor")
    
    # Move to CPU, detach, make contiguous
    t = x.detach().to("cpu").contiguous()
    
    # Canonicalize shape to (28, 28, 1) if requested
    if normalize_shape:
      if t.ndim == 2:  # (28,28)
        t = t.unsqueeze(-1)  # (28,28,1)
      elif t.ndim == 3 and t.shape[0] == 1:  # (1,28,28) -> (28,28,1)
        t = t.permute(1, 2, 0).contiguous()
    
    # Canonicalize dtype to avoid hash changing across float16/float32/etc.
    # If your data is in [0,1] floats, this will quantize deterministically.
    if t.dtype.is_floating_point:
      t = (t.clamp(0, 1) * 255.0).round().to(torch.uint8)
    else:
      # If already uint8/int, you can keep it; here we convert to uint8 for consistency.
      t = t.to(torch.uint8)
    
    # Hash raw bytes
    b = t.numpy().tobytes(order="C")
    sResult = hashlib.sha256(b).hexdigest()
    self.hashes.append(sResult)
    return sResult
  
  def save(self, filename=None):
    if filename is not None:
      self.filename = filename
    
    self.fs.text.save(self.hashes, self.filename)
    return self

  def load(self, filename=None):
    if filename is not None:
      self.filename = filename

    self.loaded_hashes = self.fs.text.load(self.filename)
    self.is_loaded = self.loaded_hashes is not None
    return self
  
  def compare(self):
    bResult = True
    if self.loaded_hashes is not None:
      for nIndex, sHash in enumerate(self.hashes):
        if sHash != self.hashes[nIndex]:
          bResult = False
          break
        
    return bResult
