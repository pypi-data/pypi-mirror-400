"""Additional coverage tests to exercise package entrypoints and helpers.

These tests reload `pyovf` from the repo source tree (not the installed
site-packages) so coverage counts towards the tracked files.
"""

import importlib
import sys
from pathlib import Path

import numpy as np
import pytest


def _reload_pyovf_from_repo():
    """Reload pyovf ensuring the repo path is first on sys.path.

    If the C++ extension is not available, skip the calling test.
    """
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    # Prefer in-tree built extension artifacts if present (e.g. build/lib.*-cpython-313)
    abi_tag = f"cpython-{sys.version_info.major}{sys.version_info.minor}"
    build_dir = repo_root / "build"
    if build_dir.exists():
        candidates = sorted(
            build_dir.glob(f"lib.*-{abi_tag}"),
            key=lambda p: len(p.name),
        )
        for candidate in candidates:
            if candidate.is_dir():
                sys.path.insert(0, str(candidate))

    # Drop cached modules to force reload from source
    for name in list(sys.modules.keys()):
        if name == "pyovf" or name.startswith("pyovf."):
            sys.modules.pop(name, None)

    try:
        return importlib.import_module("pyovf")
    except ImportError as exc:
        pytest.skip(
            f"pyovf extension not available for Python {sys.version_info.major}.{sys.version_info.minor}: {exc}",
            allow_module_level=False,
        )


def test_version_and_init_execution():
    pyovf = _reload_pyovf_from_repo()

    # __init__ should expose __version__ and author metadata
    assert hasattr(pyovf, "__version__")
    assert isinstance(pyovf.__version__, str)
    assert hasattr(pyovf, "__author__")
    assert hasattr(pyovf, "__email__")

    # _version module should be imported and populated
    ver = importlib.import_module("pyovf._version")
    assert ver.__version__ == pyovf.__version__
    assert isinstance(ver.__version_tuple__, tuple)


def test_helper_size_hrf():
    pyovf = _reload_pyovf_from_repo()
    from pyovf.helper_funcs import size_hrf

    assert size_hrf(0) == "0B"
    assert size_hrf(1024) == "1KiB"
    # Large value should scale
    human = size_hrf(5 * 1024**3)
    assert human.endswith("GiB")


def test_basic_create_read_write_roundtrip(tmp_path):
    pyovf = _reload_pyovf_from_repo()

    data = np.random.rand(1, 4, 5, 3).astype(np.float32)
    ovf = pyovf.create(data, title="coverage")

    target = tmp_path / "cov.ovf"
    pyovf.write(str(target), ovf)

    ovf2 = pyovf.read(str(target))
    np.testing.assert_array_almost_equal(ovf2.data, data)
    assert ovf2.Title == "coverage"

    # read_data_only path
    arr = pyovf.read_data_only(str(target))
    np.testing.assert_array_equal(arr, data.squeeze())


def test_has_cpp_extension_and_file_exists(tmp_path):
    pyovf = _reload_pyovf_from_repo()

    dummy = tmp_path / "dummy.txt"
    dummy.write_text("ok")

    assert pyovf.has_cpp_extension() is True
    assert pyovf.file_exists(str(dummy)) is True
    assert pyovf.file_exists(str(tmp_path / "missing.txt")) is False
