from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from solver.classes import Turn


def remove_dup(arr):
    """
    Remove dublicates from array of object.
    :return: array of objects
    """
    unique = list(set(arr))
    return unique


def remove_duplicated_turns(turns: list[Turn]) -> list[Turn]:
    """
    Удаляет дубликаты из списка объектов Turn.

    Дубликатами считаются объекты, у которых одинаковые значения
    cell.col и cell.row.

    Args:
        turns (List[Turn]): Список объектов Turn, из которого нужно удалить дубликаты.

    Returns:
        List[Turn]: Список уникальных объектов Turn без дубликатов.
    """
    seen = set()
    unique_turns = []

    for turn in turns:
        # Создаем уникальный идентификатор для каждого Turn на основе cell.col и cell.row
        identifier = (turn.cell.col, turn.cell.row)

        if identifier not in seen:
            seen.add(identifier)
            unique_turns.append(turn)

    return unique_turns
