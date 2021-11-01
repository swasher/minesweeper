"""
Сначала нужно выполнить manual_save_board.py scan -
когда еще поле пустое, эта команда запомнит геометрию поля.

Затем manual_save_board.py save -
эта команда запишет в файл pickle объект Matrix,
который содержит "снимок" текущего поля
"""


import sys
import os
import pickle
import shelve
import cv2 as cv
from datetime import datetime

from matrix import Matrix
from patterns import patterns
from patterns import Asset
from main import find_board


def scan():
    board = find_board(patterns, Asset)
    with shelve.open('shelve') as d:
        d['col_values'] = board[0]
        d['row_values'] = board[1]
        d['region'] = board[2]


def save():
    with shelve.open('shelve') as d:
        col_values = d['col_values']
        row_values = d['row_values']
        region = d['region']

    matrix = Matrix(row_values, col_values, region, patterns)
    matrix.update()
    matrix.display()

    date_time_str = datetime.now().strftime("%d-%b-%Y--%H.%M.%S.%f")
    dir = 'game_SAVE_' + date_time_str
    picklefile = 'obj.pickle'
    image_file = 'image.png'

    if not os.path.exists(dir):
        os.makedirs(dir)

    with open(os.path.join(dir, picklefile), 'wb') as outp:
        pickle.dump(matrix, outp, pickle.HIGHEST_PROTOCOL)

    image = matrix.get_image()
    cv.imwrite(os.path.join(dir, image_file), image)


if __name__ == '__main__':
    action = sys.argv[1]
    if action == 'scan':
        scan()
    elif action == 'save':
        save()


