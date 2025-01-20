from dataclasses import dataclass
from core import Cell
from core import Action


@dataclass
class Turn:
    cell: Cell
    action: Action
    solver: str  # Какой тип должен определять солвер? Строка? Или может быть ссылка на функцию?
    difficulty: float | None  # пока не ясно, как реализовать, но смысл в том, что этот параметр показывает сколько бы времени думал человек перед этим решением
    probability: float | None  # рассчитанная вероятность мины
    effectiveness: float | None  # эффективность нажатия (напр., сколько ячеек откроется при нажатии)


class Root(object):
    """
    Used in E2 and B2
    """
    ancestor = None # объект Cell - клетка, для которой строился root
    closed = []     # список объектов Cell
    flags = []      # список объектов Flag
    number = 0      # int, цифра, вокруг которой построен "корень"

    def __init__(self, cell, closed, flags):
        self.ancestor = cell
        self.closed = closed
        self.flags = flags
        self.digit = cell.digit

    def __repr__(self):
        return f'NUMBER: {self.digit} with {len(self.closed)} closed and {len(self.flags)} flags'

    @property
    def len_closed(self):
        return len(self.closed)

    @property
    def rest_bombs(self):
        return self.digit - len(self.flags)


def create_roots(matrix):
    """
    Used in E2 and B2

    Строит "дерево" корней (соседних клеток) для каждой цифры на поле.
    Берутся в учет только те клетки, у которых есть пустые клетки вокруг.
    Для каждой цифры создается объект класса Root, который содержит список закрытых ячеек и список флагов,
    приходящихся на эти ячейки.
    :param matrix:
    :return:
    """
    roots = []
    for cell in matrix.get_digit_cells():
        if len(matrix.around_closed_cells(cell)):
            closed = matrix.around_closed_cells(cell)
            flags = matrix.around_flagged_cells(cell)
            roots.append(Root(cell, closed, flags))
    return roots

