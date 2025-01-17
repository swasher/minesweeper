from itertools import groupby


def compress_array(arr):
    """
    Удаляет из списка целые числа, которые находятся в близи difference друг к другу. Например:
    input [91, 91, 122, 123, 124, 154, 185, 217, 248, 279, 310, 311, 342, 374]
    difference 1
    output [91, 122, 124, 154, 185, 217, 248, 279, 310, 342, 374]

    Найдено тут. Как работает, хрен поймешь.
    https://stackoverflow.com/a/53177510/1334825


    Args:
        arr: array of int

    Returns:
        newarr: array of int
    """
    DIFFERENCE = 1

    def runs(difference=DIFFERENCE):
        start = None
        def inner(n):
            nonlocal start
            if start is None:
                start = n
            elif abs(start-n) > difference:
                start = n
            return start
        return inner

    newarr = [next(g) for k, g in groupby(sorted(arr), runs())]
    return newarr