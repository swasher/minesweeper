from .solver_R1 import solver_R1
from .solver_R1_smart import solver_R1_smart
from .solver_B1 import solver_B1
from .solver_B2 import solver_B2
from .solver_E1 import solver_E1
from .solver_E2 import solver_E2
from .solver_B1E1 import solver_B1E1
from .solver_noguess import solver_noguess

from solver.multi_solver import multi_solver
from . import solver_B1_new
from . import solver_B2_new
from .solver_E1_new import solver_E1_new
from .solver_E2_new import solver_E2_new

__all__ = [
    'solver_B1', 'solver_E2', 'solver_B2', 'solver_B1E1',
    'solver_R1_smart', 'solver_R1',
    'solver_B1_new', 'solver_B2_new', 'solver_E1_new', 'solver_E2_new',
    'solver_noguess',
    'multi_solver'
]