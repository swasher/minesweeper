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

asset_data = importlib.import_module(f'{directory}.asset', package='.minesweeper')

# Дополнительные поля к ячейкам сапера, которые образовывают игровую доску, в пикселях
Asset.border['top'] = asset_data.top
Asset.border['bottom'] = asset_data.bottom
Asset.border['left'] = asset_data.left
Asset.border['right'] = asset_data.right

# Y координата для клика по смайлу
Asset.smile_y_coord = asset_data.smile_y_coord

# Разрешить для ассета режим No guess (без отгадывания, первый ход по зеленому кресту)
Asset.allow_noguess = asset_data.allow_noguess

# Какие кнопки мыши задействованы для данной реализации
Asset.flag = asset_data.flag
Asset.open = asset_data.open
Asset.nearby = asset_data.nearby

# Лаг обновления экрана после клика мышки
# float Lag for the board to have time to update the image after click the mouse button. Different value for different game realization.
Asset.LAG = asset_data.LAG


# Создаем список patterns - который содержит все изображения клеток. Тип SimpleNamespace
# Можно обращаться patterns.bomb или patterns.n3
# Так же делаем list_patterns - это просто tuple всех паттернов.
keys = ['n' + str(x) for x in range(7)]
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

# Список цифр, используемых на поле в подсчете бомб и секунд
red_digits = [Asset(f'clock{i}', f'{directory}/clock_{i}.png') for i in range(10)]

