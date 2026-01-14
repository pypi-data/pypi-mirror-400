from enum import Enum

class CNNSizeFactor(Enum):
  TINY = 1
  PETITE = 2
  SMALL = 3
  MEDIUM = 4


class CNNStemSetup(object):
  def __init__(self, size_factor: CNNSizeFactor, input_channels: int = 3, is_vit_like: bool = False):
    self.size_factor: CNNSizeFactor = size_factor
    self.input_channels = input_channels
    self.windows = []
    self.strides = []
    
    if is_vit_like:
      self.windows = [4]
      self.strides = [4]
    else:
      if self.size_factor is CNNSizeFactor.TINY:
        self.windows = [3]
        self.strides = [1]
      elif self.size_factor is CNNSizeFactor.PETITE:
        self.windows = [3]
        self.strides = [2]
      elif self.size_factor is CNNSizeFactor.SMALL:
        self.windows = [5]
        self.strides = [2]
      elif self.size_factor is CNNSizeFactor.MEDIUM:
        self.windows = [7, 3] #TODO: Check various papers
        self.strides = [2, 2]
      else:
        raise ValueError(f"Unknown CNN scale factor: {self.size_factor.name}")
    