"""
Слой абстракции между логикой и конкретной реализацией сапера.

В другие модули нужно импортировать не экземпляр, а сам класс Board, и из него брать
необходимые данные.

Так же предоставляет для других модулей:
- patterns - объект SimpleNamespace со всеми типами ячеек, можно ссылаться как patterns.bomb или patterns.n1
- list_patterns - то же, в виде tuple
- red_digits - tuple с красными буквами часов и счетчика бомб

Каждый итем в списках - экземпляр класса Pattern

---------------

WORK 2560х1440 [Scaling: 1(96dpi), Raw Dpi: 93 (Ratio:1.03)]
масштаб клетка
10      11x11 px (min size)
20      22х23 px
*22     25х25 px (can be 25x24 or even 24x24)
24      27х27 px
28      32х32 px
60      67x67 px (max size)

HOUSE
масштаб клетка
22      22x22 px
*24     24x24 px

"""

import os
import pathlib
import importlib
import cv2 as cv
from types import SimpleNamespace
from config import config


class Asset(object):
    """
    Привязывает растровые изображения ячеек к классу Pattern. Является зависимым от типа сапера.
    """
    # ----
    # WARNING!!!!
    # РАЗМЕР АССЕТОВ НЕ СООТВЕТСТВУЕТ РАЗМЕРУ ЯЧЕЕК - ОНИ КРОПЛЕНЫ В РАЗМЕР ИЗОБРАЖЕНИЯ!!!
    # ТОЛЬКО РАЗМЕР ЯЧЕЙКИ CLOSED ЯВЛЯЕТСЯ РАЗМЕРОМ ЯЧЕЕК В ПИКСЕЛЯХ!!!
    # ПОЭТОМУ ТУТ НЕ МОЖЕТ БЫТЬ СВОЙСТВ ШИРИНА-ВЫСОТА
    # ----

    border = {}  # граница поля сапера в пикселях, от ячеек до края; скриншот каждый раз делается по этой области
    smile_y_coord = 0  # координата Y для клика по смайлу
    name = ''
    filename = ''
    similarity = 0
    raster = ''
    open_digit_action = ''

    def __init__(self, name, filename):
        self.name = name
        self.filename = filename
        self.raster = cv.imread(filename, cv.IMREAD_COLOR)

    def __repr__(self):
        return '<'+self.name+'>'


directory = config.asset
asset = config.asset

# deprecated
# asset_data = importlib.import_module(f'{directory}.asset', package='.minesweeper')

# Дополнительные поля к ячейкам сапера, которые образовывают игровую доску, в пикселях
Asset.border['top'] = config.top
Asset.border['bottom'] = config.bottom
Asset.border['left'] = config.left
Asset.border['right'] = config.right

# Y координата для клика по смайлу
Asset.smile_y_coord = config.smile_y_coord

# Разрешить для ассета режим No guess (без отгадывания, первый ход по зеленому кресту)
Asset.allow_noguess = config.allow_noguess

# Какие кнопки мыши задействованы для данной реализации
Asset.flag = config.flag
Asset.open = config.open
Asset.nearby = config.nearby

# Лаг обновления экрана после клика мышки
# float Lag for the board to have time to update the image after click the mouse button. Different value for different game realization.
Asset.LAG = config.LAG

# Проверяем наличие всех изображений ассета - получаем эксепшн при отсутствии файла
pics = ['0.png', '1.png', '2.png', '3.png', '4.png', '5.png', '6.png', '7.png', '8.png', 'bomb.png', 'clock_0.png', 'clock_1.png', 'clock_2.png', 'clock_3.png', 'clock_4.png', 'clock_5.png', 'clock_6.png', 'clock_7.png', 'clock_8.png', 'clock_9.png', 'closed.png', 'error_bomb.png', 'fail.png', 'flag.png', 'red_bomb.png', 'smile.png', 'win.png']
if Asset.allow_noguess:
    pics.append('noguess.png')
for f in pics:
    pathlib.Path(pathlib.PurePath(directory, f)).open()

# Создаем список patterns - который содержит все изображения клеток. Его тип - SimpleNamespace
# К нему можно обращаться patterns.bomb или patterns.n3
# Так же делаем list_patterns - это просто tuple всех паттернов.
keys = ['n' + str(x) for x in range(8)]
# TODO в теории ниже должно быть range(9) - но изображение восьмерки очень сложно поймать.
numbered_cells = [Asset(f'{i}', f'{directory}/{i}.png') for i in range(8)]
d = dict(zip(keys, numbered_cells))
patterns = SimpleNamespace(**d)

patterns.closed = Asset('closed', f'{directory}/closed.png')
patterns.bomb = Asset('bomb', f'{directory}/bomb.png')
patterns.red_bomb = Asset('red_bomb', f'{directory}/red_bomb.png')
patterns.flag = Asset('flag', f'{directory}/flag.png')
patterns.fail = Asset('fail', f'{directory}/fail.png')
patterns.win = Asset('win', f'{directory}/win.png')
patterns.smile = Asset('smile', f'{directory}/smile.png')
# TODO Если асет для minesweeper onlie то добавлять иначе нет
if Asset.allow_noguess:
    patterns.noguess = Asset('noguess', f'{directory}/noguess.png')

# конвертируем объект SimpleNamespace, который по сути обертка для dict, в список.
# Потому что dict не итерируемый, а в cell.py нам нужен перебор `for` циклом
list_patterns = []
for name, obj in patterns.__dict__.items():
    list_patterns.append(obj)

# TODO говногод
#      но я хз как сделать красиво. Суть в том, что дальше мы будем очень часто итерировать этот список.
#      и для увеличения производительности самые часто встечающиеся элементы должны быть в начале списка. Это 0 и closed
list_patterns.remove(patterns.closed)
list_patterns.insert(0, patterns.closed)


# Список цифр, используемых на поле в подсчете бомб и секунд
red_digits = [Asset(f'clock{i}', f'{directory}/clock_{i}.png') for i in range(10)]
