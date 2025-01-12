import pytest
import numpy as np
from classes import SolveMatrix
from classes import Cell
from asset import asset

"""
The tests cover:
All surrounding cells closed
All surrounding cells open
Mix of open and closed cells
Flagged cells (should not be counted as closed)
Corner cells (3 neighbors)
Edge cells (5 neighbors)
Various positions on the board
1x1 matrix edge case
Parametrized tests for different positions
Each test verifies both the count of closed cells and ensures that returned cells are actually closed. The tests use the fixtures and asset system that appears to be part of the codebase.
"""


@pytest.fixture
def matrix():
    """Creates a 3x3 matrix with all cells initially closed."""
    m = SolveMatrix(width=3, height=3)
    # Fill matrix with cells
    for row in range(3):
        for col in range(3):
            m.table[row, col] = Cell(m, row=row, col=col)
            m.table[row, col].content = asset.closed  # All cells start closed
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
    for cell in matrix.table.flat:
        cell.content = asset.n0  # Set all cells as open with 0 mines around

    center = matrix.table[1, 1]
    closed_cells = matrix.around_closed_cells(center)
    
    assert len(closed_cells) == 0

def test_mixed_cells(matrix):
    """Test with mix of open and closed cells."""
    center = matrix.table[1, 1]
    
    # Open specific cells around center
    matrix.table[0, 0].content = asset.n1  # Open with 1 mine around
    matrix.table[0, 2].content = asset.n2  # Open with 2 mines around
    matrix.table[2, 2].content = asset.n0  # Open with 0 mines around
    
    closed_cells = matrix.around_closed_cells(center)
    
    assert len(closed_cells) == 5  # Should have 5 closed cells remaining
    assert all(cell.is_closed for cell in closed_cells)

def test_flagged_cells(matrix):
    """Test that flagged cells are not counted as closed."""
    center = matrix.table[1, 1]
    
    # Flag some cells
    matrix.table[0, 0].content = asset.flag
    matrix.table[0, 1].content = asset.flag
    
    closed_cells = matrix.around_closed_cells(center)
    
    assert len(closed_cells) == 6  # 8 surrounding - 2 flagged
    assert all(cell.is_closed for cell in closed_cells)
    assert all(not cell.is_flag for cell in closed_cells)

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

def test_1x1_matrix():
    """Test with 1x1 matrix (no neighbors)."""
    tiny_matrix = SolveMatrix(width=1, height=1)
    tiny_matrix.table[0, 0] = Cell(tiny_matrix, row=0, col=0)
    tiny_matrix.table[0, 0].asset = asset.closed
    
    closed_cells = tiny_matrix.around_closed_cells(tiny_matrix.table[0, 0])
    assert len(closed_cells) == 0
