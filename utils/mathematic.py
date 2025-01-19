import random


def random_point_in_square(x, y, w, h):
    """
    x, y - координаты левого верхнего угла в пикселях
    w, h - ширина и высота прямоугольника
    :return: Случайную точку в этом прямоугольнике, с учетом безопасных полей.
    """
    safe_x, safe_y = int(w*0.2), int(h*0.2)

    x1, x2 = x + safe_x, x + w - safe_x
    y1, y2 = y + safe_y, y + h - safe_y
    xx = random.randint(x1, x2)
    yy = random.randint(y1, y2)
    return xx, yy


def point_in_rect(point: tuple[int, int],
                  x1: int, y1: int,
                  w: int, h: int) -> bool:
    """
    Проверяет, находится ли точка внутри прямоугольника.

    Args:
        point (Tuple[int, int]): Координаты точки (x, y).
        x1 (int): X-координата левого верхнего угла прямоугольника.
        y1 (int): Y-координата левого верхнего угла прямоугольника.
        w (int): Ширина прямоугольника.
        h (int): Высота прямоугольника.

    Returns:
        bool: True, если точка находится внутри прямоугольника, иначе False.
    """
    # Вычисляем координаты правого нижнего угла прямоугольника
    x2, y2 = x1 + w, y1 + h

    # Извлекаем координаты точки
    x, y = point

    # Проверяем, находится ли точка внутри прямоугольника
    return (x1 < x < x2) and (y1 < y < y2)
