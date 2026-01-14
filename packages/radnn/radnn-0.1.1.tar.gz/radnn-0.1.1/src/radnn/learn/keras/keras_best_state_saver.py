import os

from radnn.core import RequiredLibs
oReqs = RequiredLibs()
if oReqs.is_tensorflow_installed:
  import tensorflow.keras as ker

class KBestStateSaver(object):
  # -----------------------------------------------------------------------------------
  def __init__(self, experiment_fs, metric, verbose=2):
    self.experiment_fs = experiment_fs
    self.metric = metric
    self.checkpoint_fs = self.experiment_fs.subfs("checkpoints")

    sCheckPointPathTemplate = os.path.join(self.checkpoint_fs.base_folder, "{epoch}")

    self.Callback = ker.callbacks.ModelCheckpoint(  filepath=sCheckPointPathTemplate,
                                                    verbose=verbose, save_weights_only=True,
                                                    monitor="val_" + self.metric,
                                                    mode="max", save_best_only=True)
  # -----------------------------------------------------------------------------------