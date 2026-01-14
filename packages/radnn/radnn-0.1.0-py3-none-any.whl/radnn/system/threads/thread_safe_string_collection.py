from .thread_safe_queue import ThreadSafeQueue

class StringCollectionThreadSafe(ThreadSafeQueue):
  # -------------------------------------------------------------------------------------------------------------------
  def __init__(self, filename=None, name="Text"):
    super(StringCollectionThreadSafe, self).__init__(name)

    self.filename = filename
    self.__count  = 0
    self.__index  = 0
  # -------------------------------------------------------------------------------------------------------------------
  def append(self, text):
    self.push(text)
  # -------------------------------------------------------------------------------------------------------------------
  def print(self, text, *args):
    if args is None:
      self.push(text)
    else:
      self.push(text + " " + " ".join(map(str, args)))
  # -------------------------------------------------------------------------------------------------------------------
  def flush(self):
    if self.CanDelete:
      with open(self.filename, "a") as oFile:
        for sLine in self.queue:
          print(sLine, file=oFile)
      self.clear()
  # -------------------------------------------------------------------------------------------------------------------
  def display_and_flush(self):
    if self.CanDelete:
      if self.filename is None:
        for sLine in self.queue:
          print(sLine)
      else:
        with open(self.filename, "a") as oFile:
          for sLine in self.queue:
            print(sLine, file=oFile)
      self.clear()
  # -------------------------------------------------------------------------------------------------------------------
  def __iter__(self):
    self.update_lock.Lock()
    try:
      self.__index  = 0
      self.__count = len(self.queue)
      self.CanDelete = False
    finally:
      self.update_lock.UnLock()

    return self
  # -------------------------------------------------------------------------------------------------------------------
  def __next__(self):
    if self.__index < self.__count:
      oResult = self.queue[self.__index]
      self.__index += 1
      return oResult
    else:
      self.CanDelete = True
      raise StopIteration()
  # -------------------------------------------------------------------------------------------------------------------








