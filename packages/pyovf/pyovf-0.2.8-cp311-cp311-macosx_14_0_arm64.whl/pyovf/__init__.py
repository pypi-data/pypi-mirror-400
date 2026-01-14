# (c) 2021-2026 Prof. Flavio ABREU ARAUJO. All rights reserved.

try:
    from ._version import __version__
except ImportError:
    # Fallback for when package is not installed
    __version__ = "0.0.0.dev0"

__author__ = 'Flavio ABREU ARAUJO'
__email__ = 'flavio.abreuaraujo@uclouvain.be'

from .helper_funcs import *
from .ovf_handler import (
    OVFFile,
    read,
    write,
    read_data_only,
    create,
    has_cpp_extension,
    file_exists,
)

__all__ = [
    'OVFFile',
    'read',
    'write',
    'read_data_only',
    'create',
    'has_cpp_extension',
    'file_exists',
]
