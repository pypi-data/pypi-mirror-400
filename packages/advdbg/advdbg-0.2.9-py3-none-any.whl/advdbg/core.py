'''
Welcome to Advanced Debug.
Core module.
'''

import os
from datetime import datetime
import random
from typing import Dict, Any, Optional, List
import requests

from .update import Update
from .colors import Colors
from .exceptions import OutputListError
# class Colors:
#     WARN = ""
#     ERROR = ""
#     INFO = ""
#     SUCCESS = ""

listPhrases = ['Writting some lines.', "Don't forgot to define!", 'Waiting for your command.']
randomPhrase = random.choice(listPhrases)

class AdvDBG:
    _category_store: Dict[str, Dict[str, Any]] = {}
    _defined_categories: Dict[str, 'AdvDBG'] = {}
    
    def __init__(self, title='Debug', activated=False, notify=False, output: Optional[List[str]] = None, legacy=False):
        if isinstance(title, str) and isinstance(activated, bool) and isinstance(notify, bool):
            self.title = title
            self.activated = False
            self._defed = False
            self.notify = notify
            self.output = output or ['console']
            self.legacy = legacy
        else:
            raise ValueError('Some parameters do not match required types')
            
        # Валидация output
        self._validate_output(self.output)
        
        if title not in self._category_store:
            self._category_store[title] = {}
        if title not in self._defined_categories:
            self._defined_categories[title] = self
    
    def _validate_output(self, output_list: List[str]) -> None:
        """Валидирует список output"""
        if output_list is None:
            return
        
        # Проверка на допустимые значения
        allowed = {'console', 'file'}
        for output_type in output_list:
            if output_type not in allowed:
                print(f"{Colors.ERROR} Error - AdvDBG | Error when reading the output type: Detected disallowed output. Please use console or file.\033[0m")
                raise OutputListError(f"Disallowed output type: {output_type}")
        
        # Проверка на повторяющиеся значения
        if len(output_list) != len(set(output_list)):
            # Находим дубликаты
            seen = set()
            duplicates = set()
            for item in output_list:
                if item in seen:
                    duplicates.add(item)
                else:
                    seen.add(item)
            
            print(f"{Colors.ERROR} Error - AdvDBG | {len(duplicates)} repeating output types were found. Please, delete repeating types and try again.\033[0m")
            raise OutputListError(f"Repeating output types: {', '.join(duplicates)}")
    
    @classmethod
    def define(cls, title: str = 'Debug', activated: bool = True, notify: bool = False, output: Optional[List[str]] = None, legacy: bool = False):
        '''Defines your debug category.
        :param title: Title of your category
        :param activated: Toggle availability of category
        :param notify: Toggles notification if category is not activated
        :param output: Where logger will save lines?
        :param legacy: Use old style?'''
        
        # Валидация перед созданием экземпляра
        output = output or ['console']
        
        # Проверка на допустимые значения
        allowed = {'console', 'file'}
        for output_type in output:
            if output_type not in allowed:
                print(f"{Colors.ERROR} Error - AdvDBG | Error when reading the output type: Detected disallowed output. Please use console or file.\033[0m")
                raise ValueError(f"Disallowed output type: {output_type}")
        
        # Проверка на повторяющиеся значения
        if len(output) != len(set(output)):
            # Находим дубликаты
            seen = set()
            duplicates = set()
            for item in output:
                if item in seen:
                    duplicates.add(item)
                else:
                    seen.add(item)
            
            print(f"{Colors.ERROR} Error - AdvDBG | {len(duplicates)} repeating output types were found. Please, delete repeating types and try again.\033[0m")
            raise ValueError(f"Repeating output types: {', '.join(duplicates)}")
        
        inst = cls(title, activated, notify, output, legacy)
        inst.title = title
        inst.activated = True
        inst.notify = notify
        inst.output = output
        inst.legacy = legacy
        inst._defed = True
        
        cls._category_store[title] = {
            'title': title,
            'activated': activated,
            'notify': notify,
            'output': output,
            'legacy': legacy,
            'created_at': datetime.now()
        }
        cls._defined_categories[title] = inst
        return inst
        
    @classmethod
    def get_category_settings(cls, category: str) -> Optional[Dict[str, Any]]:
        if category in cls._category_store:
            return cls._category_store[category].copy()
        return None
    
    @classmethod
    def get_all_categories(cls) -> List[str]:
        return list(cls._category_store.keys())
        
    @classmethod
    def export_all_data(cls) -> Dict[str, Any]:
        return {
            'categories': cls._category_store.copy(),
            'total_categories': len(cls._category_store),
            'export_timestamp': datetime.now().isoformat(),
            'version': '1.0'
        }
    
    def _write_to_log(self, text, log_type='INFO'):
        '''For-Module only method.'''
        if not 'file' in self.output:
            return
        
        try:
            # Creating logs directory relative to the current working directory
            logs_dir = os.path.join(os.getcwd(), 'logs')
            os.makedirs(logs_dir, exist_ok=True)
            
            current_date = datetime.now().strftime("%d.%m.%Y")
            filename = f"log_{current_date}.txt"
            filepath = os.path.join(logs_dir, filename)
            
            current_time = datetime.now().strftime("%H:%M:%S")
            log_entry = f"{self.title} {current_time} | {text}\n"
            
            file_exists = os.path.exists(filepath)
            
            with open(filepath, 'a', encoding='utf-8') as f:
                if not file_exists:
                    f.write(f"/// Advanced Debugger\n")
                    f.write(f"Category: {self.title}\n")
                    f.write(randomPhrase)
                    f.write("\n\n")
                
                f.write(log_entry)
                
        except Exception as e:
            print(f"\033[33mWARNING\033[0m | Failed to write to log file: {e}")
        
    def info(self, text):
        """Print debug information
        Type: INFO
    
        :param text: Text to show"""
        if not isinstance(text, str):
            try:
                text = str(text)
            except Exception as e:
                text = f"Cannot convert to string format: {e}"
    
        if self.activated:
            if self.legacy and 'console' in self.output:
                print(f'[\033[90mINFO \033[95m{self.title} at {datetime.now().strftime("%D, %H:%M:%S")}\033[0m] {text} \033[0m')
            elif not self.legacy and 'console' in self.output:
                print(f'{Colors.INFO} Info - {self.title} ({datetime.now().strftime("%D, %H:%M:%S")}) | {text}\033[0m')
            if 'file' in self.output:
                self._write_to_log(text, 'INFO')
        elif self.notify:
            print(f'Notification from {self.title}: Tried to output when disactivated.\n\033[93mTip: \033[0mIf you are did not want to saw these notifications, turn off NOTIFY property with using notify=False\033[0m')
        else:
            return
            
    def warn(self, text):
        if not isinstance(text, str):
            try:
                text = str(text)
            except Exception as e:
                text = f"Cannot convert to string format: {e}"
        
        if self.activated:
            if self.legacy and 'console' in self.output:
                print(f'[\033[90mWARN \033[95m{self.title} at {datetime.now().strftime("%D, %H:%M:%S")}\033[0m] {text} \033[0m')
            elif not self.legacy and 'console' in self.output:
                print(f'{Colors.WARN} Warn - {self.title} ({datetime.now().strftime("%D, %H:%M:%S")}) | {text}\033[0m')
            if 'file' in self.output:
                self._write_to_log(text, 'WARN')
        elif self.notify:
            print(f'Notification from {self.title}: Tried to output when disactivated.\n\033[93mTip: \033[0mIf you are did not want to saw these notifications, turn off NOTIFY property with using notify=False')
        else:
            return
            
    def success(self, text):
        if not isinstance(text, str):
            try:
                text = str(text)
            except Exception as e:
                text = f"Cannot convert to string format: {e}"
        
        if self.activated:
            if self.legacy and 'console' in self.output:
                print(f'[\033[90mSUCCESS \033[95m{self.title} at {datetime.now().strftime("%D, %H:%M:%S")}\033[0m] {text} \033[0m')
            elif not self.legacy and 'console' in self.output:
                print(f'{Colors.SUCCESS} Success - {self.title} ({datetime.now().strftime("%D, %H:%M:%S")}) | {text}\033[0m')
            if 'file' in self.output:
                self._write_to_log(text, 'SUCCESS')
        elif self.notify:
            print(f'Notification from {self.title}: Tried to output when disactivated.\n\033[93mTip: \033[0mIf you are did not want to saw these notifications, turn off NOTIFY property with using notify=False')
        else:
            return
            
    def error(self, text):
        if not isinstance(text, str):
            try:
                text = str(text)
            except Exception as e:
                text = f"Cannot convert to string format: {e}"
                    
        if self.activated:
            if self.legacy:
                print(f'[\033[33mERROR \033[95m{self.title} at {datetime.now().strftime("%D, %H:%M:%S")}\033[0m] {text} \033[0m')
            elif not self.legacy:
                print(f'{Colors.ERROR} Error - {self.title} ({datetime.now().strftime("%D, %H:%M:%S")}) | {text}\033[0m')
            if 'file' in self.output:
                self._write_to_log(text, 'ERROR')
        elif self.notify:
            print(f'Notification from {self.title}: Tried to output when disactivated.\n\033[93mTip: \033[0mIf you are did not want to saw these notifications, turn off NOTIFY property with using notify=False')
        else:
            return
    
    def notification(self, text):
        """This type is deprecated."""
        print('Type "Notification" is deprecated. Please, change it to another.')
    
    def cfg(self, activated=None, title: str = 'Debug', notify: bool = True, output: Optional[List[str]] = None):
        '''Configure existing category'''
        output = output or ['console']
        
        # Валидация нового output
        self._validate_output(output)
        
        if activated is not None:
            self.activated = activated
            if self.activated is False:
                self.notify = notify
        elif title is not None:
            self.title = title
        elif output is not None:
            self.output = output
            
        if self.title in self._category_store:
            self._category_store[self.title]['activated'] = self.activated
            self._category_store[self.title]["title"] = self.title
            self._category_store[self.title]["output"] = self.output
        
        return self
        
    def about():
            print(f'Advanced Debugger\nfrom Darkey Labs\n\nVersion v{Update.return_installed()}\nLicensed with MIT')
           
            
    def __call__(self, text):
        if not isinstance(text, str):
            try:
                text = str(text)
            except Exception as e:
                text = f"Cannot convert to string format: {e}"
        self.info(text)