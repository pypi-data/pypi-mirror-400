# (c) 2024-26 by Prof. Flavio ARAUJO. All rights reserved.

import os
import sys
import numpy as np
from .helper_funcs import size_hrf

# Load C++ extension
def _get_ovf_file_py():
    """Load and return the C++ extension module (_ovf_core pybind11 binding)"""
    import importlib.util
    from pathlib import Path
    
    # Try normal import first (for installed packages)
    try:
        from . import _ovf_core
        return _ovf_core
    except ImportError:
        pass
    
    # Fallback: try to load from file for development builds
    try:
        root = Path(__file__).parent
        so_files = list(root.glob("_ovf_core*.so"))
        if so_files:
            spec = importlib.util.spec_from_file_location("_ovf_core", str(so_files[0]))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    except Exception:
        pass
    
    # No extension found
    raise ImportError(
        f"PyOVF C++ extension (_ovf_core) not found for Python {sys.version_info.major}.{sys.version_info.minor}. "
        "Ensure the package is properly built: pip install -e . or pip install pyovf"
    )

# Load on first import
OVF_File_py = _get_ovf_file_py()


class OVFFile:
    """
    High-level wrapper for OVF file handling.
    
    Provides a Pythonic interface to the low-level C++ OVF_File binding.
    Supports creation, reading, and writing of OVF (OOMMF Vector Field) files.
    """
    
    def __init__(self, data=None, title="m", xstepsize=1e-9, ystepsize=1e-9, zstepsize=1e-9):
        """
        Initialize OVFFile.
        
        Parameters
        ----------
        data : ndarray, optional
            3D or 4D numpy array (Z, Y, X) or (Z, Y, X, valuedim)
        title : str
            Title of the OVF file
        xstepsize : float
            X grid spacing in meters
        ystepsize : float
            Y grid spacing in meters
        zstepsize : float
            Z grid spacing in meters
        """
        self._raw = OVF_File_py.OVFFile()  # pybind11 binding class
        self._data = None
        self._original_shape = None  # Track original shape for roundtrip
        self.Title = title
        self.meshunit = "m"
        self.xstepsize = xstepsize
        self.ystepsize = ystepsize
        self.zstepsize = zstepsize
        self.TotalSimTime = 0
        self.TotalSimTimeUnit = "s"
        
        if data is not None:
            self._set_data(data)
    
    def _set_data(self, data):
        """Set data from numpy array."""
        if data.dtype != np.float32:
            data = data.astype(np.float32)
        
        # Store original shape for roundtrip
        self._original_shape = data.shape
        data_copy = np.copy(data)
        
        # Ensure 4D shape (Z, Y, X, valuedim) for internal storage
        if len(data.shape) == 2:
            data_copy = data_copy.reshape(data.shape[0], data.shape[1], 1, 1)
        elif len(data.shape) == 3:
            data_copy = data_copy.reshape(data.shape[0], data.shape[1], data.shape[2], 1)
        elif len(data.shape) == 4:
            pass
        else:
            raise ValueError(f"Data must be 2D, 3D, or 4D, got shape {data.shape}")
        
        self._data = data_copy
    
    @property
    def data(self):
        """Get the data array in original shape."""
        if self._data is None:
            return None
        # Return data in the original shape if available
        if self._original_shape is not None:
            return self._data.reshape(self._original_shape)
        return self._data
    
    @data.setter
    def data(self, value):
        """Set data from numpy array."""
        self._set_data(value)
    
    @property
    def znodes(self):
        """Number of nodes in Z direction."""
        return self._data.shape[0] if self._data is not None else 0
    
    @property
    def ynodes(self):
        """Number of nodes in Y direction."""
        return self._data.shape[1] if self._data is not None else 0
    
    @property
    def xnodes(self):
        """Number of nodes in X direction."""
        return self._data.shape[2] if self._data is not None else 0
    
    @property
    def valuedim(self):
        """Dimension of each value (1 for scalar, 3 for vector)."""
        if self._data is None:
            return 0
        return self._data.shape[3] if len(self._data.shape) == 4 else 1
    
    def _sync_to_raw(self):
        """Sync Python attributes to the C++ raw object."""
        if self._data is not None:
            # Convert data if needed
            data = self._data
            if data.dtype != np.float32:
                data = data.astype(np.float32)
            
            self._raw.Title = self.Title
            self._raw.meshtype = "rectangular"
            self._raw.meshunit = "m"
            self._raw.xstepsize = self.xstepsize
            self._raw.ystepsize = self.ystepsize
            self._raw.zstepsize = self.zstepsize
            self._raw.data = data
    
    def write(self, filename):
        """Write OVF file to disk."""
        self._sync_to_raw()
        self._raw.write(filename)
    
    def read(self, filename):
        """Read OVF file from disk."""
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"File not found: {filename}")
        
        self._raw.read(filename)
        self._data = np.copy(self._raw.data)
        self.Title = self._raw.Title
        self.xstepsize = self._raw.xstepsize
        self.ystepsize = self._raw.ystepsize
        self.zstepsize = self._raw.zstepsize


