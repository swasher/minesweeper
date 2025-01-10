from dataclasses import dataclass


@dataclass
class Foo():
    i: int

a = 5
b = 'Moo'
c = Foo(5)
d = Foo
e = b + str(a)

values = "5"


def taste(values):
    c = 7

    match values:
        case 'Foo', c:
            print('foo', c)
        case 'Foo', 2+3:
            print('foo', c)
        case 'Foo':
            print(5)

        case _:
            print('dont match')

if __name__ == '__main__':
    values = 'foo', 5
    taste(values)