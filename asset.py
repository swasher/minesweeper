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

import pathlib
from types import SimpleNamespace
import cv2 as cv
from config import config


class Asset(object):
    """
    Тип Asset инкапсулиет растровае изображения ячеек и других объектов игрового поля в объекты.
    """
    # ----
    # WARNING!!!!
    # РАЗМЕР АССЕТОВ НЕ СООТВЕТСТВУЕТ РАЗМЕРУ ЯЧЕЕК - ОНИ КРОПЛЕНЫ В РАЗМЕР ИЗОБРАЖЕНИЯ!!!
    # ТОЛЬКО РАЗМЕР ЯЧЕЙКИ CLOSED ЯВЛЯЕТСЯ РАЗМЕРОМ ЯЧЕЕК В ПИКСЕЛЯХ!!!
    # ПОЭТОМУ ТУТ НЕ МОЖЕТ БЫТЬ СВОЙСТВ ШИРИНА-ВЫСОТА
    # ----

    # TODO У нас кадлый экземпряр Asset имеет несвойственные для него поля,
    #      например, Clock0 имеет поля LAG, border и так далее. Можно увидеть в дебаге.

    name = ''
    filename = ''
    similarity = 0
    raster = ''
    value = None  # if applicable - represent number of Cell; if not - None
    repr = None   # if appicable - represent cell in print board

    def __init__(self, name, filename, value=None, repr=None):
        self.name = name
        self.filename = filename
        self.raster = cv.imread(filename, cv.IMREAD_COLOR)
        self.value = value
        self.repr = repr

    def __repr__(self):
        return '<'+self.name+'>'


directory = config.asset

# deprecated
# asset_data = importlib.import_module(f'{directory}.asset', package='.minesweeper')


# Проверяем наличие всех изображений ассета - получаем эксепшн при отсутствии файла
pics = ['0.png', '1.png', '2.png', '3.png', '4.png', '5.png', '6.png', '7.png', '8.png', 'bomb.png', 'clock_0.png', 'clock_1.png', 'clock_2.png', 'clock_3.png', 'clock_4.png', 'clock_5.png', 'clock_6.png', 'clock_7.png', 'clock_8.png', 'clock_9.png', 'closed.png', 'error_bomb.png', 'fail.png', 'flag.png', 'red_bomb.png', 'smile.png', 'win.png']
if config.allow_noguess:
    # потому что не во всех наборах есть такое изображение - пока только в Minesweeper online
    pics.append('noguess.png')
for f in pics:
    # Проверяем, все ли есть файлы ассета; если нет, возникнет эксепшн.
    pathlib.Path(pathlib.PurePath(directory, f)).open()


# digits
n0 = Asset('0', f'{directory}/0.png', 0, ' ')
n1 = Asset('1', f'{directory}/1.png', 1, '1')
n2 = Asset('2', f'{directory}/2.png', 2, '2')
n3 = Asset('3', f'{directory}/3.png', 3, '3')
n4 = Asset('4', f'{directory}/4.png', 4, '4')
n5 = Asset('5', f'{directory}/5.png', 5, '5')
n6 = Asset('6', f'{directory}/6.png', 6, '6')
n7 = Asset('7', f'{directory}/7.png', 7, '7')
n8 = Asset('8', f'{directory}/8.png', 8, '8')

# cells
closed = Asset('closed', f'{directory}/closed.png', None, '·')
bomb = Asset('bomb', f'{directory}/bomb.png', None, '⚹')
red_bomb = Asset('red_bomb', f'{directory}/red_bomb.png', None, '✱')
flag = Asset('flag', f'{directory}/flag.png', None, '⚑')
# if config.allow_noguess:
noguess = Asset('noguess', f'{directory}/noguess.png', None, 'x')

# smile
fail = Asset('fail', f'{directory}/fail.png')
win = Asset('win', f'{directory}/win.png')
smile = Asset('smile', f'{directory}/smile.png')

# Список цифр, используемых на поле в подсчете бомб и секунд
red_digits = []
for i in range(10):
    obj = Asset(f'clock_{i}', f'{directory}/clock_{i}.png', i)
    red_digits.append(obj)


digits = [n1, n2, n3, n4, n5, n6, n7, n8]
open_cells = [n0, n1, n2, n3, n4, n5, n6, n7, n8]
bombs = [bomb, red_bomb]
all_cell_types = [closed, n0, n1, n2, n3, n4, n5, n6, n7, n8, flag, bomb, red_bomb]


