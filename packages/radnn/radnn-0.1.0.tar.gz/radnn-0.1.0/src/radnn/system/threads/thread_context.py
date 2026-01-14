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
import time
from threading import Thread, Event, get_ident
from datetime import datetime


#=======================================================================================================================
class ThreadEx(Thread):
    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self,target=None, name=None, args=(), kwargs=None):
        #//TODO: delegate target, args and kwargs properly
        super(ThreadEx, self).__init__(target=target, name=name, args=args, kwargs=kwargs)
        self._stop_event = Event()
    # ------------------------------------------------------------------------------------------------------------------
    def stop(self):
        self._stop_event.set()
    # ------------------------------------------------------------------------------------------------------------------
    @property
    def is_stopped(self):
        return self._stop_event.is_set()
    # ------------------------------------------------------------------------------------------------------------------
#=======================================================================================================================
    
    
    
    



    
    
#=======================================================================================================================
class ThreadContext(object):
    __NEXT_ID = 0

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, name=None, is_daemon_thread=True, verbose_level=1):
        #........................... |  Instance Attributes | ...........................
        type(self).__NEXT_ID += 1
        if name is None:
            self.name = str(type(self).__NEXT_ID)
        else:
            self.name           = f"{name}{str(type(self).__NEXT_ID)}"
        self.thread_id      = None
        self.verbose_level = verbose_level

        #// Settings \\
        self.is_daemon_thread     = is_daemon_thread
        self.join_timeout        = 5 #secs
        
        # // Control Variables \\ 
        self.must_continue       = False
        self.has_finished  = False
        self.has_started   = False

        # // Agregated Objects \\
        self.thread_handle       = None
        self.thread_args         = None
        self.on_after_finish_handler = None
        self.run_once_func  = None
        #................................................................................
    # ------------------------------------------------------------------------------------------------------------------
    def sleep(self, interval_in_msecs):
        time.sleep(interval_in_msecs / 1000.0)
    # ------------------------------------------------------------------------------------------------------------------
    def _thread_start(self, args):
        self.thread_id   = get_ident()
        self.thread_args = args
        self.has_started = True

        if self.verbose_level > 0:
            print(f"{self} is starting with arguments:", args)

        self.has_finished = False
        try:
            if self.run_once_func is None:
                self.loop()
            else:            
                self.run_once_func(args)
        finally:
            self.has_finished = True
    # ------------------------------------------------------------------------------------------------------------------
    def _thread_finish(self):
        while not self.has_finished:
            pass

        # Callback after finishing
        if self.on_after_finish_handler is not None:
            self.on_after_finish_handler()

        # Signal the thread to stop via the event
        self.thread_handle.stop()

        # Wait for the thread to finish
        if self.verbose_level > 1:
            print(f"{self} joining...")

        self.thread_handle.join(self.join_timeout)

        if self.verbose_level > 1:
            nTimeDelta = datetime.now() - self._stop_action_start
            print(f"{self} joined after {(nTimeDelta.microseconds / 1000):.3f} msecs")
    # ------------------------------------------------------------------------------------------------------------------
    def start(self, args=None):
        self.must_continue = True

        self.thread_handle = ThreadEx(target=self._thread_start, args=(), kwargs={"args": args})
        self.thread_handle.setDaemon(True)
        self.thread_handle.start()
    # ------------------------------------------------------------------------------------------------------------------
    def resume(self, args=None):
        if not self.has_started:
            self.start(args)
    # ------------------------------------------------------------------------------------------------------------------
    def stop(self):
        self._stop_action_start = datetime.now()
        if self.verbose_level > 0:
            print(f"{self} is stopping ...")
        # Break the loop and wait for the method to exit
        self.must_continue = False
        self._thread_finish()
    # ------------------------------------------------------------------------------------------------------------------
    def terminate(self):
        self.stop()
    # ------------------------------------------------------------------------------------------------------------------
    def loop(self):
        pass
    # ------------------------------------------------------------------------------------------------------------------
    def __str__(self):
        return f"{self.name} ({self.thread_id})"
    # ------------------------------------------------------------------------------------------------------------------
    def __repr__(self):
        return self.__str__()
    # ------------------------------------------------------------------------------------------------------------------
#=======================================================================================================================












