import importlib
import pkgutil
import inspect
from sqlmodel import SQLModel

import models

# Dynamically import all modules in Models folder
for loader, module_name, is_pkg in pkgutil.iter_modules(models.__path__):
    module = importlib.import_module(f"models.{module_name}")

    # Ensure all classes inheriting SQLModel are loaded
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and issubclass(obj, SQLModel):
            globals()[name] = obj
