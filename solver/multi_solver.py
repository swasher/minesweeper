from .classes import Turn
from core.screen import ScreenMatrix as Matrix

from . import solver_E1_new
from . import solver_B1_new
from .solver_B1 import solver_B1
from .solver_R1_smart import solver_R1_smart


solvers = [solver_E1_new, solver_B1_new, solver_R1_smart]


def multi_solver(matrix: Matrix) -> list[Turn]:
    for solver in solvers:
        pass