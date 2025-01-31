class InvalidCharacterError(Exception):
    """Исключение для обработки недопустимых символов при преобразовании текста моей матрицы в символы minesweepr"""
    pass


class BoardNotFound(Exception):
    """Исключение, если на экране не обнаружен Mineseweeper"""
    print("Board not founded.")
