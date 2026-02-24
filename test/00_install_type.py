try:
    from geokdtree.cpp import KDTree
    print("Using C++ implementation of KDTree")
except ImportError:
    from geokdtree.kdtree import KDTree
    print("Using Python implementation of KDTree")