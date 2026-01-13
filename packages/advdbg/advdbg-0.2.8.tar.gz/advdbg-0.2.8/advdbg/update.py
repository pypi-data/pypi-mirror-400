import requests
import importlib.metadata

class Update:
    """Class for AdvDBG to interact with Update"""
    def return_latest():
        """Get latest version of AdvDBG.
        
        Returns:
            Actual version from PyPi."""
        url = 'https://pypi.org/pypi/advdbg/json'
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        return data['info']['version']
        
    def return_installed():
        try:
            return importlib.metadata.version('advdbg')
        except importlib.metadata.PackageNotFoundError:
            return None
            
    def check_for_updates():
        if Update.return_installed() != Update.return_latest():
            return f"Not latest!"
       
        return "Latest"
        
print(Update.check_for_updates())