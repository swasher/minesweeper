"""
контурный анализ.
производится оконтруривание, а потом подсчет контуров.
Для данной цели (LED цифры) не подошло, но для других целей может сгодиться.

"""

import cv2
import numpy as np
import numpy.typing as npt
from typing import Sequence, Tuple, Union


def search_pattern_in_image_universal_countur(
    pattern: npt.NDArray,
    image: Union[npt.NDArray, str, None] = None,
    threshold: float = 0.9,
    method: int = cv2.TM_CCOEFF_NORMED
) -> Tuple[Sequence[int], float]:
    """
    Поиск ОДНОГО вхождения шаблона в изображении без использования склеивания найденных изображений.
    Автоматически конвертирует цветные изображения в черно-белые.
    Возвращает координаты верхнего левого угла совпадения и степень сходства.

    Parameters:
        pattern (npt.NDArray): Шаблон (цветной или черно-белый массив изображения).
        image (npt.NDArray | str | None): Исходное изображение (цветной или черно-белый массив изображения). Может принимать значения:
          - None: поиск по всему экрану
          - NDArray: поиск в предоставленном изображении
          - str: если строка представляет собой путь к существующему файлу, изображение загружается из файла
        threshold (float): Пороговое значение для фильтрации совпадений.
        method (int): Метод сравнения шаблона и изображения (по умолчанию cv2.TM_CCOEFF_NORMED).

    Returns:
        point(x, y): Координаты верхнего левого угла совпадения.
        similarity: Степень сходства найденного изображения (1 = 100%)
    """
    # Если изображение не предоставлено, используем весь экран (не реализовано в этом примере)
    if image is None:
        raise ValueError("Поиск по всему экрану не реализован в этом примере.")

    # Если изображение передано как строка (путь к файлу), загружаем его
    if isinstance(image, str):
        image = cv2.imread(image, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError(f"Не удалось загрузить изображение из файла: {image}")

    # Конвертируем изображение и шаблон в черно-белые, если они цветные
    if len(image.shape) == 3:
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        image_gray = image

    if len(pattern.shape) == 3:
        pattern_gray = cv2.cvtColor(pattern, cv2.COLOR_BGR2GRAY)
    else:
        pattern_gray = pattern

    # Применяем шаблонное сопоставление
    result = cv2.matchTemplate(image_gray, pattern_gray, method)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    # Если степень сходства ниже порога, возвращаем None
    if max_val < threshold:
        return None, max_val

    # Возвращаем координаты и степень сходства
    return max_loc, max_val


def recognize_led_digit(image: npt.NDArray) -> str:
    """
    Распознавание LED-цифры на изображении с использованием контурного анализа.

    Parameters:
        image (npt.NDArray): Изображение с LED-цифрой.

    Returns:
        str: Распознанная цифра.
    """
    # Преобразуем изображение в градации серого
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Применяем пороговую обработку
    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)

    # Морфологические операции для улучшения качества
    kernel = np.ones((3, 3), np.uint8)
    processed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

    # Поиск контуров
    contours, _ = cv2.findContours(processed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Фильтрация контуров по площади (убираем слишком маленькие контуры)
    min_area = 100  # Минимальная площадь контура
    filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]

    # Определение цифры на основе контуров
    def recognize_digit(contours):
        # Пример простого анализа: считаем количество контуров
        # (Этот метод нужно адаптировать под ваши LED-цифры)
        num_segments = len(contours)
        if num_segments == 2:
            return "1"
        elif num_segments == 5:
            return "3"
        # Добавьте другие условия для остальных цифр
        else:
            return "Unknown"

    return recognize_digit(filtered_contours)


# Пример использования
if __name__ == "__main__":
    # Загрузка изображения и шаблона
    pattern = cv2.imread('../assets/asset_24_1920x1080/LED_0.png')
    image = cv2.imread('../led_of_msonline.png')

    # Поиск шаблона в изображении
    location, similarity = search_pattern_in_image_universal_countur(pattern, image)
    if location:
        print(f"Шаблон найден в координатах: {location}, сходство: {similarity:.2f}")

        # Вырезаем область с найденным шаблоном
        x, y = location
        h, w = pattern.shape[:2]
        digit_region = image[y:y+h, x:x+w]

        # Распознаем цифру в вырезанной области
        digit = recognize_led_digit(digit_region)
        print(f"Распознанная цифра: {digit}")
    else:
        print("Шаблон не найден.")