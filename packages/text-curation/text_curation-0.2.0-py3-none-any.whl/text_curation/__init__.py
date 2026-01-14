from importlib.metadata import version

from .curator import TextCurator

__version__ = version("text_curation")

__all__ = ["TextCurator", "__version__ "]