def has_cpp_extension():
    """Check if C++ extension is available."""
    return True  # C++ extension is available if import succeeded


def file_exists(filename):
    """Check if a file exists."""
    return os.path.isfile(filename)


def create(data, title="m", xstepsize=1e-9, ystepsize=1e-9, zstepsize=1e-9):
    """
    Create an OVFFile from data.
    
    Parameters
    ----------
    data : ndarray
        3D or 4D numpy array
    title : str
        Title of the OVF file
    xstepsize : float
        X grid spacing
    ystepsize : float
        Y grid spacing
    zstepsize : float
        Z grid spacing
        
    Returns
    -------
    OVFFile
        OVF file object
    """
    return OVFFile(data=data, title=title, xstepsize=xstepsize, 
                   ystepsize=ystepsize, zstepsize=zstepsize)


# #* Initialise the wraper object (Cython -> C++ connector)
# #* "obj" is a direct link to the C++ object (be careful)
# OVF_raw = OVF_File_py.OVF_File_py()


#* High level OVF read function (flexible - returns OVFFile or tuple)
def read(filename, return_mesh=False):
    """
    Read OVF file.
    
    Parameters
    ----------
    filename : str
        Path to OVF file
    return_mesh : bool
        If True, returns (X, Y, data) for backward compatibility
        If False, returns OVFFile object (default)
        
    Returns
    -------
    OVFFile or tuple
        OVFFile object or (X, Y, data) tuple if return_mesh=True
    """
    if not os.path.isfile(filename):
        raise FileNotFoundError(f"File not found: {filename}")
    
    OVF_raw = OVF_File_py.OVFFile()  # pybind11 binding class
    OVF_raw.read(filename)
    
    human_readable_size = size_hrf(OVF_raw.data.nbytes)
    print(f'OVF [{OVF_raw.Title} data] # of elements: '
        f'{OVF_raw.elementNum} (size: {human_readable_size})')
    
    # Create OVFFile object
    ovf = OVFFile()
    ovf._raw = OVF_raw
    raw_data = np.copy(OVF_raw.data)
    
    # Determine the original shape based on dimensionality
    # If valuedim == 1 and xnodes == 1, original was 3D (Z, Y, X)
    # Otherwise keep as 4D
    znodes, ynodes, xnodes = raw_data.shape[0], raw_data.shape[1], raw_data.shape[2]
    valuedim = raw_data.shape[3] if len(raw_data.shape) == 4 else 1
    
    ovf._data = raw_data
    # Store original shape for later retrieval
    if valuedim == 1:
        if xnodes == 1:
            # Was 3D: (Z, Y, X)
            ovf._original_shape = (znodes, ynodes, xnodes)
        else:
            # Was likely 3D (Z, Y, X, 1) but with X > 1
            # Keep 3D shape
            ovf._original_shape = (znodes, ynodes, xnodes)
    else:
        # Was 4D
        ovf._original_shape = (znodes, ynodes, xnodes, valuedim)
    
    ovf.Title = OVF_raw.Title
    ovf.xstepsize = OVF_raw.xstepsize
    ovf.ystepsize = OVF_raw.ystepsize
    ovf.zstepsize = OVF_raw.zstepsize
    
    if return_mesh:
        # Backward compatibility: return (X, Y, data)
        data = ovf._data
        X_shift = ovf.xstepsize * ovf.xnodes / 2
        Y_shift = ovf.ystepsize * ovf.ynodes / 2
        X_lin = np.arange(OVF_raw.xbase,
                            ovf.xstepsize * ovf.xnodes,
                            ovf.xstepsize) - X_shift
        Y_lin = np.arange(OVF_raw.ybase,
                            ovf.ystepsize * ovf.ynodes,
                            ovf.ystepsize) - Y_shift
        X, Y = np.meshgrid(X_lin, Y_lin)
        return X, Y, data
    else:
        return ovf


