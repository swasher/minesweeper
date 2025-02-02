"""
Mostly created by gpt-chat ))
"""
import cv2
import numpy as np
from assets import led_digits
from utils import find_file
from .util import capture_full_screen

def upscale_image(image):
    """
    Увеличивает изображение в три раза.

    :param image: Исходное изображение.
    :return: Увеличенное изображение.
    """
    # Увеличиваем изображение в 2 раза
    upscaled_image = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    return upscaled_image


def align_to_template(image, target_size, alignment='center'):
    """
    Центрирует изображение по горизонтали или выравнивает его влево/вправо,
    добавляя отступы для достижения заданного размера.

    :param image: Входное изображение (ROI).
    :param target_size: Целевой размер (ширина, высота).
    :param alignment: Выравнивание ('center', 'left', 'right').
    :return: Изображение с заданным выравниванием.
    """
    target_width, target_height = target_size
    height, width = image.shape[:2]

    # Масштабируем изображение с сохранением пропорций
    scale = min(target_width / width, target_height / height)
    new_width = int(width * scale)
    new_height = int(height * scale)
    resized = cv2.resize(image, (new_width, new_height))

    # Вычисляем отступы
    if alignment == 'center':
        left = (target_width - new_width) // 2
        right = target_width - new_width - left
    elif alignment == 'right':
        left = target_width - new_width
        right = 0
    elif alignment == 'left':
        left = 0
        right = target_width - new_width
    else:
        raise ValueError("alignment должен быть 'center', 'left' или 'right'")

    top = (target_height - new_height) // 2
    bottom = target_height - new_height - top

    # Добавляем отступы
    padded = cv2.copyMakeBorder(resized, top, bottom, left, right, cv2.BORDER_CONSTANT, value=1)
    return padded


def resize_with_padding(image, target_size):
    """
    Масштабирует изображение с сохранением пропорций и добавляет отступы, чтобы довести его до нужного размера.

    :param image: Входное изображение (ROI).
    :param target_size: Целевой размер (ширина, высота).
    :return: Изображение с добавленными отступами.
    """
    target_width, target_height = target_size
    height, width = image.shape[:2]

    # Вычисление коэффициента масштабирования
    scale = min(target_width / width, target_height / height)
    new_width = int(width * scale)
    new_height = int(height * scale)

    # Масштабирование изображения
    resized = cv2.resize(image, (new_width, new_height))

    # Вычисление отступов для дополнения
    top = (target_height - new_height) // 2
    bottom = target_height - new_height - top
    left = (target_width - new_width) // 2
    right = target_width - new_width - left

    # Добавление отступов
    padded = cv2.copyMakeBorder(resized, top, bottom, left, right, cv2.BORDER_CONSTANT, value=30)
    return padded


def image_processing(image, ksize=(3, 5)):
    # Преобразование в оттенки серого и выделение красных объектов
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([179, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(mask1, mask2)

    # # Объеденение сегментов LED-цифр с помощью морфологических операций
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, ksize)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel)

    return red_mask


