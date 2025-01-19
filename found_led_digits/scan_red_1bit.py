import cv2
import numpy as np
import numpy.typing as npt
from typing import Sequence, Tuple, Union
from assets import *
from utils import find_file
from .util import capture_full_screen
from config import config


def extract_red(image: npt.NDArray) -> npt.NDArray:
    """
    Выделяем RED пиксели и близкие к ним, остальные удаляем.

    Parameters:
        image (npt.NDArray): Исходное изображение (BGR).

    Returns:
        npt.NDArray: Бинарная маска (1-bit изображение).
    """
    # Определение диапазона для красного цвета в BGR
    lower_bound = np.array([0, 0, 200])  # Нижняя граница (близкие к красному)
    upper_bound = np.array([50, 50, 255])  # Верхняя граница (чистый красный)
    # Создание маски
    mask = cv2.inRange(image, lower_bound, upper_bound)
    # Применение маски к изображению
    result = cv2.bitwise_and(image, image, mask=mask)

    return result


def apply_1bit(image: npt.NDArray) -> npt.NDArray:
    """
    Создает маску для выделения пикселей с цветом RGB (255, 0, 0).

    Parameters:
        image (npt.NDArray): Исходное изображение (BGR).

    Returns:
        npt.NDArray: Бинарная маска (1-bit изображение).
    """
    # Определяем цвет RGB (255, 0, 0) в формате BGR (OpenCV использует BGR)
    target_color = np.array([0, 0, 255])  # BGR: (0, 0, 255) = RGB: (255, 0, 0)
    # Создаем маску, где пиксели с целевым цветом будут белыми (255), остальные — черными (0)
    mask = cv2.inRange(image, target_color, target_color)
    return mask


def apply_smooth(image: npt.NDArray) -> npt.NDArray:
    smooth = cv2.GaussianBlur(image, (3, 3), 0)
    division = cv2.divide(image, smooth, scale=255)
    return division


def unsharp_mask(image, kernel_size=(5, 5), sigma=1.0, amount=1.0, threshold=0):
    """Return a sharpened version of the image, using an unsharp mask."""
    blurred = cv2.GaussianBlur(image, kernel_size, sigma)
    sharpened = float(amount + 1) * image - float(amount) * blurred
    sharpened = np.maximum(sharpened, np.zeros(sharpened.shape))
    sharpened = np.minimum(sharpened, 255 * np.ones(sharpened.shape))
    sharpened = sharpened.round().astype(np.uint8)
    if threshold > 0:
        low_contrast_mask = np.absolute(image - blurred) < threshold
        np.copyto(sharpened, image, where=low_contrast_mask)
    return sharpened


def search_pattern_in_image_1bit(
    pattern: npt.NDArray,
    image: Union[npt.NDArray, str, None] = None,
    threshold: float = 0.9,
    method: int = cv2.TM_CCOEFF_NORMED
) -> Tuple[Sequence[int], float]:
    """
    Поиск ОДНОГО вхождения шаблона в изображении с использованием 1-bit масок.
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
    match image:
        case None:
            # Image is None, take screenshot
            image = capture_full_screen()
        case str():
            # Image is a string, read from file
            if image_path := find_file(image):
                image = cv2.imread(image_path)
        case np.ndarray():
            # Image is a numpy array.
            pass
        case _:
            raise ValueError("Image is Unknown type")

    # выделяем красный и почти красный
    image_red = extract_red(image)
    pattern_red = extract_red(pattern)

    image_red_unsharp = unsharp_mask(image_red)
    pattern_red_unsharp = unsharp_mask(pattern_red)

    # # Создаем 1-bit маски для изображения и шаблона
    # image_mask = apply_1bit(image_red_unsharp)
    # pattern_mask = apply_1bit(pattern_red_unsharp)

    # Применяем шаблонное сопоставление
    result = cv2.matchTemplate(image_red_unsharp, pattern_red_unsharp, method)

    # Вариант из учебника
    # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
        location = min_loc
        similarity = min_val
    else:
        location = max_loc
        similarity = max_val



    # # DEBUG; YOU CAN SEE WHAT GRABBING
    # # draw at each cell it's row and column number
    if True:
        #
        # == Написать текст ==
        #
        # cv.putText(image, str(x), (y + 11, x + 5), cv.FONT_HERSHEY_SIMPLEX, 0.3, 255)

        #
        # == Нарисовать прямоугольник ==
        #
        template_height, template_width = pattern.shape[:2]  # Размеры шаблона
        top_left = max_loc  # Левый верхний угол прямоугольника
        bottom_right = (top_left[0] + template_width, top_left[1] + template_height)  # Правый нижний угол
        cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 1)

        cv2.imwrite('grabbed.png', image)  # сохраняем в файл
        cv2.imshow("Display window", image)  # показываем юзеру картинку
        k = cv2.waitKey(0)  # и ждем нажатия кнопки

    # Возвращаем координаты и степень сходства
    return location, similarity


# Пример использования
if __name__ == "__main__":
    # method = cv2.TM_CCOEFF
    method = cv2.TM_CCOEFF_NORMED  # ++
    # method = cv2.TM_CCORR
    # method = cv2.TM_CCORR_NORMED  # ++
    # method = cv2.TM_SQDIFF
    # method = cv2.TM_SQDIFF_NORMED

    patterns = [led0, led1, led2, led3, led4, led5, led6, led7, led8, led9]
    test_game = config.asset
    if test_game == 'asset_24_1920x1080':
        img = 'led_of_msonline.png'
        patterns_in_pic = [led0, led1, led2, led3, led8, led9]
    elif test_game == 'asset_vienna':
        img = 'led_of_vienna.png'
        patterns_in_pic = [led0, led1, led2, led3, led9]

    for led in patterns:
        location, similarity = search_pattern_in_image_1bit(pattern=led.raster, image=img, method=method)
        # print('Location:', location)
        is_pattern_in_image = '+' if led in patterns_in_pic else '-'
        print(f'{led.name} {is_pattern_in_image} Sim: {similarity:.2f}', location)
