from contextlib import suppress
from importlib import import_module
from types import ModuleType
from typing import Optional


def import_module_otherwise_none(module_to_import: str) -> Optional[ModuleType]:
    with suppress(ImportError):
        return import_module(module_to_import)

    return None
