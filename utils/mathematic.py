import random
import numpy as np
from .classes import Point


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
    return Point(xx, yy)


def random_point_in_circle(x: int, y: int, r: int) -> Point:
    """Generate a random integer point within a circle.

    This function generates a random point inside a circle defined by its center
    coordinates (x, y) and radius R. The point is uniformly distributed within the circle.

    Args:
        x (int): The x-coordinate of the center of the circle.
        y (int): The y-coordinate of the center of the circle.
        r (int): The radius of the circle.

    Returns:
        tuple[int, int]: A tuple containing the integer x and y coordinates of the random point.
    """
    # Generate a random radius
    r = int(r * np.sqrt(np.random.rand()))  # Scale by sqrt for uniform distribution
    # Generate a random angle
    theta = np.random.uniform(0, 2 * np.pi)

    # Calculate the coordinates of the point
    x_random = int(x + r * np.cos(theta))
    y_random = int(y + r * np.sin(theta))

    return Point(x_random, y_random)


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
