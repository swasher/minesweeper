from .classes import Turn
from core.screen import ScreenMatrix as Matrix

from .solver_E1_new import solver_E1_new
from .solver_E2_new import solver_E2_new
from .solver_B1_new import solver_B1_new
from .solver_B2_new import solver_B2_new
from .solver_R1_smart import solver_R1_smart
from utils import remove_duplicated_turns


solvers = [solver_E1_new, solver_B1_new, solver_B2_new, solver_E2_new]


def multi_solver(matrix: Matrix) -> list[Turn]:
    turns = []
    for solver in solvers:
        solutions = solver(matrix)
        for turn in solutions:
            print(turn.cell, turn.solver)
        turns.extend(solutions)

    turns = remove_duplicated_turns(turns)

    return turns
