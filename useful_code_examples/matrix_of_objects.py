import numpy

num_rows = 4
num_cols = 4


class Cell:
    status = ''
    x = 0
    y = 0

    def __init__(self, status, x, y):
        self.status = status
        self.x = x
        self.y = y

    def count_closed(self):
        pass


matrix = numpy.full((num_rows, num_cols), Cell)


def fill_matrix():
    for x in range(num_rows):
        for y in range(num_cols):
            c = Cell('closed', x, y)
            matrix[x][y] = c


def prn():
    for x in range(num_rows):
        # print('\n')
        t = ''
        for y in range(num_cols):
            # print(type(matrix[x][y]))
            s = matrix[x][y].status
            t = t + s + ' - '
        print(t)


fill_matrix()
prn()
matrix[1][2].status = 'open'
print('\n')
prn()