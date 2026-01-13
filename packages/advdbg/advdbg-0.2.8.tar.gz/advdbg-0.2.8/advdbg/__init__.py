'''
Welcome to Advanced Debug.
Licensed with MIT

Change Logs:
	- Added .about()
	- Added custom exception
	- Added checker for updates
'''

__version__ = '0.2.7'

from .core import AdvDBG

from .analyze import Breakpoint
import requests
from .update import Update

__all__ = ['AdvDBG', 'Breakpoint']
if Update.check_for_updates() == "Not latest!":
                print('Available new update\n{Colors.INFO}{Update.return_installed()} → {Update.return_latest()}')

# For easy access, you can create a default instance
DebuGGer = AdvDBG()