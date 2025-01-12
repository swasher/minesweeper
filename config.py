from os import path
import configparser
import ctypes


settings_file = path.abspath(path.join(path.dirname(__file__), 'settings.ini'))
settings_local_file = path.abspath(path.join(path.dirname(__file__), 'settings.local.ini'))


conf = configparser.ConfigParser()
conf.read(settings_file, encoding='utf-8')

# Читаем вспомогательный конфигурационный файл, настройки из которого перезаписывают settings.ini
conf.read(settings_local_file, encoding='utf-8')


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
        LAG - Лаг обновления экрана после клика мышки

        string_val = config.get('section_a', 'string_val')
        bool_val = config.getboolean('section_a', 'bool_val')
        int_val = config.getint('section_a', 'int_val')
        """
        self.asset = conf.get('main', 'asset')

        # main
        self.seconds_beetwen_games = conf.getint('main', 'seconds_beetwen_games')

        # game
        self.noguess = conf.getboolean('game', 'no_guess')
        self.noflag = conf.getboolean('game', 'noflag')
        self.arena = conf.getboolean('game', 'arena')
        self.need_win_parties = conf.getint('game', 'need_win_parties')
        self.need_total_parties = conf.getint('game', 'need_total_parties')

        # mouse
        self.mouse_randomize_xy = conf.getboolean('mouse', 'mouse_randomize_xy')
        self.use_neural_mouse = conf.getboolean('mouse', 'use_neural_mouse')

        # debug
        self.turn_by_turn = conf.getboolean('debug', 'turn_by_turn')
        self.icecream = conf.getboolean('debug', 'icecream')
        self.extra_pause_between_clicks = conf.getfloat('debug', 'extra_pause_between_clicks')
        self.print_time_between_clicks = conf.getboolean('debug', 'print_time_between_clicks')

        # implementation
        self.left = conf.getint(self.asset, 'left')
        self.right = conf.getint(self.asset, 'right')
        self.top = conf.getint(self.asset, 'top')
        self.bottom = conf.getint(self.asset, 'bottom')
        self.smile_y_coord = conf.getint(self.asset, 'smile_y_coord')
        self.allow_noguess = conf.getboolean(self.asset, 'allow_noguess')
        self.screen_refresh_lag = conf.getfloat(self.asset, 'screen_refresh_lag')

        # self.flag = conf.get(self.asset, 'flag')
        self.flag_button = conf.get(self.asset, 'flag')

        # self.open = conf.get(self.asset, 'open')
        self.open_button = conf.get(self.asset, 'open')

        # self.nearby = conf.get(self.asset, 'nearby')
        self.nearby_button = conf.get(self.asset, 'nearby')

        # tk version
        self.tk = conf.getboolean(self.asset, 'tk')

        self.measured_distance = list(map(float, conf.get(self.asset, 'measured_distance').split(",")))
        self.measured_duration = list(map(float, conf.get(self.asset, 'measured_duration').split(",")))
        self.minimum_delay_between_clicks = conf.getfloat(self.asset, 'minimum_delay_between_clicks')


config = Configuration()
