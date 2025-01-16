from config import config


class Board:

    def __init__(self):
        self.border = {}  # граница поля сапера в пикселях, от ячеек до края; скриншот каждый раз делается по этой области
        self.smile_y_coord = 0  # координата Y для клика по смайлу

        # Дополнительные поля к ячейкам сапера, которые образовывают игровую доску, в пикселях
        self.border['top'] = config.top
        self.border['bottom'] = config.bottom
        self.border['left'] = config.left
        self.border['right'] = config.right

        # Y координата для клика по смайлу
        # TODO откуда до куда эта координата ?????
        self.smile_y_coord = config.smile_y_coord


board = Board()

