import configparser

conf = configparser.ConfigParser()
conf.read('settings.ini')


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
        self.randomize_mouse = conf.getboolean('main', 'randomize_mouse')
        self.save_game_R1 = conf.getboolean('main', 'save_game_R1')
        self.duration_mouse = conf.getfloat('main', 'duration_mouse')
        # debug
        self.turn_by_turn = conf.getboolean('debug', 'turn_by_turn')
        self.icecream = conf.getboolean('debug', 'icecream')


config = Configuration()
