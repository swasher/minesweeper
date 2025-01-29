from core import Matrix

matrix = Matrix()
matrix.load('patterns/5x5_E1_1__.txt')
matrix.display()
print(f'Total mines: {matrix.total_mines}')
print(f'Flags count: {matrix.get_num_flags}')
print(f'Mines remained: {matrix.get_remaining_mines_count}')
matrix.solve()