#* High level OVF read function (only data, safe)
def read_data_only(filename):
    if os.path.isfile(filename):
        OVF_raw = OVF_File_py.OVFFile()  # pybind11 binding class
        OVF_raw.read(filename)
        human_readable_size = size_hrf(OVF_raw.data.nbytes)
        print(f'OVF [{OVF_raw.Title} data] # of elements: '
            f'{OVF_raw.elementNum} (size: {human_readable_size})')
        data = np.copy(OVF_raw.data)
        return data.squeeze()
    else:
        raise ValueError(filename + " does not exist!")


#* High level OVF write function (flexible)
def write(filename, data, title="m", Xlim=[0,1], Ylim=[0,1], Zlim=[0,1]):
    """
    Write OVF file.
    
    Parameters
    ----------
    filename : str
        Path where OVF file will be written
    data : OVFFile or ndarray
        OVFFile object or numpy array to write
    title : str
        Title (only used if data is ndarray)
    Xlim : list
        X limits (only used if data is ndarray)
    Ylim : list
        Y limits (only used if data is ndarray)
    Zlim : list
        Z limits (only used if data is ndarray)
    """
    if isinstance(data, OVFFile):
        # Write from OVFFile object
        data.write(filename)
    else:
        # Write from raw numpy array (backward compatibility)
        if (np.prod(data.shape) > 120e6):
            file_size_limit_hr = size_hrf(120e6*4)
            file_size_hr = size_hrf(np.prod(data.shape)*4)
            raise ValueError(f'Creating a file larger than {file_size_limit_hr} ' \
                f'is not supported (your request: {file_size_hr}).')
        
        if (len(data.shape) > 1) and (len(data.shape) <= 4):
            if len(data.shape) == 2:
                data = data.reshape(tuple(list(data.shape) + [1, 1]))
            elif len(data.shape) == 3:
                data = data.reshape(tuple(list(data.shape) + [1]))
        else:
            raise ValueError("Dimension not supported, it must be 2, 3, or 4!")
        
        OVF_raw = OVF_File_py.OVFFile()  # pybind11 binding class
        
        # Convert data if needed
        if data.dtype != np.float32:
            data = data.astype(np.float32)
        
        # Set OVFFile properties
        OVF_raw.Title = title
        OVF_raw.meshtype = "rectangular"
        OVF_raw.meshunit = "m"
        
        # Calculate step sizes from limits
        znodes, ynodes, xnodes = data.shape[:3]
        xstepsize = (Xlim[1] - Xlim[0]) / xnodes if xnodes > 0 else 1.0
        ystepsize = (Ylim[1] - Ylim[0]) / ynodes if ynodes > 0 else 1.0
        zstepsize = (Zlim[1] - Zlim[0]) / znodes if znodes > 0 else 1.0
        
        OVF_raw.xstepsize = xstepsize
        OVF_raw.ystepsize = ystepsize
        OVF_raw.zstepsize = zstepsize
        
        OVF_raw.xmin = Xlim[0]
        OVF_raw.xmax = Xlim[1]
        OVF_raw.ymin = Ylim[0]
        OVF_raw.ymax = Ylim[1]
        OVF_raw.zmin = Zlim[0]
        OVF_raw.zmax = Zlim[1]
        
        # Set data
        OVF_raw.data = data
        
        # Write file
        OVF_raw.write(filename)

