from .asset import Asset, initialize_assets, find_asset_by_value

# Объявляем все переменные как None изначально
bomb_wrong = bomb_red = bomb = flag = closed = None
n0 = n1 = n2 = n3 = n4 = n5 = n6 = n7 = n8 = None
led0 = led1 = led2 = led3 = led4 = led5 = led6 = led7 = led8 = led9 = None
win = fail = smile = None
bombs = digits = open_cells = all_cell_types = led_digits = None
there_is_bomb = no_guess = None


def init(custom_path=None):
    """Инициализирует все ассеты и делает их доступными для импорта"""
    global bomb_wrong, bomb_red, bomb, flag, closed
    global n0, n1, n2, n3, n4, n5, n6, n7, n8
    global led0, led1, led2, led3, led4, led5, led6, led7, led8, led9
    global win, fail, smile
    global bombs, digits, open_cells, led_digits, all_cell_types
    global no_guess, there_is_bomb

    # Получаем инициализированные ассеты
    assets = initialize_assets(custom_path)

    # Присваиваем значения глобальным переменным
    bomb_wrong = assets['bomb_wrong']
    bomb_red = assets['bomb_red']
    bomb = assets['bomb']
    flag = assets['flag']
    closed = assets['closed']
    no_guess = assets['no_guess']
    there_is_bomb = assets['there_is_bomb']

    win = assets['win']
    fail = assets['fail']
    smile = assets['smile']

    n0 = assets['n0']
    n1 = assets['n1']
    n2 = assets['n2']
    n3 = assets['n3']
    n4 = assets['n4']
    n5 = assets['n5']
    n6 = assets['n6']
    n7 = assets['n7']
    n8 = assets['n8']

    led0 = assets['led0']
    led1 = assets['led1']
    led2 = assets['led2']
    led3 = assets['led3']
    led4 = assets['led4']
    led5 = assets['led5']
    led6 = assets['led6']
    led7 = assets['led7']
    led8 = assets['led8']
    led9 = assets['led9']

    # Инициализируем коллекции
    led_digits = {led0, led1, led2, led3, led4, led5, led6, led7, led8, led9}
    digits = {n1, n2, n3, n4, n5, n6, n7, n8}
    open_cells = {n0, n1, n2, n3, n4, n5, n6, n7, n8}
    bombs = {bomb, bomb_red, bomb_wrong}
    all_cell_types = {closed, n0, n1, n2, n3, n4, n5, n6, n7, n8, flag, bomb, bomb_red, bomb_wrong, there_is_bomb}

    all_cell_types.add(no_guess)
    all_cell_types.add(there_is_bomb)

    return assets


# Инициализируем с дефолтными значениями при импорте модуля
init()

__all__ = [
    'bomb_wrong', 'bomb_red', 'bomb', 'flag', 'closed',
    'n0', 'n1', 'n2', 'n3', 'n4', 'n5', 'n6', 'n7', 'n8',
    'led0', 'led1', 'led2', 'led3', 'led4', 'led5', 'led6', 'led7', 'led8', 'led9',
    'win', 'fail', 'smile',
    'led_digits', 'digits', 'open_cells', 'bombs', 'all_cell_types',
    'there_is_bomb', 'no_guess',
    'find_asset_by_value',
    'init',
]
