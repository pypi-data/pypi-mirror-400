import importlib
import inspect
import json
import pkgutil
from dataclasses import is_dataclass
from enum import IntEnum

from py_mdr.ocsf_models.events.base_event import BaseEvent
from py_mdr.ocsf_models.objects.base_model import BaseModel
from py_mdr.ocsf_models.objects.metadata import Metadata


def get_all_classes(module):  # pragma: no cover
    classes = []
    modules = [module]

    # Recursively find all submodules
    package_name = module.__name__
    for loader, name, is_pkg in pkgutil.walk_packages(module.__path__, package_name + '.'):
        modules.append(importlib.import_module(name))

    # Find all classes defined in the modules
    for mod in modules:
        for name, obj in inspect.getmembers(mod):
            if inspect.isclass(obj) and obj.__module__.startswith(package_name):
                classes.append(obj)

    return classes


def is_json_serializable(obj):  # pragma: no cover
    try:
        json.dumps(obj)
        return True
    except TypeError:
        return False


def test_classes():
    """
    This tests the following for each of the classes that define the OCSF models:
    * Every class should either be a subclass of BaseModel or IntEnum.
    * For subclasses of BaseModel:
        * They should contain a method called `as_dict`
        * `as_dict` should return a JSON serializable dictionary
    * Events should be a subclass of EventBase (not enforced)
        * All subclasses of EventBase should have an attribute called Metadata that is an instance of objects.metadata.Metadata


    :return:
    """
    module = importlib.import_module("py_mdr.ocsf_models")
    all_classes = get_all_classes(module)

    for cls in all_classes:
        assert issubclass(cls, (BaseModel, IntEnum)), f"{cls.__name__} is not a subclass of BaseModel or IntEnum"
        if issubclass(cls, BaseModel):
            assert is_dataclass(cls)
            instance = cls()  # Assumes a no-argument constructor or customize as needed
            assert hasattr(instance, 'as_dict'), f"{cls.__name__} does not have a `to_dict` method"
            assert is_json_serializable(
                instance.as_dict(
                    False)), f"{cls.__name__} `to_dict` method does not return a JSON serializable dictionary"

        if issubclass(cls, BaseEvent) and cls is not BaseEvent:
            instance = cls()
            assert hasattr(instance, 'metadata'), f"{cls.__name__} does not have a Metadata attribute"
            metadata = getattr(instance, 'metadata')
            assert isinstance(metadata,
                              Metadata), f"{cls.__name__} has a Metadata attribute that is not a subclass of objects.Metadata"
