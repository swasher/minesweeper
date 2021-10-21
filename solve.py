import icecream
from util import remove_dup

def solve(matrix):
    bomb_cells = solver_B1(matrix)
    #return array, click  # мы возвращаем несколько клеток и действие, что делать - либо отметить как бомбы
                         # либо как пустые клетки
    return bomb_cells, []


# DEPRECATED
# def count_around_closed(matrix, x, y):
#     count = 0
#     cells = []
#     for row in [x-1, x, x+1]:
#         for col in [y-1, y, y+1]:
#             if (row not in range(matrix.matrix_width)) \
#                     or (col not in range(matrix.matrix_height)) \
#                     or (row == x and col == y):
#                 continue
#             if matrix.table[row][col].status in ['closed', 'flag']:  # в подсчете принимают участие
#                                                         # все закрытые ячейки - и closed и flag
#                 count += 1
#                 if matrix.table[row][col].status == 'closed':    # но в список для отмечания флажком попадают
#                                                                 # только те, которые еще не отмечены, т.е. тьолько closed
#                     cells.append([row, col])
#     return count, cells


def solver_B1(matrix):
    bomb_cells = []
    for cell in matrix.number_cells():
        cells = matrix.around_closed_cells(cell)
        if cell.number == len(cells):
            # значит во всех клетках cells есть бомбы
            bomb_cells += cells
    bomb_cells = remove_dup(bomb_cells)
    return bomb_cells


def solver_B2():
    pass