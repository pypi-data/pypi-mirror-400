"""
pyovf - Python library for reading and writing OVF files

OVF (OOMMF Vector Field) is a file format used by micromagnetic simulation
software like OOMMF and mumax3 to store spatially discretized vector and
scalar fields.

Example usage:
    >>> import pyovf
    >>> 
    >>> # Read an OVF file
    >>> ovf = pyovf.read("magnetization.ovf")
    >>> print(ovf.data.shape)  # (nz, ny, nx, 3) for vector field
    >>> 
    >>> # Access metadata
    >>> print(f"Grid: {ovf.xnodes}x{ovf.ynodes}x{ovf.znodes}")
    >>> print(f"Time: {ovf.TotalSimTime} {ovf.TotalSimTimeUnit}")
    >>> 
    >>> # Modify and save
    >>> ovf.data[0, :, :, 2] = 1.0  # Set mz=1 in first layer
    >>> pyovf.write("modified.ovf", ovf)
"""

__version__ = "1.0.0"
__author__ = "Flavio Abreu Araujo"

from typing import Optional, Union
from pathlib import Path
import numpy as np

# Try to import the C++ extension
try:
    from ._ovf_core import OVFFile, IDX, file_exists
    _HAS_CPP_EXTENSION = True
except ImportError as e:
    _HAS_CPP_EXTENSION = False
    _IMPORT_ERROR = str(e)
    
    # Provide a pure-Python fallback
    class OVFFile:
        """Pure-Python OVF file handler (fallback when C++ extension unavailable)"""
        
        def __init__(self):
            self.Title = ""
            self.meshtype = "rectangular"
            self.meshunit = "m"
            self.xmin = self.ymin = self.zmin = 0.0
            self.xmax = self.ymax = self.zmax = 0.0
            self.xnodes = self.ynodes = self.znodes = 0
            self.xstepsize = self.ystepsize = self.zstepsize = 0.0
            self.xbase = self.ybase = self.zbase = 0.0
            self.valuedim = 3
            self.StageSimTime = 0.0
            self.TotalSimTime = 0.0
            self.StageSimTimeUnit = "s"
            self.TotalSimTimeUnit = "s"
            self._data = None
            
        @property
        def data(self):
            return self._data
        
        @data.setter
        def data(self, value):
            self._data = np.asarray(value, dtype=np.float32)
            if self._data.ndim == 4:
                self.znodes, self.ynodes, self.xnodes, self.valuedim = self._data.shape
            elif self._data.ndim == 3:
                self.znodes, self.ynodes, self.xnodes = self._data.shape
                self.valuedim = 1
                
        def read(self, filename: str) -> None:
            """Read OVF file (pure Python implementation)"""
            self._read_ovf_python(filename)
            
        def write(self, filename: str) -> None:
            """Write OVF file (pure Python implementation)"""
            self._write_ovf_python(filename)
            
        def _read_ovf_python(self, filename: str) -> None:
            """Pure Python OVF reader"""
            import struct
            
            with open(filename, 'rb') as f:
                # Read header
                while True:
                    line = f.readline().decode('latin-1').strip()
                    if not line:
                        continue
                    
                    if line.startswith('# Begin: Data Binary 4'):
                        # Read verification value
                        check = struct.unpack('<f', f.read(4))[0]
                        if abs(check - 1234567.0) > 1.0:
                            raise ValueError(f"Invalid verification value: {check}")
                        
                        # Read data
                        total = self.xnodes * self.ynodes * self.znodes * self.valuedim
                        raw = f.read(total * 4)
                        data = np.frombuffer(raw, dtype='<f4')
                        
                        if self.valuedim == 1:
                            self._data = data.reshape(self.znodes, self.ynodes, self.xnodes)
                        else:
                            self._data = data.reshape(self.znodes, self.ynodes, 
                                                      self.xnodes, self.valuedim)
                        break
                    
                    elif line.startswith('# Begin: Data'):
                        raise NotImplementedError("Only Binary 4 format is supported")
                    
                    # Parse header fields
                    if line.startswith('#'):
                        parts = line[1:].strip().split()
                        if len(parts) >= 2:
                            key = parts[0].rstrip(':')
                            value = parts[1] if len(parts) > 1 else ""
                            
                            if key == 'xnodes':
                                self.xnodes = int(value)
                            elif key == 'ynodes':
                                self.ynodes = int(value)
                            elif key == 'znodes':
                                self.znodes = int(value)
                            elif key == 'valuedim':
                                self.valuedim = int(value)
                            elif key == 'xstepsize':
                                self.xstepsize = float(value)
                            elif key == 'ystepsize':
                                self.ystepsize = float(value)
                            elif key == 'zstepsize':
                                self.zstepsize = float(value)
                            elif key == 'xmin':
                                self.xmin = float(value)
                            elif key == 'ymin':
                                self.ymin = float(value)
                            elif key == 'zmin':
                                self.zmin = float(value)
                            elif key == 'xmax':
                                self.xmax = float(value)
                            elif key == 'ymax':
                                self.ymax = float(value)
                            elif key == 'zmax':
                                self.zmax = float(value)
                            elif key == 'Title':
                                self.Title = value
                            elif key == 'meshtype':
                                self.meshtype = value
                            elif key == 'meshunit':
                                self.meshunit = value
                                
        def _write_ovf_python(self, filename: str) -> None:
            """Pure Python OVF writer"""
            import struct
            
            with open(filename, 'wb') as f:
                def writeln(s):
                    f.write((s + '\n').encode('latin-1'))
                
                writeln("# OOMMF OVF 2.0")
                writeln("# Segment count: 1")
                writeln("# Begin: Segment")
                writeln("# Begin: Header")
                writeln(f"# Title: {self.Title}")
                writeln(f"# meshtype: {self.meshtype}")
                writeln(f"# meshunit: {self.meshunit}")
                writeln(f"# xmin: {self.xmin}")
                writeln(f"# ymin: {self.ymin}")
                writeln(f"# zmin: {self.zmin}")
                writeln(f"# xmax: {self.xmax}")
                writeln(f"# ymax: {self.ymax}")
                writeln(f"# zmax: {self.zmax}")
                writeln(f"# valuedim: {self.valuedim}")
                writeln(f"# xbase: {self.xbase}")
                writeln(f"# ybase: {self.ybase}")
                writeln(f"# zbase: {self.zbase}")
                writeln(f"# xnodes: {self.xnodes}")
                writeln(f"# ynodes: {self.ynodes}")
                writeln(f"# znodes: {self.znodes}")
                writeln(f"# xstepsize: {self.xstepsize}")
                writeln(f"# ystepsize: {self.ystepsize}")
                writeln(f"# zstepsize: {self.zstepsize}")
                writeln("# End: Header")
                writeln("# Begin: Data Binary 4")
                
                # Write verification value
                f.write(struct.pack('<f', 1234567.0))
                
                # Write data
                data = np.asarray(self._data, dtype='<f4')
                f.write(data.tobytes())
                
                writeln("# End: Data Binary 4")
                writeln("# End: Segment")
    
    class IDX:
        """4D index structure"""
        def __init__(self, d=0, x=0, y=0, z=0):
            self.d = d
            self.x = x
            self.y = y
            self.z = z
            
    def file_exists(filename: str) -> bool:
        return Path(filename).exists()


