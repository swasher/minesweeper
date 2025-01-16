import pytest
import numpy as np
from typing import List, Tuple
from classes import Cell
from classes import ScreenMatrix


@pytest.fixture
def matrix():
    """Create a 3x4 matrix with unique cells for testing."""
    m = ScreenMatrix(width=4, height=3)
    for row in range(3):
        for col in range(4):
            m.table[row, col] = Cell(m, row=row, col=col)
    return m


@pytest.fixture
def small_matrix():
    """Create a 2x2 matrix with unique cells."""
    m = ScreenMatrix(width=2, height=2)
    for row in range(2):
        for col in range(2):
            m.table[row, col] = Cell(m, row=row, col=col)
    return m


@pytest.fixture
def tiny_matrix():
    """Create a 1x1 matrix with a single cell."""
    m = ScreenMatrix(width=1, height=1)
    m.table[0, 0] = Cell(m, row=0, col=0)
    return m


def test_center_cell(matrix):
    """Test neighbors for a center cell (should have 8 neighbors)."""
    center = matrix.table[1, 1]
    neighbors = matrix.around_cells(center)

    expected_positions = {
        (0, 0), (0, 1), (0, 2),
        (1, 0),         (1, 2),
        (2, 0), (2, 1), (2, 2)
    }

    assert len(neighbors) == 8
    assert all(isinstance(cell, Cell) for cell in neighbors)

    neighbor_positions = {(cell.row, cell.col) for cell in neighbors}
    assert neighbor_positions == expected_positions


@pytest.mark.parametrize("position,expected_count", [
    ((0, 0), 3),  # top-left
    ((0, 3), 3),  # top-right
    ((2, 0), 3),  # bottom-left
    ((2, 3), 3)  # bottom-right
])
def test_corner_cells(matrix, position, expected_count):
    """Test neighbors for corner cells (should have 3 neighbors each)."""
    row, col = position
    cell = matrix.table[row, col]
    neighbors = matrix.around_cells(cell)

    assert len(neighbors) == expected_count
    assert all(isinstance(cell, Cell) for cell in neighbors)


@pytest.mark.parametrize("position,expected_count", [
    ((0, 1), 5),  # top edge
    ((0, 2), 5),  # top edge
    ((1, 0), 5),  # left edge
    ((1, 3), 5),  # right edge
    ((2, 1), 5),  # bottom edge
    ((2, 2), 5)  # bottom edge
])
def test_edge_cells(matrix, position, expected_count):
    """Test neighbors for edge cells (should have 5 neighbors each)."""
    row, col = position
    cell = matrix.table[row, col]
    neighbors = matrix.around_cells(cell)

    assert len(neighbors) == expected_count
    assert all(isinstance(cell, Cell) for cell in neighbors)


def test_invalid_coordinates(matrix):
    """Test behavior with invalid cell coordinates."""
    invalid_cell = Cell(matrix, row=5, col=5)  # Outside matrix bounds

    with pytest.raises(IndexError):
        matrix.around_cells(invalid_cell)


def test_1x1_matrix(tiny_matrix):
    """Test behavior with a 1x1 matrix (should have 0 neighbors)."""
    neighbors = tiny_matrix.around_cells(tiny_matrix.table[0, 0])
    assert len(neighbors) == 0


@pytest.mark.parametrize("position", [
    (0, 0), (0, 1),
    (1, 0), (1, 1)
])
def test_2x2_matrix(small_matrix, position):
    """Test behavior with a 2x2 matrix (should have 3 neighbors per cell)."""
    row, col = position
    cell = small_matrix.table[row, col]
    neighbors = small_matrix.around_cells(cell)

    assert len(neighbors) == 3
    assert all(isinstance(cell, Cell) for cell in neighbors)


def test_cell_uniqueness(matrix):
    """Test that each neighbor is returned exactly once."""
    center = matrix.table[1, 1]
    neighbors = matrix.around_cells(center)

    positions = [(cell.row, cell.col) for cell in neighbors]
    unique_positions = set(positions)

    assert len(positions) == len(unique_positions), "Each neighbor should appear exactly once"


def test_neighbor_values(matrix):
    """Test that neighbor cells have correct row and column values."""
    center = matrix.table[1, 1]
    neighbors = matrix.around_cells(center)

    for cell in neighbors:
        # Check that neighbors are within one cell distance
        assert abs(cell.row - center.row) <= 1
        assert abs(cell.col - center.col) <= 1
        # Check that we don't get the center cell itself
        assert not (cell.row == center.row and cell.col == center.col)


@pytest.mark.parametrize("dimensions", [
    (3, 4),  # Regular matrix
    (2, 2),  # Small square matrix
    (1, 3),  # Single row matrix
    (3, 1),  # Single column matrix
])
def test_matrix_dimensions(dimensions):
    """Test that the method works with different matrix dimensions."""
    height, width = dimensions
    m = ScreenMatrix(width=width, height=height)

    # Fill matrix with cells
    for row in range(height):
        for col in range(width):
            m.table[row, col] = Cell(m, row=row, col=col)

            cell = m.table[row, col]
            neighbors = m.around_cells(cell)

            # Special cases for 1xN or Nx1 matrices
            if width == 1:  # Single column
                if row == 0 or row == height - 1:  # Top or bottom
                    expected_count = 1
                else:  # Middle
                    expected_count = 2
            elif height == 1:  # Single row
                if col == 0 or col == width - 1:  # Ends
                    expected_count = 1
                else:  # Middle
                    expected_count = 2
            else:  # Regular matrix (width > 1 and height > 1)
                is_top = (row == 0)
                is_bottom = (row == height - 1)
                is_left = (col == 0)
                is_right = (col == width - 1)

                # Corner cases: 3 neighbors
                if (is_top or is_bottom) and (is_left or is_right):
                    expected_count = 3
                # Edge cases (but not corner): 5 neighbors
                elif is_top or is_bottom or is_left or is_right:
                    expected_count = 5
                # Center cases: 8 neighbors
                else:
                    expected_count = 8

            assert len(neighbors) == expected_count, \
                f"Cell at ({row}, {col}) in {height}x{width} matrix should have {expected_count} neighbors"
