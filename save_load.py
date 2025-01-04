"""
Сначала нужно выполнить manual_save_board.py scan -
когда еще поле пустое, эта команда запомнит геометрию поля.

Затем в процессе игры manual_save_board.py save -
эта команда запишет в файл pickle объект Matrix,
который содержит "снимок" текущего поля

Команда load <DIR> воссоздает сохраненный объект Matrix
"""


import sys
import os
import pickle
import shelve
import cv2 as cv
from datetime import datetime

from matrix import Matrix
import asset
from board import board
# from main import find_board

from solver import solver_R1
from solver import solver_R1_corner
from solver import solver_R1_smart
from solver import solver_B1
from solver import solver_E1
from solver import solver_E2
from solver import solver_B2
from solver import solver_B1E1


def scan():
    col_values, row_values, region = find_board(asset.closed, board)
    with shelve.open('shelve') as d:
        d['col_values'] = col_values
        d['row_values'] = row_values
        d['region'] = region


def save():
    # todo move to config
    picklefile = 'obj.pickle'
    image_file = 'image.png'

    with shelve.open('shelve') as d:
        col_values = d['col_values']
        row_values = d['row_values']
        region = d['region']

    matrix = Matrix()
    matrix.initialize_from_screen(row_values, col_values, region)
    matrix.update()
    matrix.display()

    date_time_str = datetime.now().strftime("%d-%b-%Y--%H.%M.%S.%f")
    dir = 'game_SAVE_' + date_time_str

    if not os.path.exists(dir):
        os.makedirs(dir)

    with open(os.path.join(dir, picklefile), 'wb') as outp:
        pickle.dump(matrix, outp, pickle.HIGHEST_PROTOCOL)

    image = matrix.get_image()
    cv.imwrite(os.path.join(dir, image_file), image)

    print(f'Saved: {dir}')


def load(dir):
    """
    Demo load matrix from pickle
    :param f: relative path to obj.pickle
    :return: matrix object
    """
    picklefile = 'obj.pickle'
    image_file = 'image.png'
    full_path = os.path.join(dir, picklefile)

    print(full_path)
    with open(full_path, 'rb') as inp:
        matrix = pickle.load(inp)
    return matrix


def solve():
    """
    Test solve engine on saved board
    :return:
    """
    engine = solver_E2

    picklefile = 'obj.pickle'
    image_file = 'image.png'
    dir = 'game_R1_19-Dec-2024--20.28.53.526313_e74a'

    matrix = load(dir)
    matrix.display()

    cells, button = engine(matrix)
    print('Cells', cells)
    print('Button', button)


if __name__ == '__main__':
    action = sys.argv[1]
    if action == 'scan':
        scan()
    elif action == 'save':
        save()
    elif action == 'load':
        matrix = load(sys.argv[2])
        matrix.display()
    elif action == 'solve':
        solve()
