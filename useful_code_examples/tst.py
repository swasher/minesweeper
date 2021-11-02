col_values = [18, 42, 66, 90, 114, 138, 162, 186, 210, 234]
row_values = [81, 105, 129, 153, 177]

for row, coordy in enumerate(row_values):  # cell[строка][столбец]
    print()
    for col, coordx in enumerate(col_values):
        c = [row, col] #, coordx, coordy]
        # self.table[row, col] = c
        print(c, end='')