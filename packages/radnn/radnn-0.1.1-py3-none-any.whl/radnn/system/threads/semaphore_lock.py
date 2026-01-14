# ======================================================================================
#
#     Rapid Deep Neural Networks
#
#     Licensed under the MIT License
# ______________________________________________________________________________________
# ......................................................................................

# Copyright (c) 2018-2025 Pantelis I. Kaplanoglou

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
from threading import BoundedSemaphore

#=======================================================================================================================
class SemaphoreLock(BoundedSemaphore):
    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, value=1):
        super(SemaphoreLock, self).__init__(value)
    # ------------------------------------------------------------------------------------------------------------------
    def lock(self, blocking=True, timeout=None):
        self.acquire(blocking, timeout)
    # ------------------------------------------------------------------------------------------------------------------
    def unlock(self):
        self.release()
    # ------------------------------------------------------------------------------------------------------------------
    # //TODO: Not working, check if this can be fixed
    '''
    def __enter__(self):
        self.Lock()
        return self
    
    def __exit__(self, exception_type, exception_val, trace):
        try:
            self.Unlock()
        except:
            print("Could not unlock semaphore")
            return True     
    '''
    # ------------------------------------------------------------------------------------------------------------------
#=======================================================================================================================
