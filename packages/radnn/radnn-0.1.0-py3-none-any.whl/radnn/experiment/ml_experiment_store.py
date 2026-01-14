from radnn import FileStore
class MLExperimentStore(FileStore):
  def __init__(self, base_folder, is_verbose=False, must_exist=False):
    super(MLExperimentStore, self).__init__(base_folder, is_verbose, must_exist)

    self.param_fs = self.subfs("weights")
    self.log_fs = self.subfs("logs")
    self.checkpoint_fs = self.subfs("checkpoints")
    self.state_fs = self.subfs("state")
