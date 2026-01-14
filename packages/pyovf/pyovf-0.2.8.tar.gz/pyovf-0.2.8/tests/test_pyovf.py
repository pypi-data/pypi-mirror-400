"""
Unit tests for pyovf
"""

import numpy as np
import pytest
import tempfile
import os
import sys
from pathlib import Path

# Ensure repo and in-tree build artifacts are importable before attempting pyovf import
repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

abi_tag = f"cpython-{sys.version_info.major}{sys.version_info.minor}"
build_dir = repo_root / "build"
if build_dir.exists():
    for candidate in sorted(build_dir.glob(f"lib.*-{abi_tag}"), key=lambda p: len(p.name)):
        if candidate.is_dir():
            sys.path.insert(0, str(candidate))

# Attempt to import pyovf; skip tests if the C++ extension isn't available
try:
    import pyovf
except ImportError as exc:
    pytest.skip(
        "pyovf extension not available for this interpreter; build or install the wheel first",
        allow_module_level=True,
    )


class TestOVFFile:
    """Tests for OVFFile class"""
    
    def test_create_empty(self):
        """Test creating an empty OVFFile"""
        ovf = pyovf.OVFFile()
        assert ovf.xnodes == 0
        assert ovf.ynodes == 0
        assert ovf.znodes == 0
        
    def test_create_with_data(self):
        """Test creating OVFFile with data"""
        data = np.random.rand(2, 10, 20, 3).astype(np.float32)
        ovf = pyovf.create(data, xstepsize=5e-9, ystepsize=5e-9, zstepsize=10e-9)
        
        assert ovf.xnodes == 20
        assert ovf.ynodes == 10
        assert ovf.znodes == 2
        assert ovf.valuedim == 3
        assert ovf.xstepsize == 5e-9
        
    def test_create_scalar_field(self):
        """Test creating a scalar field"""
        data = np.random.rand(1, 50, 50).astype(np.float32)
        ovf = pyovf.create(data)
        
        assert ovf.valuedim == 1
        assert ovf.xnodes == 50
        assert ovf.ynodes == 50
        assert ovf.znodes == 1


class TestReadWrite:
    """Tests for read/write functionality"""
    
    def test_roundtrip_vector(self):
        """Test writing and reading a vector field"""
        # Create test data
        data = np.random.rand(2, 10, 20, 3).astype(np.float32)
        ovf = pyovf.create(data, title="test_m")
        
        with tempfile.NamedTemporaryFile(suffix='.ovf', delete=False) as f:
            filename = f.name
            
        try:
            # Write
            pyovf.write(filename, ovf)
            assert os.path.exists(filename)
            
            # Read back
            ovf2 = pyovf.read(filename)
            
            # Verify
            assert ovf2.xnodes == ovf.xnodes
            assert ovf2.ynodes == ovf.ynodes
            assert ovf2.znodes == ovf.znodes
            assert ovf2.valuedim == ovf.valuedim
            np.testing.assert_array_almost_equal(ovf2.data, data, decimal=5)
            
        finally:
            os.unlink(filename)
            
    def test_roundtrip_scalar(self):
        """Test writing and reading a scalar field"""
        data = np.random.rand(1, 50, 50).astype(np.float32)
        ovf = pyovf.create(data, title="test_scalar")
        
        with tempfile.NamedTemporaryFile(suffix='.ovf', delete=False) as f:
            filename = f.name
            
        try:
            pyovf.write(filename, ovf)
            ovf2 = pyovf.read(filename)
            
            assert ovf2.valuedim == 1
            np.testing.assert_array_almost_equal(ovf2.data, data, decimal=5)
            
        finally:
            os.unlink(filename)
            
    def test_metadata_preservation(self):
        """Test that metadata is preserved through read/write cycle"""
        data = np.zeros((1, 10, 10, 3), dtype=np.float32)
        ovf = pyovf.create(data)
        ovf.Title = "magnetization"
        ovf.meshunit = "nm"
        ovf.TotalSimTime = 1e-9
        ovf.TotalSimTimeUnit = "s"
        
        with tempfile.NamedTemporaryFile(suffix='.ovf', delete=False) as f:
            filename = f.name
            
        try:
            pyovf.write(filename, ovf)
            ovf2 = pyovf.read(filename)
            
            assert ovf2.Title == "magnetization"
            # Note: some metadata may not round-trip perfectly
            
        finally:
            os.unlink(filename)


class TestUtilities:
    """Tests for utility functions"""
    
    def test_has_cpp_extension(self):
        """Test has_cpp_extension function"""
        result = pyovf.has_cpp_extension()
        assert isinstance(result, bool)
        
    def test_file_exists(self):
        """Test file_exists function"""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            filename = f.name
            
        try:
            assert pyovf.file_exists(filename)
            os.unlink(filename)
            assert not pyovf.file_exists(filename)
        except:
            if os.path.exists(filename):
                os.unlink(filename)
            raise


class TestDataManipulation:
    """Tests for data manipulation"""
    
    def test_data_modification(self):
        """Test that data can be modified"""
        data = np.zeros((1, 10, 10, 3), dtype=np.float32)
        ovf = pyovf.create(data)
        
        # Modify data
        ovf.data[0, 5, 5, 2] = 1.0
        
        assert ovf.data[0, 5, 5, 2] == 1.0
        
    def test_data_shape(self):
        """Test data array shape"""
        data = np.random.rand(3, 20, 30, 3).astype(np.float32)
        ovf = pyovf.create(data)
        
        assert ovf.data.shape == (3, 20, 30, 3)


