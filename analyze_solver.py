import os
import pickle

import solver


# TODO добавить описание, что это и как этим юзать

def load(dir):
    with open(os.path.join(dir, picklefile), 'rb') as inp:
        matrix = pickle.load(inp)
    return matrix


if __name__ == '__main__':
    engine = solver.solver_B1E1

    picklefile = 'obj.pickle'
    image_file = 'image.png'
    dir = 'game_SAVE_24-Nov-2021--16.23.22.264359'
    matrix = load(dir)
    matrix.display()

    cells, button = engine(matrix)
    print('Cells', cells)
    print('Button', button)

