import json
import os

from typing import Callable, TypeVar, Any

from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class SBox:
    def __init__(self, filename: str = '.secret.json', interactive: bool = False, auto_save: bool = False):
        '''
        Create new SBox vault.
        
        :param filename: Path to the JSON file where secrets are stored.
        :param interactive: If True, prompt user for missing values via CLI.
        :param auto_save: If True, automatically save the vault after parsing.
        '''
        
        self.filename = filename
        self.interactive = interactive
        self.auto_save = auto_save
        
        self.models = {}
        self.gens = {}
        
        try:
            with open(self.filename) as file:
                self.filedict: dict[dict, Any] = json.load(file)
        except FileNotFoundError:
            self.filedict = {}
    
    def _get_field(self, model: type[BaseModel], field: str):
        m_name = model.__name__
        env_key = f'{m_name}_{field}'.upper()

        env_val = os.getenv(env_key)
        if env_val is not None:
            return env_val
        
        if (model, field) in self.gens:
            return self.gens[(model, field)]()

        if self.interactive:
            try:
                f_type = model.model_fields[field].annotation.__name__
                return input(f'Enter {m_name}.{field} ({f_type}): ')
            except EOFError:
                pass

        raise ValueError(
            f'Field {m_name}.{field} is missing! '
            f'Set it via env var "{env_key}", JSON file or @gen.'
        )
            
    def gen(self, model: type[BaseModel], field_name: str):
        '''
        Register a generator function for a specific model field.
        
        :param model: The Pydantic model class.
        :param field_name: The name of the field to generate values for.
        '''
        
        def deco(func: Callable):
            self.gens[(model, field_name)] = func
            
            return func
        return deco
    
    def parse(self, *models: type[BaseModel]):
        '''
        Load data into models, performing migrations if the schema has changed.
        
        :param models: One or more Pydantic model classes to process.
        :raises ValueError: If a field is missing and cannot be filled.
        '''
        
        for model in models:
            m_name = model.__name__
            if m_name in self.filedict:
                saved_fields = list(self.filedict[m_name].keys())
                model_fields = list(model.model_fields.keys())

                if set(saved_fields) != set(model_fields):       
                    for i in saved_fields:
                        if i not in model_fields:
                            del self.filedict[m_name][i]
                    
                    for i in model_fields:
                        if i not in saved_fields:
                            self.filedict[m_name][i] = self._get_field(model, i)
                
                self.models[m_name] = model(**self.filedict[m_name])
            else:
                filled_model = {}
                for field in model.model_fields:
                    filled_model[field] = self._get_field(model, field)
                
                self.filedict[m_name] = filled_model
                self.models[m_name] = model(**filled_model)
        
        if self.auto_save:
            self.saveall()
    
    def saveall(self):
        '''
        Save all values into vault file
        '''
        
        file_exists = os.path.exists(self.filename)
        with open(self.filename, 'w') as file:
            json.dump(self.filedict, file, indent=4)
        
        if not file_exists and os.name == 'posix':
            os.chmod(self.filename, 0o600)
    
    def __getattr__(self, name: str) -> Any:
        if name in self.models:
            return self.models[name]
        
        raise AttributeError(f'Model {name} not parsed yet!')

    def get_model(self, model: type[T]) -> T:
        '''
        Retrieve a parsed model instance with full type hinting support.
        
        :param model: The Pydantic model class to retrieve.
        :return: An instance of the requested model.
        :raises AttributeError: If the model hasn't been parsed yet.
        '''
        
        name = model.__name__
        
        return self.__getattr__(name)