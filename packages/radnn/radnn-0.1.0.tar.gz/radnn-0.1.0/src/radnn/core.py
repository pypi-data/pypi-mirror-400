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
import sys
import socket
import platform
import psutil
import subprocess
from datetime import datetime
import importlib
import importlib.util


class RequiredLibs(object):
  def __init__(self):
    self.is_tensorflow_installed = importlib.util.find_spec("tensorflow") is not None
    if not self.is_tensorflow_installed:
      self.is_tensorflow_installed = importlib.util.find_spec("tensorflow-gpu") is not None
    self.is_torch_installed = importlib.util.find_spec("torch") is not None
    self.is_opencv_installed = importlib.util.find_spec("cv2") is not None




# ----------------------------------------------------------------------------------------------------------------------
def system_name() -> str:
  return MLInfrastructure.host_name(False)
# ----------------------------------------------------------------------------------------------------------------------
def now_iso():
  return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
# ----------------------------------------------------------------------------------------------------------------------
def shell_command_output(command_string):
  oOutput = subprocess.check_output(command_string, shell=True)
  oOutputLines = oOutput.decode().splitlines()

  oResult = []
  for sLine in oOutputLines:
      oResult.append(sLine)

  return oResult
# ----------------------------------------------------------------------------------------------------------------------





# ======================================================================================================================
class MLInfrastructure(object):
  # --------------------------------------------------------------------------------------------------------------------
  @classmethod
  def is_linux(cls):
    return not (cls.is_windows or cls.is_colab or cls.is_macos())
  # --------------------------------------------------------------------------------------------------------------------
  @classmethod
  def is_windows(cls):
    sPlatform = platform.system()
    return (sPlatform == "Windows")
  # --------------------------------------------------------------------------------------------------------------------
  @classmethod
  def is_colab(cls):
    return "google.colab" in sys.modules
  # --------------------------------------------------------------------------------------------------------------------
  @classmethod
  def is_macos(cls):
    sPlatform = platform.system()
    return (sPlatform == "Darwin")
  # --------------------------------------------------------------------------------------------------------------------
  @classmethod
  def host_name(cls, is_using_ip_address=True) -> str:
    sPlatform = platform.system()
    sHostName = socket.gethostname()
    sIPAddress = socket.gethostbyname(sHostName)

    bIsColab = "google.colab" in sys.modules
    if bIsColab:
      sResult = "(colab)"
      if is_using_ip_address:
        sResult += "-" + sIPAddress
    else:
      if sPlatform == "Windows":
        sResult = "(windows)-" + sHostName
      elif sPlatform == "Darwin":
        sResult = "(macos)-" + sHostName
      else:
        sResult = "(linux)-" + sHostName
    return sResult
  # --------------------------------------------------------------------------------------------------------------------
# ======================================================================================================================



# ======================================================================================================================
class HardwareDevice(object):
  def __init__(self, name):
    self.name = name

  def __str__(self):
    return self.name
  
  def __repr__(self):
    return self.__str__()
    
    
# ======================================================================================================================
class CPU(HardwareDevice):
  # --------------------------------------------------------------------------------------------------------------------
  def __init__(self, name):
    super(CPU, self).__init__(name)
    self._cpuid()
  # --------------------------------------------------------------------------------------------------------------------
  def _cpuid(self):
    '''
    CPU Identification for both Windows and Linux
    '''
    sPlatform = platform.system()
    
    if sPlatform == "Windows":
      oCPUs = subprocess.check_output(
        ["powershell", "-Command",
         "(Get-CimInstance Win32_Processor | Select-Object -ExpandProperty Name) -join \"\n\""],
        text=True
      ).strip().splitlines()
      
      self.name = ""
      for sCPU in oCPUs:
        self.name += f', {sCPU}'
      
    elif sPlatform == "Darwin":
      pass #MacOS
    else:
      self.name = ""
      with open("/proc/cpuinfo") as f:
        for line in f:
          line = line.strip()
          if line.startswith("model name"):
            self.name += f', {line.split(":", 1)[1].strip()}'
    if self.name.startswith(", "):
      self.name = self.name[2:]
  # --------------------------------------------------------------------------------------------------------------------


# ======================================================================================================================
class NeuralProcessingUnit(HardwareDevice):
  def __init__(self, name):
    super(NeuralProcessingUnit, self).__init__(name)
    self.compute_capability = None
    self.vram_in_gb = None
    
    
# ======================================================================================================================
class AIGridInfo(HardwareDevice):
  # --------------------------------------------------------------------------------------------------------------------
  def __init__(self, name=None):
    self.name = name
    if self.name is None:
      self.name = socket.gethostname()
    self.cpu = CPU(platform.processor())
    
    mem = psutil.virtual_memory()
    total_bytes = mem.total
    self.ram_in_gb = round(total_bytes / (1024 ** 3))
    
    self.devices = []
  # --------------------------------------------------------------------------------------------------------------------
  @property
  def device(self):
    if len(self.devices) > 0:
      return self.devices[0]
    else:
      return self.cpu
  # --------------------------------------------------------------------------------------------------------------------
  def discover_devices(self, framework_type: str = "torch"):
    '''
    Detects the AI accelerators using the framework libraries
    :param framework_type: The framework that is used "torch" or "tensorflow"
    :return:
    '''
    self.cpu = CPU(platform.processor())
    
    if framework_type == "torch":
      import torch
      device_count = torch.cuda.device_count()
      for i in range(device_count):
        oUnit = NeuralProcessingUnit(torch.cuda.get_device_name(i))
        oUnit.compute_capability = torch.cuda.get_device_capability(i)
        oUnit.vram_in_gb = round(torch.cuda.get_device_properties(i).total_memory / (1024 ** 3))
        self.devices.append(oUnit)
    elif framework_type == "tensorflow":
      import tensorflow as tf
      gpus = tf.config.list_physical_devices("GPU")
      for gpu in gpus:
        details = tf.config.experimental.get_device_details(gpu)
        oUnit = NeuralProcessingUnit(details["device_name"])
        oUnit.compute_capability = details["compute_capability"]
        print(details)
    return self
  # --------------------------------------------------------------------------------------------------------------------
  def __str__(self):
    sResult  = f'{"|"*24}\n'
    sResult += f"|| [{self.name[:16]:^16}] ||\n"
    sResult  = f'{"|"*24}\n'
    sResult += f" |__ CPU: {self.cpu}\n"
    sResult += f" |__ RAM: {self.ram_in_gb}  GB\n"
    sResult += f" |__ NPUs\n"
    for oDevice in self.devices:
      if isinstance(oDevice, NeuralProcessingUnit):
        sResult += f'{" "*5} |__ {oDevice.name} {oDevice.vram_in_gb} GB\n'
      else:
        sResult += f'{" "*5} |__ {oDevice} \n'
    return sResult
  # --------------------------------------------------------------------------------------------------------------------
  def __repr__(self):
    return self.__str__()
  # --------------------------------------------------------------------------------------------------------------------
    
# ======================================================================================================================

