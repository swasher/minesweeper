"""
Пороговая обработка (Thresholding)
----------------------------------

После применения функции cv.matchTemplate, вы получаете карту совпадений (result), где каждому пикселю соответствует значение, указывающее, насколько хорошо шаблон совпадает с этой областью изображения. Эти значения обычно нормализованы в диапазоне от 0 до 1 (если используется метод сравнения, такой как cv.TM_CCOEFF_NORMED).

Зачем нужна пороговая обработка?

Карта совпадений может содержать много "шума" — областей с низкими значениями совпадения, которые не представляют интереса.

Пороговая обработка позволяет выделить только те области, где совпадение достаточно сильное.

Как это работает:

Вы задаете пороговое значение (например, 0.9), которое определяет, какие значения на карте совпадений считать значимыми.

Все значения ниже порога отбрасываются, а значения выше порога сохраняются.


Немаксимальное подавление (Non-Maximum Suppression, NMS)
--------------------------------------------------------

После пороговой обработки у вас могут остаться несколько областей, которые соответствуют шаблону. Однако эти области могут перекрываться, что приводит к дублированию результатов.

Зачем нужно NMS?

NMS помогает выбрать только одно наилучшее совпадение в области, устраняя дубликаты.

Это особенно полезно, если шаблон встречается на изображении несколько раз, и вы хотите выделить только наиболее значимые совпадения.

Как это работает:

Вы находите все области, которые превышают порог.

Для каждой области вы вычисляете "счет уверенности" (например, значение из карты совпадений).

Если области перекрываются, вы оставляете только ту, у которой счет уверенности выше, а остальные подавляете.
"""
from typing import Sequence

import cv2 as cv
import numpy as np
import numpy.typing as npt

from .util import capture_full_screen
from utils import find_file


def non_max_suppression(boxes, scores, threshold):
    # Реализация NMS
    if len(boxes) == 0:
        return []

    # Координаты bounding box'ов
    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]

    # Вычисление площадей
    areas = (x2 - x1 + 1) * (y2 - y1 + 1)
    order = scores.argsort()[::-1]  # Сортировка по убыванию уверенности

    keep = []
    while order.size > 0:
        i = order[0]
        keep.append(i)
        # Вычисление пересечений
        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])

        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)
        overlap = (w * h) / areas[order[1:]]

        # Удаление box'ов с большим перекрытием
        inds = np.where(overlap <= threshold)[0]
        order = order[inds + 1]

    return keep


def search_pattern_in_image_NMS(
    pattern: npt.NDArray,
    image: npt.NDArray | str = None,
    threshold: float = 0.9,
    method: int = cv.TM_CCOEFF_NORMED
) -> tuple[Sequence[int], float]:

    match image:
        case None:
            # Image is None, take screenshot
            image = capture_full_screen()
        case str():
            # Image is a string, read from file
            if image_path := find_file(image):
                image = cv.imread(image_path)
        case np.ndarray():
            # Image is a numpy array.
            pass
        case _:
            raise ValueError("Image is Unknown type")

    # Загрузка изображения и шаблона
    h, w = pattern.shape[:2]

    # Применение matchTemplate
    result = cv.matchTemplate(image, pattern, method)
    threshold = 0.9
    loc = np.where(result >= threshold)

    # Создание bounding box'ов
    boxes = []
    similarities = []
    for pt in zip(*loc[::-1]):
        boxes.append([pt[0], pt[1], pt[0] + w, pt[1] + h])
        similarities.append(result[pt[1], pt[0]])  # Извлечение степени совпадения

    # Применение NMS
    boxes = np.array(boxes)
    scores = result[loc]
    keep = non_max_suppression(boxes, scores, 0.5)

    # Отображение результатов
    for i in keep:
        cv.rectangle(image, (boxes[i][0], boxes[i][1]), (boxes[i][2], boxes[i][3]), (0, 255, 0), 1)
        # Вывод степени совпадения
        similarity = similarities[i]
        text = f"Similarity: {similarity:.2f}"
        cv.putText(image, text, (boxes[i][0], boxes[i][1] - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    cv.imshow('Result', image)
    cv.waitKey(0)
    cv.destroyAllWindows()

    return loc, scores