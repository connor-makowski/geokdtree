
from geokdtree import KDTree
from time import time

print("\n===============\nBasic Scale Tests:\n===============")

for n in range(1, 6):
    n_act = 10**n
    nodes = [(i, i + 1) for i in range(n_act)]
    start_time = time()
    kd_tree = KDTree(nodes)
    print(
        f"n={n_act} KD-Tree built in {round((time() - start_time) * 1000, 4)} ms"
    )
    start_time = time()
    closest_point = kd_tree.closest_point((5, 5.5))
    print(
        f"n={n_act} KD-Tree found in {round((time() - start_time) * 1000, 4)} ms"
    )
    if closest_point != (5, 6):
        print(f"KD-Tree closest point test failed for n={n_act}")
        success = False
