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
from .semaphore_lock import SemaphoreLock

    

class ThreadSafeQueue(object):
    #-------------------------------------------------------------------------------------------------------------------
    def __init__(self, name="Queue", max_queued_items=None):
        #........................... |  Instance Attributes | ...........................
        self.name = name
        self.queue=[]
                
        # // Settings \\
        self.max_queued_items = max_queued_items
        self.can_delete              = True
        
        # // Control Params \\
        self.is_queue_locked = False
        
        # // Composites \\
        self.update_lock = SemaphoreLock()
        #................................................................................

    # -------------------------------------------------------------------------------------------------------------------
    @property
    def count(self):
        return len(self.queue)

    # -------------------------------------------------------------------------------------------------------------------
    @property
    def is_empty(self):
        bResult = (len(self.queue) == 0)

        return bResult
    #-------------------------------------------------------------------------------------------------------------------
    def push(self, value):
        self.update_lock.lock()
        try:
            if self.max_queued_items is None:
                bCanAppend = True
            else: 
                bCanAppend = len(self.queue) < self.max_queued_items
            
            if bCanAppend:     
                self.queue.append(value)
        finally:
            self.update_lock.unlock()
    #-------------------------------------------------------------------------------------------------------------------
    def pop(self, index=0):
        nValue = None        
        if self.can_delete:
            self.update_lock.lock()
            try:
                bMustPop = len(self.queue) > 0
                if bMustPop:
                    if index == -1:
                        index = len(self.queue) - 1
                    nValue = self.queue.pop(index)
            finally:
                self.update_lock.unlock()
            
        return nValue
    #-------------------------------------------------------------------------------------------------------------------
    def clear(self):
        self.update_lock.lock()
        try:
            self.queue = []
        finally:
            self.update_lock.unlock()
    #-------------------------------------------------------------------------------------------------------------------
    '''
    def pop_ex(self, index=0):
        nValue,nRemainingItemCount = [None,None]
        if self.can_delete:
            self.update_lock.Lock()
            try:
                nRemainingItemCount = len(self.queue)
                bMustPop = nRemainingItemCount > 0 
                if bMustPop:
                    if index == -1:
                        index = len(self.queue) - 1
                    nValue = self.queue.pop(index)
                    nRemainingItemCount = len(self.queue)
            finally:
                self.update_lock.UnLock()
            
        return nValue, nRemainingItemCount
    '''
    #-------------------------------------------------------------------------------------------------------------------
    def push_ex(self, message):
        while self.is_queue_locked:
            pass
        
        if self.max_queued_items is None:
            bCanAppend = True
        else: 
            bCanAppend = len(self.queue) < self.max_queued_items
            
        if not bCanAppend:
            return  
        
        self.is_queue_locked = True
        try:
            self.queue.append(message)
        finally:
            self.is_queue_locked = False
    #-------------------------------------------------------------------------------------------------------------------
    def pop_ex(self):
        sMessage = None
        if self.can_delete:
            while self.is_queue_locked:
                pass
                
            self.is_queue_locked = True
            try:
                if len(self.queue) > 0:
                    sMessage = self.queue.pop(0)
            finally:
                self.is_queue_locked = False

        return sMessage
    #-------------------------------------------------------------------------------------------------------------------













