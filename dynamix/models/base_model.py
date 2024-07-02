"""
This file contains the base class for all models.
"""
from typing import Optional
from abc import ABC, abstractmethod

class BaseModel:
    @abstractmethod
    def __init__(self):
        ''' Model initialization. '''
        pass

    @abstractmethod
    def generate(self, text_prompt:str, folder_path:Optional[str]=None, filename:Optional[str]=None):
        '''  Generates an image from a given text_prompt. 
        
        @returns the URL of the generated image or save_path if download is True
        
        '''
        pass