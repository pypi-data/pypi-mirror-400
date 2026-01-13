from .pycore import *

__doc__ = pycore.__doc__
if hasattr(pycore, "__all__"):
    __all__ = pycore.__all__