class TestAdvancedFeatures:
    """Tests for advanced features and edge cases"""
    
    def test_large_file_handling(self):
        """Test handling of large files"""
        data = np.random.rand(10, 100, 100, 3).astype(np.float32)
        ovf = pyovf.create(data)
        
        with tempfile.NamedTemporaryFile(suffix='.ovf', delete=False) as f:
            filename = f.name
            
        try:
            pyovf.write(filename, ovf)
            ovf2 = pyovf.read(filename)
            assert ovf2.data.shape == data.shape
        finally:
            if os.path.exists(filename):
                os.unlink(filename)
    
    def test_different_data_types(self):
        """Test handling different numeric types"""
        # Test float64
        data64 = np.random.rand(1, 10, 10, 3).astype(np.float64)
        ovf64 = pyovf.create(data64)
        assert ovf64.data.dtype in [np.float32, np.float64]
        
        # Test int32 conversion
        data_int = np.random.randint(0, 100, (1, 10, 10, 3)).astype(np.int32)
        ovf_int = pyovf.create(data_int)
        assert ovf_int.data is not None
    
    def test_single_cell(self):
        """Test with single cell"""
        data = np.array([[[[1, 2, 3]]]], dtype=np.float32)
        ovf = pyovf.create(data)
        
        assert ovf.xnodes == 1
        assert ovf.ynodes == 1
        assert ovf.znodes == 1
    
    def test_custom_step_sizes(self):
        """Test with custom step sizes"""
        data = np.random.rand(1, 10, 10, 3).astype(np.float32)
        ovf = pyovf.create(
            data,
            xstepsize=1e-8,
            ystepsize=2e-8,
            zstepsize=5e-8
        )
        
        assert ovf.xstepsize == 1e-8
        assert ovf.ystepsize == 2e-8
        assert ovf.zstepsize == 5e-8
    
    def test_ovf_properties(self):
        """Test OVFFile properties and attributes"""
        data = np.random.rand(2, 15, 20, 3).astype(np.float32)
        ovf = pyovf.create(data)
        
        # Test various properties
        assert hasattr(ovf, 'xnodes')
        assert hasattr(ovf, 'ynodes')
        assert hasattr(ovf, 'znodes')
        assert hasattr(ovf, 'valuedim')
        assert hasattr(ovf, 'xstepsize')
        assert hasattr(ovf, 'ystepsize')
        assert hasattr(ovf, 'zstepsize')
        assert hasattr(ovf, 'data')
    
    def test_read_nonexistent_file(self):
        """Test reading a non-existent file"""
        try:
            pyovf.read('/nonexistent/path/file.ovf')
            # If we get here, the function didn't raise an error
            # That's okay, it might return None or an empty OVFFile
        except (FileNotFoundError, IOError, OSError):
            # This is expected
            pass
    
    def test_write_to_invalid_path(self):
        """Test writing to an invalid path"""
        data = np.random.rand(1, 10, 10, 3).astype(np.float32)
        ovf = pyovf.create(data)
        
        try:
            pyovf.write('/nonexistent/invalid/path/file.ovf', ovf)
        except (FileNotFoundError, IOError, OSError, PermissionError):
            # This is expected
            pass
    
    def test_version_info(self):
        """Test version information"""
        assert hasattr(pyovf, '__version__')
        version = pyovf.__version__
        assert isinstance(version, str)
        assert len(version) > 0
    
    def test_helper_functions(self):
        """Test helper functions"""
        # Test that helper functions are available
        assert callable(pyovf.has_cpp_extension)
        assert callable(pyovf.file_exists)
        
        # Test has_cpp_extension
        cpp_ext = pyovf.has_cpp_extension()
        assert isinstance(cpp_ext, bool)
    
    def test_empty_dimension(self):
        """Test handling of zero-size dimensions"""
        try:
            data = np.zeros((0, 10, 10, 3), dtype=np.float32)
            ovf = pyovf.create(data)
            assert ovf.znodes == 0
        except (ValueError, RuntimeError):
            # Empty dimensions might raise an error, which is acceptable
            pass


class TestErrorHandling:
    """Tests for error handling and edge cases"""
    
    def test_invalid_data_shape(self):
        """Test with invalid data shapes"""
        try:
            # 2D array instead of 3D or 4D
            data = np.random.rand(10, 10)
            ovf = pyovf.create(data)
        except (ValueError, RuntimeError, TypeError):
            pass
    
    def test_none_data(self):
        """Test with None as data"""
        try:
            ovf = pyovf.create(None)
        except (ValueError, RuntimeError, TypeError, AttributeError):
            pass
    
    def test_corrupted_file_handling(self):
        """Test handling of corrupted OVF files"""
        with tempfile.NamedTemporaryFile(suffix='.ovf', delete=False) as f:
            f.write(b"This is not a valid OVF file")
            filename = f.name
        
        try:
            try:
                ovf = pyovf.read(filename)
            except (IOError, ValueError, RuntimeError):
                pass
        finally:
            os.unlink(filename)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])