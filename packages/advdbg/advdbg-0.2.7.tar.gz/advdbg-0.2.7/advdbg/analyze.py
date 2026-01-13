import threading
import time
from datetime import datetime

class Breakpoint:
    def __init__(self, delay: int | float = 30):
        self.timeout = delay
        self.exclude_self = True
        
    def stop(self, local_vars=None, global_vars=None):
        print('\n      Breakpoint - Advanced Debugger\n')
        
        filtered_locals = self._filter_variables(local_vars) if local_vars else {}
        filtered_globals = self._filter_variables(global_vars) if global_vars else {}
        
        if filtered_locals:
            print('Local variables:\n\n')
            for name, value in filtered_locals.items():
                if not name.startswith('__'):
                    print(f"   {name}       {repr(value)}")
            print('\n')
                    
        if filtered_globals:
            print('Global variables:\n\n')
            for name, value in filtered_globals.items():
                if not name.startswith('__'):
                    print(f"   {name}       {repr(value)}")
                    
        print(f'\n\nCode will continued in {self.timeout} seconds...')
        time.sleep(self.timeout)
        
    def _filter_variables(self, variables):
	       filtered = {}
	       for name, value in variables.items():
	       	if name.startswith('__'):
	       		continue
	       		
	       	if self.exclude_self and isinstance(value, Breakpoint):
	       		continue
	       		
	       	if callable(value) and not isinstance(value, type):
	       		continue
	       		
	       	filtered[name] = value
	       return filtered