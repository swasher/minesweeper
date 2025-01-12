import pytest
import numpy as np
from classes import PlayMatrix
from classes import Cell
from asset import asset
from config import config


@pytest.fixture
def matrix():
    """Creates a 3x3 matrix for testing display functionality."""
    m = PlayMatrix()
    m.initialize(width=3, height=3)
    
    # Fill matrix with closed cells
    for row in range(3):
        for col in range(3):
            m.table[row, col] = Cell(m, row=row, col=col)
            m.table[row, col].content = asset.closed
    return m


def test_all_closed(matrix, capsys):
    """Test display with all cells closed."""
    matrix_view = matrix.display()
    captured = capsys.readouterr()
    
    # Check console output
    assert "---DISPLAY---" in captured.out
    
    # Check returned matrix view
    assert len(matrix_view) == 3  # 3 rows
    assert all(len(row.split()) == 3 for row in matrix_view)  # 3 columns
    assert all(cell == asset.closed.symbol for row in matrix_view for cell in row.split())


def test_mixed_cells(matrix, capsys):
    """Test display with mix of different cell contents."""
    # Set up different cell contents
    matrix.table[0, 0].content = asset.n1  # Open with 1 mine
    matrix.table[0, 1].content = asset.flag  # Flag
    matrix.table[1, 1].content = asset.n0  # Empty cell
    
    matrix_view = matrix.display()
    captured = capsys.readouterr()
    
    # Check console output exists
    assert "---DISPLAY---" in captured.out
    
    # Verify first row content
    first_row = matrix_view[0].split()
    assert first_row[0] == asset.n1.symbol  # "1"
    assert first_row[1] == asset.flag.symbol  # Flag symbol


def test_with_mines(matrix, capsys):
    """Test display with mines on the board."""
    if not config.tk:
        pytest.skip("Skipping test because config.tk is False")

    # Add mines to specific positions
    matrix.mines.add((0, 0))
    matrix.mines.add((1, 1))
    
    matrix_view = matrix.display()
    captured = capsys.readouterr()
    
    # Check that mines are displayed correctly when cell is closed
    first_row = matrix_view[0].split()
    assert first_row[0] == asset.there_is_bomb.symbol
    
    # Add a flag over a mine
    matrix.table[0, 0].content = asset.flag
    matrix_view = matrix.display()
    
    # Mine should not be visible when flagged
    first_row = matrix_view[0].split()
    assert first_row[0] == asset.flag.symbol


# def test_empty_matrix():
#     """Test display with empty/zero-sized matrix."""
#     empty_matrix = PlayMatrix()
#     empty_matrix.initialize(width=0, height=0)
#
#     matrix_view = empty_matrix.display()
#     assert len(matrix_view) == 0


def test_single_cell(capsys):
    """Test display with 1x1 matrix."""
    tiny_matrix = PlayMatrix()
    tiny_matrix.initialize(width=1, height=1)
    tiny_matrix.table[0, 0] = Cell(tiny_matrix, row=0, col=0)
    tiny_matrix.table[0, 0].content = asset.closed
    
    matrix_view = tiny_matrix.display()
    captured = capsys.readouterr()
    
    assert len(matrix_view) == 1
    assert len(matrix_view[0].split()) == 1
    assert matrix_view[0].split()[0] == asset.closed.symbol


def test_rectangular_matrix(capsys):
    """Test display with non-square matrix."""
    rect_matrix = PlayMatrix()
    rect_matrix.initialize(width=2, height=3)
    
    # Fill with closed cells
    for row in range(3):
        for col in range(2):
            rect_matrix.table[row, col] = Cell(rect_matrix, row=row, col=col)
            rect_matrix.table[row, col].content = asset.closed
    
    matrix_view = rect_matrix.display()
    captured = capsys.readouterr()
    
    assert len(matrix_view) == 3  # 3 rows
    assert all(len(row.split()) == 2 for row in matrix_view)  # 2 columns


def test_all_cell_contents(matrix, capsys):
    """Test display with all possible cell contents."""
    # Set up one of each possible cell content
    contents = [
        (0, 0, asset.closed),
        (0, 1, asset.flag),
        (0, 2, asset.open_cells[0]),
        (1, 0, asset.open_cells[1]),
        (1, 1, asset.open_cells[2]),
        (1, 2, asset.bomb),
    ]
    
    for row, col, content in contents:
        matrix.table[row, col].content = content
    
    matrix_view = matrix.display()
    captured = capsys.readouterr()
    
    # Verify each cell's display symbol
    for row, col, content in contents:
        displayed_symbol = matrix_view[row].split()[col]
        assert displayed_symbol == content.symbol
