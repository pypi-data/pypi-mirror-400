"""
``django_fields_iterator`` provides the ``FieldsIterator`` class that allow to iterate on some or
all of the fields of a model.
"""

from importlib.metadata import version as get_version

# Provide access to classes directly from the package root
from .iterator import FieldsIterator as FieldsIterator
from .types import FieldTypes as FieldTypes

__version__ = get_version("django-fields-iterator")
VERSION = tuple(int(part) for part in __version__.split(".") if str(part).isnumeric())
