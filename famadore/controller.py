
import sys as _sys
import os as _os
import time as _time
import inspect as _inspect

def interact():
    caller_frame = _inspect.currentframe(1)
    local_ns = caller_frame.f_locals
    global_ns = caller_frame.f_globals
    import IPython
    from IPython.config.loader import Config
    from IPython.terminal.embed import InteractiveShellEmbed
    cfg = Config()
    cfg.HistoryManager.enabled = False
    cfg.PromptManager.in_template = ">>> "
    cfg.PromptManager.in2_template = "... "
    cfg.PromptManager.out_template = ""
    cfg.TerminalInteractiveShell = cfg.InteractiveShellEmbed
    cfg.TerminalInteractiveShell.cache_size = 0
    cfg.TerminalInteractiveShell.colors = 'Linux'
    shell = InteractiveShellEmbed.instance(
        banner1="Embedded IPython shell...",
        exit_msg="Leaving IPython, resuming program...",
        config=cfg)
    
    class DummyMod(object): pass
    module = DummyMod()
    module.__dict__ = global_ns

    ishell = shell(
            local_ns=local_ns, stack_depth=2, module=module)
    return ishell

import __builtin__
__builtin__.interact = interact

def attach(modules=None, filters=None):
    
    if modules is None:
        modules = [_inspect.getmodule(_inspect.stack()[-2][0])]
    
    controller = Controller(modules=modules)
    
    return controller

def detach():
    _sys.settrace(None)


class Filter(object):

    def __init__(self):
        pass
    
    co_filename_startswith = ()

    @classmethod    
    def matches(cls, co, func_name):
        
        if co.co_filename.startswith(cls.co_filename_startswith):
            return True
        
        return None


class Controller(object):
    
    def __init__(self, modules=None, filters=None):
        
        filters = list(filters or ())
        
        for module in modules:
            for attr in dir(module):
                value = getattr(module, attr)
                if value is Filter:
                    continue
                try:
                    if issubclass(value, Filter):
                        filters.append(value)
                except TypeError:
                    continue
                
        self._filters = sorted(filters, lambda x: getattr(x, 'priority', 0))

        self._famadore_code_path = _os.path.dirname(
            _inspect.getmodule(self).__file__)
        
        self.calls = []
        
        _sys.settrace(self.profiler)

    @staticmethod
    def detach():
        detach()

    _last_call = None
    _last_ccall = None
    _stack_count = 0
    def profiler(self, frame, event, arg):

        stop_time = _time.time()

        if event == 'line':
            return

        co = frame.f_code
        
        if co.co_filename.startswith(self._famadore_code_path):
            return
        
        func_name = co.co_name
        
        for filter in self._filters:
            did_match = filter.matches(co, func_name)
            if did_match is True:
                break
            elif did_match is False:
                return
        else:
            return
                
        if 'call' in event:
            try:
                parent_call = self.calls[self._stack_count - 1]
            except IndexError:
                parent_call = None
            self._stack_count += 1
            call = Call(parent_call, co, func_name)
            self.calls.append(call)
            call.start()
        elif 'return' in event:
            self._stack_count -= 1
            self.calls[self._stack_count].stop(stop_time)
            
        return self.profiler
        

class Call(object):
    
    
    child_call = None
    
    def __init__(self, parent_call, co, func_name):
        self.parent_call = parent_call
        if parent_call:
            parent_call.child_call = self
        self.co = co
        self.func_name = func_name
    
    def start(self):
        self._start_time = _time.time()
        
    def stop(self, stop_time):
        self._stop_time = stop_time
        
    @property
    def walltime(self):
        return self._stop_time - self._start_time

    @property
    def runtime(self):
        if self.child_call:
            return self.walltime - self.child_call.walltime
        else:
            return self.walltime

class CCall(Call):
    pass
        
        
           



