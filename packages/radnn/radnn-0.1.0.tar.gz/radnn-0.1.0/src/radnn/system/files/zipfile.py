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
import os
import zipfile
from .fileobject import FileObject

class ZipFile(FileObject):
  # --------------------------------------------------------------------------------------------------------------------
  def __init__(self, filename, parent_folder=None, error_template=None, is_verbose=False):
    super().__init__(filename, parent_folder, error_template)
    self.is_verbose = is_verbose
    self._opened_filename = None
    self._encoding = None
  
  # --------------------------------------------------------------------------------------------------------
  def save(self, source_path, must_replace=True):
    """
    Compress a folder (including subfolders) into a .zip file.

    Args:
        output_zip_path (str): The path where the .zip file will be saved.
    """
    dest_zip_file = os.path.join(self.parent_folder, self.filename)
    if must_replace:
      if os.path.exists(dest_zip_file):
        os.remove(dest_zip_file)
      
      # Create the zip file
      with zipfile.ZipFile(dest_zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_path):
          for file in files:
            abs_path = os.path.join(root, file)
            # Get relative path for proper folder structure inside zip
            rel_path = os.path.relpath(abs_path, start=source_path)
            zipf.write(abs_path, rel_path)
  
  # --------------------------------------------------------------------------------------------------------
  def extract(self, dest_path, has_progress_bar=True, is_verbose=True):
    """
    Extracts a .zip file into the specified folder.

    Args:
        zip_filename (str): Path to the .zip file.
        destination_folder (str): Folder where the contents should be extracted.
    """
    source_zip_file = os.path.join(self.parent_folder, self.filename)
    
    # Ensure the zip file exists
    if not os.path.isfile(source_zip_file):
      raise FileNotFoundError(f"Zip file not found: {source_zip_file}")
    
    # Ensure destination directory exists
    os.makedirs(dest_path, exist_ok=True)
    
    # Extract the zip file
    with zipfile.ZipFile(source_zip_file, 'r') as zip_ref:
      file_list = zip_ref.infolist()
      total_files = len(file_list)
      
      oIterator = file_list
      if is_verbose and has_progress_bar:
        from tqdm import tqdm
        oIterator = tqdm(file_list, total=total_files, desc="Extracting", unit="file")
      
      for file_info in oIterator:
        zip_ref.extract(file_info, dest_path)
    if is_verbose:
      print(f" |_ Extracted '{source_zip_file}' to '{dest_path}'")
  # ----------------------------------------------------------------------------------
