from radnn.core import RequiredLibs
oReqs = RequiredLibs()
if oReqs.is_tensorflow_installed:
  import tensorflow.keras as ker

from radnn.learn.keras.keras_learning_rate_scheduler import KLearningRateScheduler

class KOptimizationCombo(object):
  # -----------------------------------------------------------------------------------
  def __init__(self, config, is_verbose=True):
    self.config = config
    self.optimizer = None
    self.callbacks = []
    self.is_verbose = is_verbose

    self.optimizer_name = self.config["Training.Optimizer"].upper()
    if self.optimizer_name == "SGD":
      self.optimizer = ker.optimizers.SGD(learning_rate=self.config["Training.LearningRate"],
                                          momentum=self.config["Training.Momentum"])
      if "Training.LearningRateSchedule" in self.config:
        oLearningRateSchedule = KLearningRateScheduler(self.config)
      self.callbacks.append(oLearningRateSchedule)
    elif self.optimizer_name == "ADAM":
      self.optimizer = ker.optimizers.Adam(learning_rate=self.config["Training.LearningRate"])
    elif self.optimizer_name == "RMSPROP":
      # //TODO: Rho
      if "Training.Momentum" in self.config:
        self.optimizer = ker.optimizers.RMSprop(learning_rate=self.config["Training.LearningRate"],
                                                momentum=self.config["Training.Momentum"])
      else:
        self.optimizer = ker.optimizers.RMSprop(learning_rate=self.config["Training.LearningRate"])

    assert self.optimizer is not None, f'Unsupported optimizer {self.config["Training.Optimizer"]}'
    if self.is_verbose:
      print(f"Learning algorithm {self.optimizer_name}")
  # -----------------------------------------------------------------------------------