"""
WORK 2560х1440
---------------

масштаб клетка
10      11x11 px (min size)
20      22х23 px
*22     25х25 px
24      27х27 px
28      32х32 px
60      67x67 px (max size)

HOUSE
22      22x22 px
*24     24x24 px

"""

from types import SimpleNamespace

# set_pict = 'asset_22_2560x1440'
set_pict = 'asset_24_1920x1080'

# TODO Choose asset by scrren size
# TODO asset должен сам определять, какой взять, а если не получится определять на лету - прибить там гвоздями


class Asset():
    name = ''
    filename = ''
    similarity = 0
    set_pict = ''

    def __init__(self, name, filename):
        self.name = name
        self.filename = filename

    def __repr__(self):
        return '<'+self.name+'>'

Asset.set_pict = set_pict

# patterns = [Cell_pattern(f'{i}', f'{Cell_pattern.asset}/{i}.png') for i in range(7)]

keys = ['n'+str(x) for x in range(7)]
numbered_cells = [Asset(f'{i}', f'{Asset.set_pict}/{i}.png') for i in range(7)]

d = dict(zip(keys, numbered_cells))
patterns = SimpleNamespace(**d)

patterns.closed = Asset('closed', f'{Asset.set_pict}/closed.png')
patterns.bomb = Asset('bomb', f'{Asset.set_pict}/bomb.png')
patterns.red_bomb = Asset('red_bomb', f'{Asset.set_pict}/red_bomb.png')
patterns.flag = Asset('flag', f'{Asset.set_pict}/flag.png')
patterns.fail = Asset('fail', f'{Asset.set_pict}/fail.png')
