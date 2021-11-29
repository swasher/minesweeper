# def fib():
#     x1 = 0
#     x2 = 1
#     def get_next_number():
#         nonlocal x1, x2
#         x1, x2 = x2, x1 + x2
#         return x2
#     return get_next_number

# fibonacci = fib()
# for i in range(2, 21):
#     num = fibonacci()
#     print(f'The {i}th Fibonacci number is {num}')


# fibonacci = fib()
# num = fibonacci()
# print(num)
# num = fibonacci()
# print(num)

# def outer():
#     x = 1
#     def inner():
#         nonlocal x
#         print(f'prev: {x}')
#         x += 1
#         print(f'new: {x}\n')
#     return inner
#
# def x():
#     pass

def outer():
    x = 10
    print(x)

    def inner():
        # nonlocal x
        y = x + 12
        print(y)

    inner()
    print(x)

outer()