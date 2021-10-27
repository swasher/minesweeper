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
        self.debug_pause = conf.getboolean('main', 'debug_pause')
        self.solvers_debug = conf.getboolean('main', 'solvers_debug')
        self.save_mouse_position = conf.getboolean('main', 'save_mouse_position')
        self.randomize_mouse = conf.getboolean('main', 'randomize_mouse')
        self.duration_mouse = conf.getfloat('main', 'duration_mouse')


config = Configuration()
