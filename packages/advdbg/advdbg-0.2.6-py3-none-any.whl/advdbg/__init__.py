'''
Welcome to Advanced Debug.
Licensed with MIT

Change Logs:
	- Hotfix 0.2.3
'''

__version__ = '0.2.4'

from .core import AdvDBG

from .analyze import Breakpoint
import requests

__all__ = ['AdvDBG', 'Breakpoint']

# For easy access, you can create a default instance
DebuGGer = AdvDBG()