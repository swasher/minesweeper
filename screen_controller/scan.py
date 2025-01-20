import numpy as np
import numpy.typing as npt
import cv2 as cv
from pathlib import Path
import win32gui
from typing import Sequence


from assets import Asset
from .util import compare_images
from .util import capture_full_screen
from utils import find_file


def find_matching_pattern(image: npt.NDArray[np.uint8], patterns: set[Asset]) -> tuple[any, float]:
    """
    Ищет подходящий паттерн для изображения

    Args:
        image: исходное BGR изображение, представленное как ndarray
        patterns: список ассетов для сравнения, в каждом ассете есть asset.raster типа npt.NDArray[np.uint8]

    Returns:
        tuple: (найденный паттерн или None, значение схожести)
    """
    DEFAULT_PRECISION = 0.8

    for pattern in patterns:
        similarity = compare_images(image, pattern.raster)
        pattern.similarity = similarity

        if similarity > DEFAULT_PRECISION:
            return pattern, similarity

        # deprecated
        # был вариант находить для каждого паттерна индекс "похожести" и выбирать наибольший
        # но по сути все совпадения имеют индекс более 0,9999 или 1,0, так что нет смысла заморачиваться
        # best_match = sorted(list_patterns, key=lambda x: x.similarity, reverse=True)[0]
        # print(best_match.similarity)
        # if best_match.similarity > precision:
        #     self.status = best_match.name

    return None, 0.0


