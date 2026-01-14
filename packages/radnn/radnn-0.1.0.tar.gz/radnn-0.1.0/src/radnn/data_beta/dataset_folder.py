from .subset_type import SubsetType

class DataSetFolder(object):
  # --------------------------------------------------------------------------------------------------------------------
  def __init__(self, folder_name, filestore):
    self.folder_name = folder_name
    self.filestore = filestore
    self.filestore_ts = None
    self.filestore_vs = None
    self.filestore_ut = None
    self.split_filestores = []

    self.subfolders = self.filestore.list_folders(is_full_path=False)
    self.is_split, sTSFolder, sVSFolder, sUTFolder = self.get_split_subfolders(self.subfolders)
    if self.is_split:
      if sTSFolder is not None:
        self.filestore_ts = self.filestore.subfs(sTSFolder, must_exist=True)
        self.split_filestores.append(self.filestore_ts)
      if sVSFolder is not None:
        self.filestore_vs = self.filestore.subfs(sVSFolder, must_exist=True)
        self.split_filestores.append(self.filestore_vs)
      if sUTFolder is not None:
        self.filestore_ut = self.filestore.subfs(sUTFolder, must_exist=True)
        self.split_filestores.append(self.filestore_ut)
  # --------------------------------------------------------------------------------------------------------------------
  def get_split_subfolders(self, folders):
    sTSFolder = None
    sVSFolder = None
    sUTFolder = None
    bIsSplit = False
    for sFolder in folders:
      oFolderSubsetType = SubsetType(sFolder)
      if oFolderSubsetType.is_training_set:
        sTSFolder = sFolder
        bIsSplit = True
      elif oFolderSubsetType.is_validation_set:
        sVSFolder = sFolder
        bIsSplit = True
      elif oFolderSubsetType.is_unknown_test_set:
        sUTFolder = sFolder
        bIsSplit = True

    #  When confusing terminology is uses and 'test' means 'validation'
    if (sUTFolder is not None) and (sVSFolder is None):
      sVSFolder = sUTFolder
      sUTFolder = None

    return bIsSplit, sTSFolder, sVSFolder, sUTFolder
  # --------------------------------------------------------------------------------------------------------------------
  def __str__(self):
    return "./" + self.folder_name
  # --------------------------------------------------------------------------------------------------------------------
  def __repr__(self):
    return self.__str__()
  # --------------------------------------------------------------------------------------------------------------------