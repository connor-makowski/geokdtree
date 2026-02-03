try:
    from geokdtree.bin.geokdtree_cpp import KDTree, GeoKDTree
    # print("Using C++ GeoKDTree implementation")
except ImportError:
    # print("Using pure-Python GeoKDTree implementation")
    from .core import KDTree, GeoKDTree