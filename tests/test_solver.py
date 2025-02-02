import pytest
"""
Not ready yet, just skip this file from pytest run.
"""
pytestmark = pytest.mark.skip

import os
import pickle
import pytest
import solver


@pytest.fixture()
def load_E2_1():
    picklefile = 'obj.pickle'
    image_file = 'image.png'
    dir = 'samples_for_solvers/E2_1'
    with open(os.path.join(dir, picklefile), 'rb') as inp:
        matrix = pickle.load(inp)
    return matrix

def test_E2_1(load_E2_1):
    engine = solver.solver_E2
    cells, button = engine(load_E2_1)
    assert cells[0].__repr__() == 'closed (7:2)'

