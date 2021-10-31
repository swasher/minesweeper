# c - closed
# f - flag
m = [['0', '1', 'closed'],
     ['1', '2', 'closed'],
     ['2', 'flag', 'closed'],
     ['3', 'closed', 'closed']]

import os
import numpy as np
from matrix import Matrix
# from cell import Cell
import cell
import re
import icecream as ic
from solve import solver_E2


def load_pic(pic='test_E2/test_E2_1_4x3.png'):
    f = os.path.basename(pic)
    result = re.search(r'(\d+)x(\d+)', f)
    rows = result[1]
    cols = result[2]
    print(rows, cols)
    ic('  second scan...')
    region = (region_x1, region_y1, region_x2, region_y2)
    cells_coord_x, cells_coord_y = scan_region(region, pattern.closed.raster)
    ic('  finish')
    # return data as `find_board`
    return cells_coord_x, cells_coord_y, region



class Matrix_test(Matrix):

    def __init__(self, rows, cols, m):
        self.height = rows
        self.width = cols
        self.table = np.full((rows, cols), cell.Cell)

        for row, row_content in enumerate(m):
            for col, status in enumerate(row_content):
                c = cell.Cell(row, col, 0, 0, 0, 0)
                c.status = status
                self.table[row, col] = c


if __name__ == '__main__':
    # rows = len(m)
    # cols = len(m[0])
    # matrix_test = Matrix_test(rows, cols, m)
    # matrix_test.display()
    #
    # cells, _ = solver_E2(matrix_test)
    # print('----')
    # print(cells)

    load_pic()

