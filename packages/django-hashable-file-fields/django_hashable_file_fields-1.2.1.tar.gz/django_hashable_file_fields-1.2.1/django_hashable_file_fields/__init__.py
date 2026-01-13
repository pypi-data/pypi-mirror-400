"""Django app providing ``HashableFileFieldsBaseModel``, a base django model to automatically compute
file-fields hashes."""

from importlib.metadata import version

__version__ = version("django-hashable-file-fields")
VERSION = tuple(int(part) for part in __version__.split(".") if str(part).isnumeric())
