from rich import print
from minesweepr import read_board
from minesweepr import Board
from minesweepr import generate_rules
from minesweepr import solve

# . = blank; * = mine(flag); x = unknown; N = count
ascii_encoded = """
...2x
.113x
.2*xx
13*xx
xxxxx
"""

ascii_encoded2 = """
xxxxx
xxxxx
11111
.....
.....
"""


def main():
    b = Board(ascii_encoded2)
    r = generate_rules(b, total_mines=2)
    # g представляет из себя кортеж: первый элемент, это List[Rule], а второй - объект MineCount, это NamedTupe с ключами 'total_cells' и 'total_mines'
    # total_cells равен кол-ву закрытых+флаги, total_mines - мы указываем при запуске generate_rules.
    """
    Судя по описанию, 
    mine_prevalence — объект, описывающий общее количество ожидаемых мин на
    доске. MineCount указывает на традиционный minesweeper (фиксированные размеры доски с общим количеством мин); float указывает на фиксированную
    вероятность того, что любая неизвестная ячейка является миной (общее количество мин будет меняться для заданных размеров доски в биномиальном распределении)
    
    То есть это либо объект MineCount, либо float
    """
    rules = r[0]
    mine_prevalence = r[1]
    solution = solve(rules=rules, mine_prevalence=mine_prevalence)
    print(solution)


if __name__ == "__main__":
    main()
