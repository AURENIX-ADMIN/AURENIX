import importlib
import inspect
import pkgutil
from typing import List, Callable
from temporalio import activity

def discover_activities(package_name: str) -> List[Callable]:
    """
    Dynamically discovers all @activity.defn decorated functions in a package.
    """
    activities = []
    package = importlib.import_module(package_name)
    
    for loader, module_name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        module = importlib.import_module(module_name)
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj) and hasattr(obj, "__temporal_activity_definition"):
                activities.append(obj)
                
    return activities
