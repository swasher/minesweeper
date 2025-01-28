# these exports can be deleted
from .minesweeper_util import read_board      # only for demo_run_minesweepr.py
from .minesweeper_util import Board           # only for demo_run_minesweepr.py
from .minesweeper_util import generate_rules  # only for demo_run_minesweepr.py

from .minesweeper import InconsistencyError
from .transformer import solver

__all__ = ['solver', 'InconsistencyError']
