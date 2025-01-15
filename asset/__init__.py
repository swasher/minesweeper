from config import config

from .asset import (bomb_wrong, bomb_red, bomb, flag, closed, n0, n1, n2, n3, n4, n5, n6, n7, n8, win, fail, smile,
                    bombs, digits, open_cells, all_cell_types)

if config.allow_noguess:
    from .asset import noguess
if config.tk:
    from .asset import there_is_bomb
