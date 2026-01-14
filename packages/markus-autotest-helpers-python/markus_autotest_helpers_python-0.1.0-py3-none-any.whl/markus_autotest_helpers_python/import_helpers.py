import importlib
import pytest
from traceback import format_exception_only
from types import ModuleType


def module_fixture(modname: str):
    """Return a pytest fixture to import the given module."""

    @pytest.fixture(scope="module", name=modname)
    def submission():
        f"""The imported module {modname}"""
        try:
            mod = importlib.import_module(modname)
        except Exception as e:
            msg = f'Could not successfully import {modname}.' \
                  f'\nDetails:\n\n{"".join(format_exception_only(e))}'
            raise AssertionError(msg) from e
        return mod

    submission.__name__ = modname

    return submission


def module_lookup(mod: ModuleType, attr: str, attr_type: str):
    """Wrapper around getattr(mod, attr).

    attr_type is used to format the error message.
    Typically 'class' or 'function'.
    """
    assert hasattr(mod, attr), f'Your {mod.__name__} module did not define a ' \
                               f'{attr} {attr_type}.'
    return getattr(mod, attr)
