import win32api
import win32gui

from assets import closed
from config import config

from screen_controller import capture_full_screen
from screen_controller import cell_coordinates
from screen_controller import search_pattern_in_image
from exceptions import BoardNotFound


def find_board():
    """
    Находит поле сапера на экране и возвращает координаты клеток и область, в которой находится доска.

    :param board: global variable
    :param closedcell: объект Pattern, который содержит изображения клеток; мы будем искать на экране закрытую клетку (pattern.closed)
    :param asset: класс (не инстанс!) Asset, в котором содержится информация о "доске" - а именно размер полей в пикселях,
            от клеток до края "доски". Именно это поле (region), а не весь экран, мы в дальнейшем будем "сканировать".
    :return cells_coord_x: [array of int] Координаты строк (верхних левых углов клеток, относительно доски)
    :return cells_coord_y: [array of int] Координаты столбцов (верхних левых углов клеток, относительно доски)
    :return region: [x1, y1, x2, y2] координаты доски сапера на экране, первая пара - верхний левый угол, вторая пара - нижний правый угол. Включает всю доску с полями вокруг.
    """

    print('Try finding board...')
    image = capture_full_screen()

    precision = 0.8
    cells = search_pattern_in_image(closed.raster, image, precision)
    cells_coord_x, cells_coord_y = cell_coordinates(cells)

    if not len(cells_coord_x) or not len(cells_coord_y):
        raise BoardNotFound
    print(f' - found, {len(cells_coord_x)}x{len(cells_coord_y)}')

    template = closed.raster
    h, w = template.shape[:2]

    # Это поля "игрового поля" в дополнение к самим клеткам в пикселях
    # left = board.border['left']
    # right = board.border['right']
    # top = board.border['top']
    # bottom = board.border['bottom']

    region_x1 = cells_coord_x[0] - config.left
    region_x2 = cells_coord_x[-1] + config.right + w
    region_y1 = cells_coord_y[0] - config.top
    region_y2 = cells_coord_y[-1] + config.bottom + h

    region = (region_x1, region_y1, region_x2, region_y2)

    # Делаем коррекцию координат, чтобы они было относительно доски, а не экрана.
    cells_coord_x = [x-region_x1 for x in cells_coord_x]
    cells_coord_y = [y-region_y1 for y in cells_coord_y]

    DEBUG_DRAW_RECTANGLE = False
    if DEBUG_DRAW_RECTANGLE:
        print('Show debug from find_board()')
        dc = win32gui.GetDC(0)
        red = win32api.RGB(255, 0, 0)
        win32gui.SetPixel(dc, 0, 0, red)  # draw red at 0,0
        win32gui.Rectangle(dc, region_x1, region_y1, region_x2, region_y2)

    # todo Тут факен шайзе. Если у нас find_board то надо, наверное, возвращать Board, если у нас board содержит
    #   информацию о доске.  А потом из board делать matrix. А то у нас какие-то цифры возвращаются, а board
    #   меняется как синглтон, что вообще не очевидно.

    return cells_coord_x, cells_coord_y, region
