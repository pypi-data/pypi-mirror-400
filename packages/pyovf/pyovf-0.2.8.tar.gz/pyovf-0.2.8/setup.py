# (c) 2020-2026 Prof. Flavio ABREU ARAUJO. All rights reserved.

"""
Setup script for pyovf - compiles C++ extension on-the-fly
Supports Python 3.8 - 3.14
"""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext

# ovf-rw repository URL
OVF_RW_REPO = "https://gitlab.flavio.be/flavio/ovf-rw.git"


class CMakeExtension(Extension):
    """CMake extension for building C++ code"""
    
    def __init__(self, name: str, sourcedir: str = "") -> None:
        super().__init__(name, sources=[])
        self.sourcedir = os.fspath(Path(sourcedir).resolve())


class CMakeBuild(build_ext):
    """Custom build_ext command that runs CMake"""
    
    def build_extension(self, ext: CMakeExtension) -> None:
        # Ensure ovf-rw sources are available
        self._ensure_ovf_rw_sources()
        
        ext_fullpath = Path.cwd() / self.get_ext_fullpath(ext.name)
        extdir = ext_fullpath.parent.resolve()
        
        # CMake configuration
        debug = int(os.environ.get("DEBUG", 0)) if self.debug is None else self.debug
        cfg = "Debug" if debug else "Release"
        
        cmake_args = [
            f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}{os.sep}",
            f"-DPYTHON_EXECUTABLE={sys.executable}",
            f"-DCMAKE_BUILD_TYPE={cfg}",
        ]
        
        build_args = []
        
        if platform.system() == "Windows":
            cmake_args += [
                "-A", "x64" if sys.maxsize > 2**32 else "Win32",
            ]
            build_args += ["--config", cfg]
        else:
            # Unix-like systems
            cmake_args += [f"-DCMAKE_BUILD_TYPE={cfg}"]
            
        # Parallel build
        if "CMAKE_BUILD_PARALLEL_LEVEL" not in os.environ:
            if hasattr(self, "parallel") and self.parallel:
                build_args += [f"-j{self.parallel}"]
            else:
                import multiprocessing
                build_args += [f"-j{multiprocessing.cpu_count()}"]
        
        build_temp = Path(self.build_temp) / ext.name
        build_temp.mkdir(parents=True, exist_ok=True)
        
        subprocess.run(
            ["cmake", ext.sourcedir, *cmake_args],
            cwd=build_temp,
            check=True,
        )
        subprocess.run(
            ["cmake", "--build", ".", *build_args],
            cwd=build_temp,
            check=True,
        )
    
    def _ensure_ovf_rw_sources(self) -> None:
        """Ensure ovf-rw sources are available for building"""
        this_dir = Path(__file__).parent.resolve()
        
        # Check multiple possible locations
        possible_locations = [
            this_dir.parent / "ovf-rw" / "src_c++",  # Sibling directory
            this_dir / "src" / "pyovf" / "ovf-rw" / "src_c++",  # Bundled
            this_dir / "ovf-rw" / "src_c++",  # Local clone
        ]
        
        for loc in possible_locations:
            if (loc / "OVF_File.cpp").exists() and (loc / "OVF_File.h").exists():
                print(f"Found ovf-rw sources at: {loc}")
                return
        
        # Sources not found, try to clone
        print("ovf-rw sources not found, attempting to clone...")
        target_dir = this_dir / "src" / "pyovf" / "ovf-rw"
        
        if self._clone_ovf_rw(target_dir):
            return
        
        raise RuntimeError(
            "Could not find or clone ovf-rw source directory.\n"
            "Please either:\n"
            "  1. Clone ovf-rw next to pyovf: git clone https://gitlab.flavio.be/flavio/ovf-rw.git\n"
            "  2. Or place OVF_File.cpp and OVF_File.h in src/pyovf/ovf-rw/src_c++/\n"
        )
    
    def _clone_ovf_rw(self, target_dir: Path) -> bool:
        """Clone ovf-rw repository and extract needed sources"""
        try:
            import tempfile
            
            with tempfile.TemporaryDirectory() as tmpdir:
                print(f"Cloning ovf-rw from {OVF_RW_REPO}...")
                result = subprocess.run(
                    ["git", "clone", "--depth", "1", OVF_RW_REPO, tmpdir],
                    capture_output=True,
                    text=True,
                )
                
                if result.returncode != 0:
                    print(f"Git clone failed: {result.stderr}")
                    return False
                
                # Copy needed sources
                src_dir = Path(tmpdir) / "src_c++"
                dest_dir = target_dir / "src_c++"
                dest_dir.mkdir(parents=True, exist_ok=True)
                
                for filename in ["OVF_File.cpp", "OVF_File.h"]:
                    src_file = src_dir / filename
                    dest_file = dest_dir / filename
                    if src_file.exists():
                        shutil.copy2(src_file, dest_file)
                        print(f"Copied {filename} to {dest_file}")
                    else:
                        print(f"Warning: {filename} not found in cloned repo")
                        return False
                
                print("Successfully fetched ovf-rw sources")
                return True
                
        except Exception as e:
            print(f"Failed to clone ovf-rw: {e}")
            return False


def get_ovf_rw_source_dir() -> str:
    """Get the path to ovf-rw source directory"""
    # Check relative to this file
    this_dir = Path(__file__).parent.resolve()
    
    # Check sibling directory first (development setup)
    ovf_rw_dir = this_dir.parent / "ovf-rw"
    if ovf_rw_dir.exists():
        return str(ovf_rw_dir)
    
    # Check if sources are bundled with the package
    bundled_dir = this_dir / "src" / "pyovf" / "ovf-rw"
    if bundled_dir.exists():
        return str(bundled_dir)
    
    # Check local clone
    local_dir = this_dir / "ovf-rw"
    if local_dir.exists():
        return str(local_dir)
    
    raise RuntimeError(
        "Could not find ovf-rw source directory. "
        "Please ensure the ovf-rw directory is present."
    )


setup(
    ext_modules=[CMakeExtension("pyovf._ovf_core", sourcedir=".")],
    cmdclass={"build_ext": CMakeBuild},
)
