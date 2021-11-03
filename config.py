import configparser
import ctypes

conf = configparser.ConfigParser()
conf.read('settings.ini')


# Известные виды сапера. Называние соотв. директории с ассетом.
assets = {'Asset_24_1920x1080': 'asset_24_1920x1080',
          'Asset_28_2560x1440': 'asset_28_2560x1440',
          'Asset_22_2560x1440': 'asset_22_2560x1440'
          }


def get_screen_size():
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    size = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]
    return size


class Configuration(object):

    def __init__(self):
        """
        debug from click function
        mark sell durin solve (mark_cell_debug function)
        debug - return mouse to it position
        time - время перемещения мыши
        pause - пуза между солверами
        icecream debug messages

        string_val = config.get('section_a', 'string_val')
        bool_val = config.getboolean('section_a', 'bool_val')
        int_val = config.getint('section_a', 'int_val')
        """
        # main
        self.LAG = conf.getfloat('main', 'LAG')
        # game
        self.noguess = conf.getboolean('game', 'noguess')
        self.need_win_parties = conf.getint('game', 'need_win_parties')
        self.need_total_parties = conf.getint('game', 'need_total_parties')
        # mouse
        self.mouse_randomize_xy = conf.getboolean('mouse', 'mouse_randomize_xy')
        self.mouse_duration = conf.getfloat('mouse', 'mouse_duration')
        self.mouse_gaussian = conf.getfloat('mouse', 'mouse_gaussian')
        self.minimum_delay = conf.getfloat('mouse', 'minimum_delay')
        # debug
        self.save_game_R1 = conf.getboolean('debug', 'save_game_R1')
        self.turn_by_turn = conf.getboolean('debug', 'turn_by_turn')
        self.icecream = conf.getboolean('debug', 'icecream')

        # TODO эта функция должна импортироваться из Util, но при этом я получают множественные
        #      цикличные импорты
        screen = get_screen_size()
        if screen == [1920, 1080]:
            self.asset = assets['Asset_24_1920x1080']
        elif screen == [2560, 1440]:
            self.asset = assets['Asset_28_2560x1440']
            # self.asset  = assets['Asset_22_2560x1440']
        # self.asset = assets['Asset_24_1920x1080']


config = Configuration()
