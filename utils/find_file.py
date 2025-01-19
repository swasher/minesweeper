from pathlib import Path


def find_file(filename, start_dir=None):
    """
    Рекурсивно ищет файл, начиная с текущей директории и поднимаясь вверх.

    :param filename: Имя файла, который нужно найти.
    :param start_dir: Директория, с которой начинать поиск (по умолчанию — текущая директория).
    :return: Абсолютный путь к файлу, если он найден, иначе None.
    """
    if start_dir is None:
        start_dir = Path.cwd()  # Начинаем с текущей директории

    current_dir = Path(start_dir)

    while True:
        # Проверяем, существует ли файл в текущей директории
        file_path = current_dir / filename
        if file_path.is_file():
            return file_path.resolve()  # Возвращаем абсолютный путь к файлу

        # Переходим на уровень выше
        parent_dir = current_dir.parent

        # Если достигли корневой директории, прекращаем поиск
        if parent_dir == current_dir:
            break

        current_dir = parent_dir

    return None  # Файл не найден