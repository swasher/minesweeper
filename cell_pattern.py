class Cell_pattern():
    name = ''
    filename = ''
    similarity = 0

    def __init__(self, name, filename):
        self.name = name
        self.filename = filename


patterns = [Cell_pattern(f'{i}', f'pic/{i}.png') for i in range(7)]
patterns.append(Cell_pattern('closed', 'pic/closed.png'))
patterns.append(Cell_pattern('bomb', 'pic/bomb.png'))
patterns.append(Cell_pattern('red_bomb', 'pic/red_bomb.png'))
patterns.append(Cell_pattern('flag', 'pic/flag.png'))
