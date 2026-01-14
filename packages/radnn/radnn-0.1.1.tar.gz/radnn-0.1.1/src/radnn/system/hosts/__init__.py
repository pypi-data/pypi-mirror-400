from radnn.core import MLInfrastructure

if MLInfrastructure.is_windows():
  from .windows_host import WindowsHost

if MLInfrastructure.is_colab():
  from .colab_host import ColabHost

if MLInfrastructure.is_linux():
  from .linux_host import LinuxHost