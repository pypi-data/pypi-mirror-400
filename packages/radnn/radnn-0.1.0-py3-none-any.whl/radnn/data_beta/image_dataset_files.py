from radnn import FileStore
from radnn.utils import camel_case
from radnn.system.files import FileList
from .dataset_folder import DataSetFolder
import sys
from tqdm import tqdm
from datetime import datetime

class ImageDataSetFiles(object):
  # --------------------------------------------------------------------------------------------------------------------
  def __init__(self, images_fs, name="files", is_progress_indicator=True):
    self.images_fs :FileStore = images_fs
    self.name = name
    self.is_progress_indicator = is_progress_indicator
    self.class_names :dict = dict()
    self.class_folders :list = []
    self.files :FileList = dict()
    self.files_ts :FileList = dict()
    self.files_vs :FileList = dict()
    self.files_ut :FileList = dict()
    self.total_file_count = 0
    self.is_split_on_main_folder = False
    self.is_split_in_class_folders = False
    self.run_date_time = None

    self.detect_class_names_from_folders()
  # --------------------------------------------------------------------------------------------------------------------
  def load(self, extensions="*.jpg;  *.png"):
    if not self.load_file_lists():
      self.detect_files(extensions)
  # --------------------------------------------------------------------------------------------------------------------
  def load_file_lists(self):
    bResult = False
    oDict = self.images_fs.obj.load(f"{self.name}-file-info.pkl")
    if oDict is not None:
      self.run_date_time = oDict["RunDateTime"]
      self.class_names = oDict["ClassNames"]
      self.class_folders = oDict["ClassFolders"]
      self.files = oDict["ClassFiles.All"]
      self.files_ts = oDict["ClassFiles.TrainingSet"]
      self.files_vs = oDict["ClassFiles.ValidationSet"]
      self.files_ut = oDict["ClassFiles.UnknownTestSet"]
      self.total_file_count = oDict["TotalFileCount"]
      self.is_split_on_main_folder = oDict["IsSplitOnMainFolder"]
      self.is_split_in_class_folders = oDict["IsSplitInClassFolders"]
      bResult = True

    return bResult
  # --------------------------------------------------------------------------------------------------------------------
  def save_file_lists(self):
    oDict = dict()
    oDict["RunDateTime"] = self.run_date_time
    oDict["ClassNames"] = self.class_names
    oDict["ClassFolders"] = self.class_folders
    oDict["ClassFiles.All"] = self.files
    oDict["ClassFiles.TrainingSet"] = self.files_ts
    oDict["ClassFiles.ValidationSet"] = self.files_vs
    oDict["ClassFiles.UnknownTestSet"] = self.files_ut
    oDict["TotalFileCount"] = self.total_file_count
    oDict["IsSplitOnMainFolder"] = self.is_split_on_main_folder
    oDict["IsSplitInClassFolders"] = self.is_split_in_class_folders
    self.images_fs.obj.save(oDict, f"{self.name}-file-info.pkl")
  # --------------------------------------------------------------------------------------------------------------------
  def detect_class_names_from_folders(self):
    oClassNamesFS = self.images_fs
    oMainFolder = DataSetFolder("/", self.images_fs)
    oFolders = oMainFolder.subfolders

    self.is_split_on_main_folder = oMainFolder.is_split
    if self.is_split_on_main_folder:
      # Detect the class names under the training set subfolder
      oClassNamesFS = oMainFolder.filestore_ts
      oFolders = oClassNamesFS.list_folders(is_full_path=False)

    for nIndex, sFolder in enumerate(oFolders):
      sClassName = camel_case(sFolder)
      self.class_names[nIndex] = sClassName
      oClassFS = oClassNamesFS.subfs(sFolder, must_exist=True)
      oClassFolder = DataSetFolder(sFolder, oClassFS)
      if not self.is_split_on_main_folder:
        if oClassFolder.is_split:
          self.is_split_in_class_folders = True
      self.class_folders.append(oClassFolder)

    return self.class_folders

  # --------------------------------------------------------------------------------------------------------------------
  def traverse_sub_folders(self, extensions, progress):
    for nClassIndex, oClassFolder in enumerate(self.class_folders):
      if progress is not None:
        progress.set_description(f"Finding files for class {self.class_names[nClassIndex]}")
        progress.refresh()
      self.files[nClassIndex] = oClassFolder.filestore.filelist(extensions)
      self.total_file_count += len(self.files[nClassIndex])
      if progress is not None:
        progress.update(1)
  # --------------------------------------------------------------------------------------------------------------------
  def traverse_sub_folders_with_split(self, extensions, progress):
    self.total_file_count = 0
    for nClassIndex, oClassFolder in enumerate(self.class_folders):
      if progress is not None:
        progress.set_description(f"Finding files for class {self.class_names[nClassIndex]}")
        progress.refresh()
      if oClassFolder.is_split:
        oClassAllFiles = FileList()
        for nIndex, oSplitFileStore in enumerate(oClassFolder.split_filestores):
          if oSplitFileStore is not None:
            oFileList = oSplitFileStore.filelist(extensions)
            for oFile in oFileList.full_paths:
              dSplit = None
              if oSplitFileStore == oClassFolder.filestore_ts:
                dSplit = self.files_ts
              elif oSplitFileStore == oClassFolder.filestore_vs:
                dSplit = self.files_vs
              elif oSplitFileStore == oClassFolder.filestore_ut:
                dSplit = self.files_ut

              if dSplit is not None:
                if nClassIndex not in dSplit:
                  dSplit[nClassIndex] = []
                dSplit[nClassIndex].append(oFile)

              oClassAllFiles.append(oFile)
      else:
        raise Exception(f"No split subfolders for class {nIndex} '{self.class_names[nIndex]}',\n"
                        + f"that is stored in {oClassFolder.filestore}\n"
                        + f"All of the classes should have the same split.")
      self.files[nClassIndex] = oClassAllFiles
      self.total_file_count += len(self.files[nClassIndex])
      if progress is not None:
        progress.update(1)


    if progress is not None:
      progress.set_description("Finished")
      progress.refresh()
  # --------------------------------------------------------------------------------------------------------------------
  def detect_files(self, extensions="*.jpg;  *.png"):
    oProgress = None
    if len(self.class_folders) > 0:
      if (not self.is_split_on_main_folder) and (not self.is_split_in_class_folders):
        if self.is_progress_indicator:
          oProgress = tqdm(total=len(self.class_folders), ncols=80)
        try:
          self.traverse_sub_folders(extensions, oProgress)
        finally:
          if self.is_progress_indicator:
            oProgress.close()

      elif (not self.is_split_on_main_folder) and self.is_split_in_class_folders:
        if self.is_progress_indicator:
          oProgress = tqdm(total=len(self.class_folders), ncols=80)
        try:
          self.traverse_sub_folders_with_split(extensions, oProgress)
        finally:
          if self.is_progress_indicator:
            oProgress.close()

      self.save_file_lists()
  # --------------------------------------------------------------------------------------------------------------------















