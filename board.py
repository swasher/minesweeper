from config import config


class Board(object):
    border = {}  # граница поля сапера в пикселях, от ячеек до края; скриншот каждый раз делается по этой области
    smile_y_coord = 0  # координата Y для клика по смайлу


board = Board()

# Дополнительные поля к ячейкам сапера, которые образовывают игровую доску, в пикселях
board.border['top'] = config.top
board.border['bottom'] = config.bottom
board.border['left'] = config.left
board.border['right'] = config.right

# Y координата для клика по смайлу
board.smile_y_coord = config.smile_y_coord

