"""
Сначала нужно выполнить save_board.py scan -
эта команда запомнит геометрию поля.

Затем save_board.py save -
эта команда запишет в файл pickle объект Matrix,
который содержит "снимок" текущего поля
"""


import sys
import pickle
import shelve
from patterns import patterns
from main import find_board
from matrix import Matrix
from datetime import datetime


def scan():
    board = find_board()

def save():
    row_values, col_values, region = find_board(patterns)
    matrix = Matrix(row_values, col_values, region, patterns)
    matrix.update()
    matrix.display()

    dateTimeObjStr = datetime.now().strftime("%d-%b-%Y--%H:%M:%S")
    picklefile = 'pickle_' + dateTimeObjStr

    with open(picklefile, 'wb') as outp:
        pickle.dump(matrix, outp, pickle.HIGHEST_PROTOCOL)



def shelve_examples():
    d = shelve.open(filename)
    d[key] = data  # store
    data = d[key]  # load
    d.close()


if __name__ == '__main__':
    action = sys.argv[1:]
    if action == scan