def search_pattern_in_image(pattern: npt.NDArray[np.uint8], image: npt.NDArray[np.uint8], precision: float) -> list[tuple[int, int, float]]:
    """
    Сканирует изображение image в поисках шаблона pattern (множественные вхождения).

    Чем меньше значение precision, тем больше "похожих" клеток находит скрипт. При поиске клеток доски:
    При значении 0.6 он вообще зацикливается
    При значении 0.7 он находит closed cell в самых неожиданных местах
    Значение 0.9 выглядит ок, но на экране 2560х1440 находит несколько ячеек
    смещенных на 1 пиксель - это из-за того, что сами ячейки экрана имеют плавающий размер, при этом
    сами ячейки находятся нормально. Увеличение threshold при этом качество результата не увеличивает - смещены сами ячейки на экране.
    В результирующем списке ячейки расположены хаотично,
    поэтому нам нужно разобрать список координат отдельно по X и отдельно по Y, и создать 2D матрицу ячеек.

    ВНИМАНИЕ! Sim в результатах может быть как "чем больше, тем лучше", так и "чем меньше, тем лучше" в зависимости
    от типа сравнения (напр, cv.TM_CCOEFF_NORMED лучше больше)

    Args:
        pattern: образец, который надо найти в image
        image: изображение, например снимок экрана или взятое из файла
        precision: - точность поиска, см. описание

    Returns:
        cells: Список ячеек, в котором каждая ячейка представлена кортежем: (x, y, sim), где:
          x, y - координаты верхнего левого угланайденного прямоугольника, относительно верхнего левого угла экрана,
          sim - значение "похожести"
    """

    h, w = pattern.shape[:2]

    method = cv.TM_CCOEFF_NORMED
    # method = cv.TM_CCORR_NORMED

    res = cv.matchTemplate(image, pattern, method)

    # fake out max_val for first run through loop
    max_val = 1

    cells = []
    # debug - view found cells
    # dc = win32gui.GetDC(0)

    while max_val > precision:
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)

        if max_val > precision:
            res[max_loc[1] - h // 2:max_loc[1] + h // 2 + 1, max_loc[0] - w // 2:max_loc[0] + w // 2 + 1] = 0
            image = cv.rectangle(image, (max_loc[0], max_loc[1]), (max_loc[0] + w + 1, max_loc[1] + h + 1), (0, 255, 0))
            cellule = (max_loc[0], max_loc[1], max_val)
            cells.append(cellule)

            # debug - put digit on found cells
            # cv.putText(image, '1', (max_loc[0]+3, max_loc[1]+10), cv.FONT_HERSHEY_SIMPLEX, 0.3, 255)

            # debug - view found cells
            # x, y = max_loc[0], max_loc[1]
            # win32gui.Rectangle(dc, x + 3, y + 3, x + 8, y + 8)

    # draw at each found cell it's row and column coordinates relatively top-left corner of screen
    SHOW_DETECTED_CELLS = False
    if SHOW_DETECTED_CELLS:
        for c in cells:
            x, y = c[0], c[1]
            # cv.putText(image, str(x), (y + 11, x + 5), cv.FONT_HERSHEY_SIMPLEX, 0.3, 255)
            # cv.putText(image, str(y), (y + 19, x + 5), cv.FONT_HERSHEY_SIMPLEX, 0.3, 255)
            cv.putText(image, str(x), (x + 1, y + 10), cv.QT_FONT_NORMAL, 0.3, 255)
            cv.putText(image, str(y), (x + 1, y + 20), cv.QT_FONT_NORMAL, 0.3, 255)
        cv.imwrite('grabbed.png', image)
        cv.imshow("Display window", image)
        k = cv.waitKey(0)

    return cells


def search_pattern_in_image_for_red_bombs(pattern: npt.NDArray, image: npt.NDArray, precision: float = 0):
    """
    Это немного тюнингованная версия search_pattern_in_image.
    Отличается настройками распознавания, заточенными под большие красные цифры (бомбы).

    Сканирует изображение image в поисках шаблона pattern (множественные вхождения).
    Возвращает два списка row_values и col_values. Начало координат - верх лево.

    Чем меньше значение precision, тем больше "похожих" клеток находит скрипт. При поиске клеток доски:
    При значении 0.6 он вообще зацикливается
    При значении 0.7 он находит closed cell в самых неожиданных местах
    Значение 0.9 выглядит ок, но на экране 2560х1440 находит несколько ячеек
    смещенных на 1 пиксель - это из-за того, что сами ячейки экрана имеют плавающий размер, при этом
    сами ячейки находятся нормально. Увеличение threshold при этом качество результата не увеличивает - смещены сами ячейки на экране.
    В результирующем списке ячейки расположены хаотично,
    поэтому нам нужно разобрать список координат отдельно по X и отдельно по Y, и создать 2D матрицу ячеек.

    :param pattern: образец, который надо найти в image
    :param image: изображение, например снимок экрана или взятое из файла
    :param precision - точность поиска, см. описание

    :return: cells_coord_x - список координаты по оси X для каждого столбца (в пикселях относительно верха лева экрана)
    :return: cells_coord_y - анал. по оси Y
    :rtype:
    """

    h, w = pattern.shape[:2]

    # method = cv.TM_CCOEFF
    method = cv.TM_CCOEFF_NORMED  # ++
    # method = cv.TM_CCORR
    # method = cv.TM_CCORR_NORMED  # ++
    # method = cv.TM_SQDIFF
    # method = cv.TM_SQDIFF_NORMED

    ### precision для TM_CCORR_NORMED, при котором удачно распознаются цифры (mine.online, 1920х1080, size 24)
    # bombs - min pecision - max precision
    # 099 - 0.937 - 0.944
    # 098 - 0.935 - 0.935
    # 098 - 0.931 - 0.944
    # 097 - 0.931 - 0.944
    # 096 - 0.929 - 0.944
    # 095 - 0.929 - 0.944
    # 094 - 0.929 - 0.944
    # 093 - 0.929 - 0.944
    # 092 - 0.929 - 0.944
    # 091 - 0.929 - 0.944
    # 090 - 0.929 - 0.944
    # 089 - 0.937 - 0.947
    # 088 - 0.935 - 0.947
    # 087 - 0.933 - 0.947

    # precision = 0.940
    res = cv.matchTemplate(image, pattern, method)

    # fake out max_val for first run through loop
    max_val = 1

    cells = []
    # debug - view found cells
    dc = win32gui.GetDC(0)

    while max_val > precision:
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)

        if max_val > precision:
            res[max_loc[1] - h // 2:max_loc[1] + h // 2 + 1, max_loc[0] - w // 2:max_loc[0] + w // 2 + 1] = 0
            image = cv.rectangle(image, (max_loc[0], max_loc[1]), (max_loc[0] + w + 1, max_loc[1] + h + 1), (0, 255, 0))
            cellule = (max_loc[0], max_loc[1], max_val)
            cells.append(cellule)

            # debug - put digit on found cells
            # cv.putText(image, '1', (max_loc[0]+3, max_loc[1]+10), cv.FONT_HERSHEY_SIMPLEX, 0.3, 255)

            # debug - view found cells
            # x, y = max_loc[0], max_loc[1]
            # win32gui.Rectangle(dc, x + 3, y + 3, x + 8, y + 8)

    # # DEBUG; YOU CAN SEE WHAT GRABBING
    # # draw at each cell it's row and column number
    # for c in cells:
    #     x = c[1]
    #     y = c[0]
    #     cv.putText(image, str(x), (y + 11, x + 5), cv.FONT_HERSHEY_SIMPLEX, 0.3, 255)
    #     cv.putText(image, str(y), (y + 19, x + 5), cv.FONT_HERSHEY_SIMPLEX, 0.3, 255)
    # # cv.imwrite('output.png', image)
    # cv.imshow("Display window", image)
    # k = cv.waitKey(0)

    return cells



def search_pattern_in_image_universal(
    pattern: npt.NDArray,
    image: npt.NDArray | str = None,
    threshold: float = 0.9,
    method: int = cv.TM_CCOEFF_NORMED
) -> tuple[Sequence[int], float]:
    """
    Поиск ОДНОГО вхождения шаблона в изображении без использования склеивания найденных изображений.
    Автоматически конвертирует цветные изображения в черно-белые.
    Возвращает все совпадения, где точность ниже заданного порога.

    Parameters:
        pattern (npt.NDArray): Шаблон (цветной или черно-белый массив изображения).
        image (npt.NDArray): Исходное изображение (цветной или черно-белый массив изображения). Может принимать значения:
          - None: поиск по всему экрану
          - NDArray: поиск в предоставленном изображении
          - str: если строка представляет собой путь к существующему файлу, изображение загружается из файла
        threshold (float): Пороговое значение для фильтрации совпадений.
        method (int): Метод сравнения шаблона и изображения (по умолчанию cv.TM_CCOEFF_NORMED).

    Returns:
        point(x, y): Список координат верхнего левого угла совпадений.
        similarity: Степерь сходства найденного изображения (1 = 100%)
    """

    """
    Тестирование:
    
    cv.TM_CCOEFF 
    ===================
        
    ### Vienna
    
    ### MSOnline
    
    cv.TM_CCOEFF_NORMED 
    ===================
    
    ### Vienna
    
    LED0-LED9
    Уверенно находит, sim=0.99-1. При отсутствии нужной цифры, выдает неправильный результат с sim~0.7-0.9 

    ### MSOnline
    
    LED0-LED9
    Sim гораздо меньше про обнаружении, и маленькая разница между ними:
          Обнаружение     Цифры нет, выдача ложная
    LED0  0.89 
    LED1  0.93             0.83
    LED2  0.87             0.60
    LED3  0.87             0.79
    LED4  0.93             0.62

    cv.TM_CCORR 
    ===================
        
    ### Vienna
    
    ### MSOnline
    
    
    cv.TM_CCORR_NORMED 
    ===================
        
    ### Vienna
    
    ### MSOnline
        
    cv.TM_SQDIFF 
    ===================
        
    ### Vienna
    
    ### MSOnline
    
    cv.TM_SQDIFF_NORMED 
    ===================
        
    ### Vienna
    
    ### MSOnline


    """

    # Проверка на пустые входные данные
    if pattern is None:
        raise ValueError("Шаблон или изображение не могут быть None")

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

    # # Если изображение, в котором нужно искать, не задано, ищем по всему экрану
    # if image is None:
    #     # image = fullscreen capture
    #     image = capture_full_screen()

    # Конвертация в черно-белый формат, если изображение цветное
    I_WANT_CONVERT_TO_GRAYSCALE = True
    if I_WANT_CONVERT_TO_GRAYSCALE:
        if len(image.shape) == 3:
            image_converted = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        else:
            image_converted = image
        if len(pattern.shape) == 3:
            pattern_converted = cv.cvtColor(pattern, cv.COLOR_BGR2GRAY)
        else:
            pattern_converted = pattern
    else:
        image_converted = image
        pattern_converted = pattern

    # Применяем метод matchTemplate
    result = cv.matchTemplate(image_converted, pattern_converted, method)

    # Нормализуйте результат
    # result_norm = cv.normalize(result, None, 0, 255, cv.NORM_MINMAX, cv.CV_8U)
    # затем можно посмотреть: cv.imshow("Display window", result)  # показываем юзеру картинку

    # Пороговая обработка
    threshold = 0.8
    _, result_thresh = cv.threshold(result, threshold, 1.0, cv.THRESH_BINARY)
    result_thresh = (result_thresh * 255).astype(np.uint8)



    # # Находим все совпадения, которые ниже или выше порога в зависимости от метода
    # if method in [cv.TM_SQDIFF, cv.TM_SQDIFF_NORMED]:
    #     locations = np.where(result > threshold)
    #     locations = list(zip(*locations[::-1]))  # Преобразуем индексы в (x, y)
    # else:
    #     locations = np.where(result < threshold)
    #     locations = list(zip(*locations[::-1]))  # Преобразуем индексы в (x, y)

    # Вариант из учебника
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
    if method in [cv.TM_SQDIFF, cv.TM_SQDIFF_NORMED]:
        location = min_loc
        similarity = min_val
    else:
        location = max_loc
        similarity = max_val

    # # DEBUG; YOU CAN SEE WHAT GRABBING
    # # draw at each cell it's row and column number
    if False:
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
        cv.rectangle(image, top_left, bottom_right, (0, 255, 0), 1)
        cv.imwrite('grabbed.png', image)  # сохраняем в файл
        cv.imshow("Display window", result_thresh)  # показываем юзеру картинку
        k = cv.waitKey(0)  # и ждем нажатия кнопки

    # Возвращаем список координат
    return location, similarity
