"""
Слой абстракции между логикой и конкретной реализацией сапера.


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
from util import get_screen_size

## TODO таким макаром мы будем искать размер экарана каждый раз при вызове паттерна!!!!
screen = get_screen_size()
if screen == [1920, 1080]:
    set_pict = 'asset_24_1920x1080'
elif screen == [2560, 1440]:
    set_pict = 'asset_28_2560x1440'
    # set_pict = 'asset_22_2560x1440'

# TODO Choose asset by screen size

# TODO asset должен сам определять, какой взять, а если не получится определять на лету - прибить там гвоздями

# TODO Сделать проверку, чтобы при загрузке ассетов они были нужного размера в px (по размеру closed ячейки)


class Asset():
    # ----
    # WARNING!!!!
    # РАЗМЕР АССЕТОВ НЕ СООТВЕТСТВУЕТ РАЗМЕРУ ЯЧЕЕК - ОНИ КРОПЛЕНЫ В РАЗМЕР ИЗОБРАЖЕНИЯ!!!
    # ТОЛЬКО РАЗМЕР ЯЧЕЙКИ CLOSED ЯВЛЯЕТСЯ РАЗМЕРОМ ЯЧЕЕК В ПИКСЕЛЯХ!!!
    # ПОЭТОМУ ТУТ НЕ МОЖЕТ БЫТЬ СВОЙСТВ ШИРИНА-ВЫСОТА
    # ----
    name = ''
    filename = ''
    similarity = 0
    set_pict = ''
    raster = ''
    border = {}  # граница поля сапера в пикселях, от ячеек до края; скриншот каждый раз делается по этой области

    def __init__(self, name, filename):
        self.name = name
        self.filename = filename
        self.raster = cv.imread(filename, cv.IMREAD_COLOR)

    def __repr__(self):
        return '<'+self.name+'>'


Asset.set_pict = set_pict

# Дополнительные поля к клеткам, в пикселях
borders = importlib.import_module('..asset', package='asset_24_1920x1080.asset')
Asset.border['top'] = borders.top
Asset.border['bottom'] = borders.bottom
Asset.border['left'] = borders.left
Asset.border['right'] = borders.right

# Как нужно покропить поле, чтобы распозавать кол-во оставшихся бомб

keys = ['n'+str(x) for x in range(7)]
numbered_cells = [Asset(f'{i}', f'{Asset.set_pict}/{i}.png') for i in range(7)]

d = dict(zip(keys, numbered_cells))


patterns = SimpleNamespace(**d)

patterns.closed = Asset('closed', f'{Asset.set_pict}/closed.png')
patterns.bomb = Asset('bomb', f'{Asset.set_pict}/bomb.png')
patterns.red_bomb = Asset('red_bomb', f'{Asset.set_pict}/red_bomb.png')
patterns.flag = Asset('flag', f'{Asset.set_pict}/flag.png')
patterns.fail = Asset('fail', f'{Asset.set_pict}/fail.png')
patterns.win = Asset('win', f'{Asset.set_pict}/win.png')
patterns.smile = Asset('smile', f'{Asset.set_pict}/smile.png')
patterns.noguess = Asset('noguess', f'{Asset.set_pict}/noguess.png')

# конвертируем объект SimpleNamespace, который по сути обертка для dict, в список.
# Потому что dict не итерируемый, а в cell.py нам нужен перебор for циклом
list_patterns = []
for name, obj in patterns.__dict__.items():
    list_patterns.append(obj)

bomb_numbers = [Asset(f'{i}', f'{Asset.set_pict}/{i}.png') for i in range(9)]