def read(filename: Union[str, Path]) -> OVFFile:
    """
    Read an OVF file.
    
    Parameters
    ----------
    filename : str or Path
        Path to the OVF file to read.
        
    Returns
    -------
    OVFFile
        An OVFFile object containing the data and metadata.
        
    Examples
    --------
    >>> ovf = pyovf.read("magnetization.ovf")
    >>> print(ovf.data.shape)
    (1, 100, 100, 3)
    """
    ovf = OVFFile()
    ovf.read(str(filename))
    return ovf


def write(filename: Union[str, Path], ovf: OVFFile) -> None:
    """
    Write an OVF file.
    
    Parameters
    ----------
    filename : str or Path
        Path to the output OVF file.
    ovf : OVFFile
        An OVFFile object to write.
        
    Examples
    --------
    >>> ovf = pyovf.read("input.ovf")
    >>> ovf.data *= 2  # Modify data
    >>> pyovf.write("output.ovf", ovf)
    """
    ovf.write(str(filename))


def create(
    data: np.ndarray,
    xstepsize: float = 1e-9,
    ystepsize: float = 1e-9,
    zstepsize: float = 1e-9,
    title: str = "m",
    meshunit: str = "m",
) -> OVFFile:
    """
    Create a new OVFFile from a NumPy array.
    
    Parameters
    ----------
    data : np.ndarray
        Data array with shape (nz, ny, nx) for scalar or (nz, ny, nx, 3) for vector.
    xstepsize, ystepsize, zstepsize : float
        Cell sizes in meters.
    title : str
        Title/description of the data.
    meshunit : str
        Unit for spatial coordinates.
        
    Returns
    -------
    OVFFile
        A new OVFFile object.
        
    Examples
    --------
    >>> data = np.zeros((1, 100, 100, 3), dtype=np.float32)
    >>> data[..., 2] = 1.0  # mz = 1
    >>> ovf = pyovf.create(data, xstepsize=5e-9, ystepsize=5e-9, zstepsize=10e-9)
    >>> pyovf.write("uniform_mz.ovf", ovf)
    """
    ovf = OVFFile()
    ovf.data = np.asarray(data, dtype=np.float32)
    
    ovf.Title = title
    ovf.meshtype = "rectangular"
    ovf.meshunit = meshunit
    
    ovf.xstepsize = xstepsize
    ovf.ystepsize = ystepsize
    ovf.zstepsize = zstepsize
    
    ovf.xbase = xstepsize / 2
    ovf.ybase = ystepsize / 2
    ovf.zbase = zstepsize / 2
    
    ovf.xmin = 0.0
    ovf.ymin = 0.0
    ovf.zmin = 0.0
    ovf.xmax = ovf.xnodes * xstepsize
    ovf.ymax = ovf.ynodes * ystepsize
    ovf.zmax = ovf.znodes * zstepsize
    
    return ovf


def has_cpp_extension() -> bool:
    """Check if the C++ extension is available."""
    return _HAS_CPP_EXTENSION


# Public API
__all__ = [
    "read",
    "write", 
    "create",
    "OVFFile",
    "IDX",
    "file_exists",
    "has_cpp_extension",
    "__version__",
]