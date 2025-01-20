import sys
from config import config
from core.screen import ScreenMatrix
from core.screen import find_board
from screen_controller import capture_full_screen


def check_minesweeper_field():
    """
    Проверяем корректность заданных полей в setting.ini, а так же расположение смайла.
    """
    col_values, row_values, region = find_board()
    matrix = ScreenMatrix(row_values, col_values, region)

    s = capture_full_screen()
    x1, x2, y1, y2 = matrix.region_x1, matrix.region_x2, matrix.region_y1, matrix.region_y2
    import cv2
    cv2.rectangle(s, (x1, y1), (x2, y2), (0, 255, 0), 1)
    smile_x = int(x1 + (x2 - x1)/2)
    smile_y = int(y1 + config.top/2)
    cv2.circle(s, (smile_x, smile_y), radius=10, color=(0, 0, 255), thickness=2)
    cv2.imshow("Screenshot with Rectangle", s)
    cv2.waitKey(0)  # Ожидание нажатия клавиши
    cv2.destroyAllWindows()

def function2():
    """Executes function2."""
    print("Function 2 is executed.")

def function3():
    """Executes function3."""
    print("Function 3 is executed.")


if __name__ == "__main__":
    # Получаем функцию по имени из глобального пространства имен
    func = globals().get(sys.argv[1])

    if callable(func):  # Проверяем, что это действительно функция
        func()  # Вызываем соответствующую функцию
    else:
        print("Invalid parameter. Please use function name as parameter.")
