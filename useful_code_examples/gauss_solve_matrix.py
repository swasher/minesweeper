import numpy

m = numpy.array([
    [1, 1, 0, 0, 0],
    [1, 1, 1, 0, 0],
    [0, 1, 1, 1, 0],
    [0, 0, 1, 1, 1],
    [0, 0, 0, 1, 1],
])

m1 = numpy.linalg.pinv(m)

v = numpy.array([1, 2, 2, 2, 1])

s = numpy.linalg.pinv(m).dot(v)

print(s)
