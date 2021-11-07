import os
import pickle
import solve

# TODO добавить описание, что это и как этим юзать

def load(dir):
    with open(os.path.join(dir, picklefile), 'rb') as inp:
        matrix = pickle.load(inp)
    return matrix


if __name__ == '__main__':
    engine = solve.solver_E2

    picklefile = 'obj.pickle'
    image_file = 'image.png'
    dir = 'game_SAVE_01-Nov-2021--23.24.55.976936'
    matrix = load(dir)
    matrix.display()

    cells, button = engine(matrix)
    print('Cells', cells)
    print('Button', button)

