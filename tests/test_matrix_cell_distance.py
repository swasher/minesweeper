import pytest
import math

from classes import SolveMatrix
from classes import Cell


@pytest.fixture
def matrix():
    """Create a 3x4 matrix with unique cells for testing."""
    m = SolveMatrix(width=4, height=3)
    for row in range(3):
        for col in range(4):
            m.table[row, col] = Cell(m, row=row, col=col)
    return m


@pytest.fixture
def cells(matrix):
    """Fixture создает набор ячеек для тестирования."""
    return {
        'center': Cell(matrix, row=1, col=1),
        'same': Cell(matrix, row=1, col=1),
        'right': Cell(matrix, row=1, col=2),
        'diagonal': Cell(matrix, row=2, col=2),
        'far': Cell(matrix, row=4, col=5),
        'negative': Cell(matrix, row=-1, col=-1)
    }


def test_same_cell(cells):
    """Тест расстояния между одной и той же ячейкой (должно быть 0)."""
    distance = SolveMatrix.cell_distance(cells['center'], cells['same'])
    assert distance == 0.0


def test_horizontal_distance(cells):
    """Тест расстояния между горизонтально расположенными ячейками."""
    distance = SolveMatrix.cell_distance(cells['center'], cells['right'])
    assert distance == 1.0


@pytest.mark.parametrize("cell1_pos,cell2_pos,expected", [
    ((0, 0), (0, 3), 3.0),  # горизонтально
    ((0, 0), (3, 0), 3.0),  # вертикально
    ((0, 0), (3, 4), 5.0),  # случай 3-4-5 треугольника
])
def test_various_distances(matrix, cell1_pos, cell2_pos, expected):
    """Тест различных расстояний между ячейками."""
    cell1 = Cell(matrix, row=cell1_pos[0], col=cell1_pos[1])
    cell2 = Cell(matrix, row=cell2_pos[0], col=cell2_pos[1])
    distance = SolveMatrix.cell_distance(cell1, cell2)
    assert distance == expected


def test_diagonal_distance(cells):
    """Тест расстояния по диагонали (должно быть √2)."""
    distance = SolveMatrix.cell_distance(cells['center'], cells['diagonal'])
    assert math.isclose(distance, math.sqrt(2), rel_tol=1e-9)


def test_negative_coordinates(cells):
    """Тест работы с отрицательными координатами."""
    distance = SolveMatrix.cell_distance(cells['center'], cells['negative'])
    # Расстояние от (1,1) до (-1,-1) должно быть 2√2
    assert math.isclose(distance, 2 * math.sqrt(2), rel_tol=1e-9)


def test_far_distance(cells):
    """Тест расстояния между далеко расположенными ячейками."""
    distance = SolveMatrix.cell_distance(cells['center'], cells['far'])
    expected = math.hypot(4 - 1, 5 - 1)  # от (1,1) до (4,5)
    assert math.isclose(distance, expected, rel_tol=1e-9)


def test_commutative_property(matrix):
    """Тест коммутативности - расстояние A->B должно равняться B->A."""
    cell1 = Cell(matrix, row=1, col=2)
    cell2 = Cell(matrix, row=3, col=5)

    distance_forward = SolveMatrix.cell_distance(cell1, cell2)
    distance_backward = SolveMatrix.cell_distance(cell2, cell1)

    assert math.isclose(distance_forward, distance_backward, rel_tol=1e-9)


@pytest.mark.parametrize("row1,col1,row2,col2", [
    (0, 0, 0, 0),  # одна и та же ячейка
    (0, 1, 0, 2),  # соседние ячейки
    (1, 1, 2, 2),  # диагональ
    (-2, -2, 2, 2),  # через центр поля
    (10, 10, -10, -10),  # большое расстояние
])
def test_positive_distance(matrix, row1, col1, row2, col2):
    """Тест что расстояние всегда положительное."""
    cell1 = Cell(matrix, row=row1, col=col1)
    cell2 = Cell(matrix, row=row2, col=col2)
    distance = SolveMatrix.cell_distance(cell1, cell2)
    assert distance >= 0
