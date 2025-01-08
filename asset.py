"""
Слой абстракции между логикой и конкретной реализацией сапера.

В другие модули нужно импортировать не экземпляр, а сам класс Board, - НА ДАННЫЙ МОМЕНТ BOARD НЕ РЕАЛИЗОВАН
и из него брать необходимые данные.

Предоставляет для других модулей следующие объекты Asset и их списки:
- ячейки - все типы ячеек, можно ссылаться как "if cell.asset == asset.bomb"
- списки ячеек, которые можно использовать как "if cell in digits"
- red_digits - (список) Красные буквы часов и счетчика бомб
- рожицы - три вида рожиц (smile)
- две специальные ячейки - noguess для игры без угадывания (minesweeper.online) и there_is_bomb для отображения бомбы в закрытой ячейке для minesweeper.Tk

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

from pathlib import Path, PurePath
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
    # ПОЭТОМУ ТУТ НЕ МОЖЕТ БЫТЬ СВОЙСТВ ШИРИНА-ВЫСОТА ЯЧЕЙКИ!
    # ----

    # TODO У нас каждый экземпряр Asset имеет несвойственные для него поля,
    #      например, Clock0 имеет поля LAG, border и так далее. Можно увидеть в дебаге.

    similarity = 0  # possible deprecated

    def __init__(self, name, filename, value=None, symbol=None):
        self.name = name
        self.filename = filename
        self.raster = cv.imread(filename, cv.IMREAD_COLOR)
        self.value = value  # digit for opened cells
        self.symbol = symbol  # if appicable - text represent of cell

    def __repr__(self):
        return '<'+self.name+'>'


dir_path = Path(__file__).resolve().parent / 'asset' / config.asset


# Проверяем наличие всех НЕОБХОДИМЫХ изображений ассета - получаем эксепшн при отсутствии файла
pics = ['0.png', '1.png', '2.png', '3.png', '4.png', '5.png', '6.png', '7.png', '8.png',
        'LED_0.png', 'LED_1.png', 'LED_2.png', 'LED_3.png', 'LED_4.png',
        'LED_5.png', 'LED_6.png', 'LED_7.png', 'LED_8.png', 'LED_9.png',
        'closed.png', 'flag.png', 'bomb.png', 'bomb_red.png', 'bomb_wrong.png',
        'face_unpressed.png', 'face_win.png', 'face_lose.png']
if config.allow_noguess:
    # потому что не во всех наборах есть такое изображение - пока только в Minesweeper online
    pics.append('no_guess.png')
for file_name in pics:
    file_path = dir_path / file_name  # Создаем полный путь к файлу
    if not file_path.exists():  # Проверяем, существует ли файл
        raise Exception(f"{file_name} не существует.")

# digits
n0 = Asset('0', dir_path.joinpath('0.png'), 0, '·')
n1 = Asset('1', dir_path.joinpath('1.png'), 1, '1')
n2 = Asset('2', dir_path.joinpath('2.png'), 2, '2')
n3 = Asset('3', dir_path.joinpath('3.png'), 3, '3')
n4 = Asset('4', dir_path.joinpath('4.png'), 4, '4')
n5 = Asset('5', dir_path.joinpath('5.png'), 5, '5')
n6 = Asset('6', dir_path.joinpath('6.png'), 6, '6')
n7 = Asset('7', dir_path.joinpath('7.png'), 7, '7')
n8 = Asset('8', dir_path.joinpath('8.png'), 8, '8')

# other cells
closed = Asset('closed', dir_path.joinpath('closed.png'), None, '⨯')
bomb = Asset('bomb', dir_path.joinpath('bomb.png'), None, '⚹')
bomb_red = Asset('bomb_red', dir_path.joinpath('bomb_red.png'), None, '✱')
bomb_wrong = Asset('bomb_wrong', dir_path.joinpath('bomb_wrong.png'), None, '⚐')
flag = Asset('flag', dir_path.joinpath('flag.png'), None, '⚑')

if config.allow_noguess:
    noguess = Asset('no_guess', dir_path.joinpath('no_guess.png'), None, '🕂')

# под закрытой клеткой находися бомба - для Tk
if dir_path.joinpath('there_is_bomb.png').exists():
    # если нет файла, то не создаем объект. Нужно только для редактора поля.
    there_is_bomb = Asset('there_is_bomb', dir_path.joinpath('there_is_bomb.png'), None, 'ơ')


# smile
fail = Asset('fail', dir_path.joinpath('face_lose.png'))
win = Asset('win', dir_path.joinpath('face_win.png'))
smile = Asset('smile', dir_path.joinpath('face_unpressed.png'))

# Список цифр, используемых на поле в подсчете бомб и секунд
red_digits = []
for i in range(10):
    obj = Asset(f'led_{i}', dir_path.joinpath(f'LED_{i}.png'), i)
    red_digits.append(obj)


digits = [n1, n2, n3, n4, n5, n6, n7, n8]
open_cells = [n0, n1, n2, n3, n4, n5, n6, n7, n8]
bombs = [bomb, bomb_red, bomb_wrong]
all_cell_types = [closed, n0, n1, n2, n3, n4, n5, n6, n7, n8, flag, bomb, bomb_red, bomb_wrong]

if config.allow_noguess:
    all_cell_types.append(noguess)
if 'there_is_bomb' in globals():
    all_cell_types.append(there_is_bomb)

