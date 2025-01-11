import pytest
import numpy as np
from classes import SolveMatrix
from classes import Cell


@pytest.fixture
def matrix():
    """Creates a 3x3 matrix with all cells initially closed."""
    m = SolveMatrix(width=3, height=3)
    # Fill matrix with cells
    for row in range(3):
        for col in range(3):
            m.table[row, col] = Cell(m, row=row, col=col)
            m.table[row, col].is_closed = True  # All cells start closed
    return m


def test_all_cells_closed(matrix):
    """Test when all surrounding cells are closed."""
    center = matrix.table[1, 1]
    closed_cells = matrix.around_closed_cells(center)

    assert len(closed_cells) == 8
    assert all(cell.is_closed for cell in closed_cells)


def test_all_cells_open(matrix):
    """Test when all surrounding cells are open."""
    # Open all cells
    for row in range(3):
        for col in range(3):
            matrix.table[row, col].is_closed = False

    center = matrix.table[1, 1]
    closed_cells = matrix.around_closed_cells(center)

    assert len(closed_cells) == 0


def test_mixed_cells(matrix):
    """Test with mix of open and closed cells."""
    # Open specific cells around center
    positions_to_open = [(0, 0), (0, 2), (2, 2)]  # corners
    for row, col in positions_to_open:
        matrix.table[row, col].is_closed = False

    center = matrix.table[1, 1]
    closed_cells = matrix.around_closed_cells(center)

    assert len(closed_cells) == 5  # 8 surrounding - 3 opened
    assert all(cell.is_closed for cell in closed_cells)


def test_corner_cell(matrix):
    """Test for a corner cell (top-left)."""
    corner = matrix.table[0, 0]
    closed_cells = matrix.around_closed_cells(corner)

    assert len(closed_cells) == 3  # Corner has only 3 neighbors
    assert all(cell.is_closed for cell in closed_cells)


def test_edge_cell(matrix):
    """Test for an edge cell (top-middle)."""
    edge = matrix.table[0, 1]
    closed_cells = matrix.around_closed_cells(edge)

    assert len(closed_cells) == 5  # Edge has 5 neighbors
    assert all(cell.is_closed for cell in closed_cells)


def test_flagged_cells(matrix):
    """Test that flagged cells are counted as closed."""
    center = matrix.table[1, 1]

    # Flag some cells but keep them closed
    matrix.table[0, 0].is_flagged = True
    matrix.table[0, 1].is_flagged = True

    closed_cells = matrix.around_closed_cells(center)
    flagged_count = sum(1 for cell in closed_cells if cell.is_flagged)

    assert len(closed_cells) == 8  # All cells still counted as closed
    assert flagged_count == 2  # Two cells should be flagged


@pytest.mark.parametrize("pos,expected_count", [
    ((0, 0), 3),  # top-left corner
    ((0, 1), 5),  # top edge
    ((1, 1), 8),  # center
    ((2, 2), 3),  # bottom-right corner
    ((1, 0), 5),  # left edge
])
def test_various_positions(matrix, pos, expected_count):
    """Test closed cells count from various positions."""
    row, col = pos
    cell = matrix.table[row, col]
    closed_cells = matrix.around_closed_cells(cell)

    assert len(closed_cells) == expected_count
    assert all(cell.is_closed for cell in closed_cells)


def test_single_open_neighbor(matrix):
    """Test with only one open neighbor."""
    center = matrix.table[1, 1]
    matrix.table[0, 0].is_closed = False  # Open just one neighbor

    closed_cells = matrix.around_closed_cells(center)

    assert len(closed_cells) == 7
    assert all(cell.is_closed for cell in closed_cells)
    assert matrix.table[0, 0] not in closed_cells


def test_1x1_matrix():
    """Test with 1x1 matrix (no neighbors)."""
    tiny_matrix = SolveMatrix(width=1, height=1)
    tiny_matrix.table[0, 0] = Cell(tiny_matrix, row=0, col=0)

    closed_cells = tiny_matrix.around_closed_cells(tiny_matrix.table[0, 0])
    assert len(closed_cells) == 0
