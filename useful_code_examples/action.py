import mouse
import math
import numpy as np

from config import config


# TODO Продумать, как сделать класс Action, чтобы не использовать в коде текстовые обозначения кнопок мыши
#      'right', 'left'. Сюда же можно вынести функции мыши из util.

class Action(object):

    def open_cell(self):
        pass

    def set_flag(self):
        pass

    def open_nearest(self):
        pass


action = Action()