def recognize_led_digits(image_source, digit_count: int = None) -> str:
    """
    Распознаёт трёхзначное число из красных семисегментных LED-цифр на изображении.

    Args:
        image (npt.NDArray | str | None): Исходное изображение (цветной или черно-белый массив изображения). Может принимать значения:
          - None: поиск по всему экрану
          - NDArray: поиск в предоставленном изображении
          - str: если строка представляет собой путь к существующему файлу, изображение загружается из файла
        digit_count: Предпологаемое количество цифр, которое должно быть найдено. Напр., в кол-ве мин всегда 3.

    Returns:
        return: Строка из digit_count (если был задан) символов, представляющая распознанное число.
    """
    # todo сделать отдельную функцию в общем util типа universal_image_source()
    match image_source:
        case None:
            # Image is None -> take screenshot
            image = capture_full_screen()
        case str():
            # Image is a string -> read from file
            if image_path := find_file(image_source):
                image = cv2.imread(image_path)
        case np.ndarray():
            # Image is a numpy array.
            image = image_source
        case _:
            raise ValueError("Image is Unknown type")

    if image is None:
        raise ValueError("Не удалось загрузить изображение")

    upscaled_image = upscale_image(image)
    red_mask = image_processing(upscaled_image)

    # Выделение контуров
    contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


    # # отображение найденный контуров
    # output_image = cv2.cvtColor(red_mask, cv2.COLOR_GRAY2BGR)
    # # Нарисуйте контуры на изображении
    # cv2.drawContours(output_image, contours, -1, (0, 255, 0), 1)  # Зеленый цвет, толщина 2
    # # Отобразите изображение с контурами
    # cv2.imshow('Contours', output_image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()


    # Отбор контуров и сортировка по x-координате
    digit_rois = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / float(h)
        if 0.1 < aspect_ratio < 0.7 and h > 10:  # Фильтр на форму и размер
            digit_rois.append((x, y, w, h))
    digit_rois = sorted(digit_rois, key=lambda roi: roi[0])  # Сортировка по x-координате

    # Если предоставлен digit_count, то должно быть обнаружено именно такое кол-во цифр
    if digit_count and len(digit_rois) != digit_count:
        raise ValueError(f"Не удалось корректно выделить нужное кол-во цифр: {digit_count}")

    # Распознавание цифр
    result = ""
    for x, y, w, h in digit_rois:
        digit_roi = red_mask[y:y + h, x:x + w]
        """
        Тут вместо (40, 80) можно использовать led0.raster.shape[::-1]
        """

        # Масштабируем ROI с сохранением пропорций и выравниванием
        alignment = 'right' if w / h < 0.3 else 'center'  # Узкие цифры, как 1, выравниваем вправо
        digit_roi_resized = align_to_template(digit_roi, (40, 80), alignment)
        # digit_roi_resized = resize_with_padding(digit_roi, (40, 80))  # Нормализация размера для шаблонов

        # Убедимся, что шаблоны и ROI имеют одинаковое количество каналов
        # if len(led_patterns['0'].shape) == 3:
        #     digit_roi_resized = cv2.cvtColor(digit_roi_resized, cv2.COLOR_GRAY2BGR)  # Преобразование в трёхканальный
        # else:
        #     digit_roi_resized = cv2.cvtColor(digit_roi_resized, cv2.COLOR_BGR2GRAY)  # Преобразование в одноканальный

        # Сравнение с шаблонами
        best_match = None
        best_score = float("-1")
        for digit in led_digits:
            pattern = digit.raster
            pattern_ensize = upscale_image(pattern)
            pattern_processed = image_processing(pattern_ensize)
            pattern_desized = align_to_template(pattern_processed, (40, 80))

            score = cv2.matchTemplate(digit_roi_resized, pattern_desized, cv2.TM_CCOEFF_NORMED).max()
            if score > best_score:
                best_score = score
                best_match = str(digit.value)

        if __name__ == "__main__":
            print(f'Score: {best_score:.2f} (seems to confirm with {best_match} digit)')

        if best_score < 0.6:  # Если корреляция ниже порога, игнорируем результат
            raise ValueError("Слишком низкая корреляция для одной из цифр:", best_score)

        if best_match is None:
            raise ValueError("Не удалось распознать одну из цифр")

        result += best_match

    return result


if __name__ == "__main__":
    # samples = ['led_mso_1.png', 'led_mso_2.png', 'led_mso_3.png', 'led_mso_4.png', 'led_mso_5.png']
    # answers = ['098', '006', '107', '366', '392']
    samples = ['sample/full_set.png']
    answers = ['000412056078093']

    for filename, answer in zip(samples, answers):
        result = recognize_led_digits(filename)
        recognize_eval = 'OK' if answer == result else 'BAD'
        print(f"{answer} FOUND: {result} ={recognize_eval}")


__all__ = ['recognize_led_digits']