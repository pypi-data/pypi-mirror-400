from radnn.core import RequiredLibs
oReqs = RequiredLibs()
if oReqs.is_tensorflow_installed:
  import tensorflow.keras as ker

class KLearningRateScheduler(ker.callbacks.LearningRateScheduler):
  # -----------------------------------------------------------------------------------
  def __init__(self, config, is_verbose=True):
    self.config = None
    self.lr_schedule = None
    self.is_verbose = is_verbose

    if isinstance(config, dict):
      self.config = config
      self.lr_schedule = config["Training.LearningRateSchedule"]
    elif isinstance(config, list):
      self.lr_schedule = config

    super(KLearningRateScheduler, self).__init__(self.check_schedule)
  # -----------------------------------------------------------------------------------
  def check_schedule(self, epoch, lr):
    nNewLR = lr

    for nIndex, oSchedule in enumerate(self.lr_schedule):
      if epoch == oSchedule[0]:
        nNewLR = oSchedule[1]
        if self.is_verbose:
          print("Schedule #%d: Setting LR to %.5f" % (nIndex + 1, nNewLR))
        break

    if self.is_verbose:
      print("LR: %.6f" % nNewLR)
    return nNewLR
  # -----------------------------------------------------------------------------------