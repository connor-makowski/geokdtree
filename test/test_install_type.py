import os
import geokdtree


def test_install_type():
    """Verify that the expected implementation (C++ vs Pure Python) is loaded based on env vars."""
    require_cpp = os.environ.get("GEOKDTREE_REQUIRE_CPP") == "1"
    require_python = os.environ.get("GEOKDTREE_REQUIRE_PYTHON") == "1"

    is_cpp = "geokdtree.cpp" in geokdtree.GeoKDTree.__module__

    if require_cpp:
        assert (
            is_cpp
        ), "Expected C++ implementation (GEOKDTREE_REQUIRE_CPP=1), but Python implementation was loaded"
    elif require_python:
        assert (
            not is_cpp
        ), "Expected Python implementation (GEOKDTREE_REQUIRE_PYTHON=1), but C++ implementation was loaded"


def test_exports():
    """Verify that top-level exports are available and callable."""
    assert hasattr(geokdtree, "GeoKDTree")
    assert hasattr(geokdtree, "KDTree")
    assert callable(geokdtree.GeoKDTree)
    assert callable(geokdtree.KDTree)
