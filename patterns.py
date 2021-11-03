"""
Слой абстракции между логикой и конкретной реализацией сапера.

В другие модули нужно импортировать не экземпляр, а сам класс Board, и из него брать
необходимые данные

Экспортирует в другие модули:
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


class Pattern(object):
    """
    Привязывает растровые изображения ячеек к классу Pattern. Является зависимым от типа сапера.
    """
    # ----
    # WARNING!!!!
    # РАЗМЕР АССЕТОВ НЕ СООТВЕТСТВУЕТ РАЗМЕРУ ЯЧЕЕК - ОНИ КРОПЛЕНЫ В РАЗМЕР ИЗОБРАЖЕНИЯ!!!
    # ТОЛЬКО РАЗМЕР ЯЧЕЙКИ CLOSED ЯВЛЯЕТСЯ РАЗМЕРОМ ЯЧЕЕК В ПИКСЕЛЯХ!!!
    # ПОЭТОМУ ТУТ НЕ МОЖЕТ БЫТЬ СВОЙСТВ ШИРИНА-ВЫСОТА
    # ----

    # TODO тут это вообще не уместно - паттерн про паттерны, а не про границы доски!!!
    border = {}  # граница поля сапера в пикселях, от ячеек до края; скриншот каждый раз делается по этой области
    name = ''
    filename = ''
    similarity = 0
    raster = ''

    def __init__(self, name, filename):
        self.name = name
        self.filename = filename
        self.raster = cv.imread(filename, cv.IMREAD_COLOR)

    def __repr__(self):
        return '<'+self.name+'>'


directory = config.asset

# Дополнительные поля к ячейкам сапера, которые образовывают игровую доску, в пикселях
borders = importlib.import_module(f'{directory}.asset', package='.minesweeper')
Pattern.border['top'] = borders.top
Pattern.border['bottom'] = borders.bottom
Pattern.border['left'] = borders.left
Pattern.border['right'] = borders.right


# Создаем список patterns - который содержит все изображения клеток. Тип SimpleNamespace
# Можно обращаться patterns.bomb или patterns.n3
# Так же делаем list_patterns - это просто tuple всех паттернов.
keys = ['n' + str(x) for x in range(7)]
# TODO в теории ниже должно быть range(9) - но изображение восьмерки очень сложно поймать.
numbered_cells = [Pattern(f'{i}', f'{directory}/{i}.png') for i in range(8)]
d = dict(zip(keys, numbered_cells))
patterns = SimpleNamespace(**d)

patterns.closed = Pattern('closed', f'{directory}/closed.png')
patterns.bomb = Pattern('bomb', f'{directory}/bomb.png')
patterns.red_bomb = Pattern('red_bomb', f'{directory}/red_bomb.png')
patterns.flag = Pattern('flag', f'{directory}/flag.png')
patterns.fail = Pattern('fail', f'{directory}/fail.png')
patterns.win = Pattern('win', f'{directory}/win.png')
patterns.smile = Pattern('smile', f'{directory}/smile.png')
# TODO Если асет для minesweeper onlie то добавлять иначе нет
if config.allow_noguess:
    patterns.noguess = Pattern('noguess', f'{directory}/noguess.png')

# конвертируем объект SimpleNamespace, который по сути обертка для dict, в список.
# Потому что dict не итерируемый, а в cell.py нам нужен перебор `for` циклом
list_patterns = []
for name, obj in patterns.__dict__.items():
    list_patterns.append(obj)

# Список цифр, используемых на поле в подсчете бомб и секунд
red_digits = [Pattern(f'clock{i}', f'{directory}/clock_{i}.png') for i in range(10)]

