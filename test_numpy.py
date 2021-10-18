import numpy as np
import icecream as ic

class Cell(object):
    x = 0
    y = 0
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __repr__(self):
        return f'{x}:{y}'

row = 3
col = 3
a = np.empty(shape=(col, row), dtype=Cell)

for y in range(row):
    for x in range(col):
        c = Cell(x, y)
        print(c)
        a[x, y] = c
        print(a[x, y])
        print()

print(a)
print(a[0][0])
print(a[1][1])
