import numpy as np

cell_coord_x = [91, 122, 123, 154, 185, 217, 248, 279, 310, 311, 342, 374]
cell_coord_y = [715, 746, 777, 778, 809, 840, 841]

a = cell_coord_x

_, unique = np.unique(a.round(decimals=3), return_index=True)

print(_, unique)