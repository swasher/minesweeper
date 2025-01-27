from rich import print
import argparse
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


def try_solve_from_ascii(ascii: str):
    b = Board(ascii)
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


def fun1():
    print("Выполняется функция fun1")

def fun2():
    print("Выполняется функция fun2")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Запуск функций по команде")
    parser.add_argument('function', help='Имя функции для запуска')
    args = parser.parse_args()

    functions = {
        'fun1': try_solve_from_ascii,
        'fun2': fun2
    }

    if args.function in functions:
        functions[args.function]()
    else:
        print("Неизвестная функция. Доступные функции: {', '.join(functions.keys())}")