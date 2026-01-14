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
from time import sleep
from .thread_context import ThreadContext
from .thread_safe_queue import ThreadSafeQueue
from .thread_safe_string_collection import StringCollectionThreadSafe



class ThreadWorker(ThreadContext):
    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, name=None, p_nLoopSleepIntervalMS=100, p_oQueue=None, p_oLog=None, is_daemon_thread=True):
        super(ThreadWorker, self).__init__(name, is_daemon_thread=is_daemon_thread)
        #........................... |  Instance Attributes | ...........................
        self.SleepIntervalMsecs = p_nLoopSleepIntervalMS        
        self.SleepIntervalMsecs
        self.Queue = p_oQueue
        self.Log = None
        #................................................................................        

        # auto create the queue and its log
        if p_oQueue is None:
            self.Queue = ThreadSafeQueue()
        if p_oLog is None:
            self.Log = StringCollectionThreadSafe()
    # ------------------------------------------------------------------------------------------------------------------
    def ThreadMain(self, p_oArgs):
        nSleepInterval = float(self.SleepIntervalMsecs/1000)
        
        while self.must_continue:
            if not self.Queue.is_empty():
                oMessage = self.Queue.pop()
                if oMessage is not None:
                    self.ThreadInvokeMethod(oMessage)
            sleep(nSleepInterval)
    # ------------------------------------------------------------------------------------------------------------------
    def ThreadInvokeMethod(self, p_oMessage): #virtual
        pass
    # ------------------------------------------------------------------------------------------------------------------


