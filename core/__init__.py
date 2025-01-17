"""

ТУТ АЦКИЙ БАГ. ПОЛУЧАЕТСЯ, ЧТО КАКУЮ МАТРИЦУ Я ПЕРВУЮ ИМПОРТИРУЮ, С ТАКИМ ПУТЕМ
И ИНИЦИАЛИЗИРУЮТСЯ АССЕТЫ, ТО ЕСТЬ ЕСЛИ Я ВВЕРХ ПОСТАВЛЮ PlayMatrix, ТО ЗАТЕМ В
ScreenMatrix У МЕНЯ УЖЕ БУДЕТ ПУТЬ К АССЕТУ asset_tk

"""

from .screen_matrix import ScreenMatrix
# from .play_matrix import PlayMatrix
from .matrix import Matrix
from .matrix import MineMode
from .cell import Cell
from .game import Game, beginner, beginner_new, intermediate, expert
from .utility import GameState, Color, Action
from .board import board
