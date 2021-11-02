import icecream as ic

class Cell_pattern():

    def __init__(self, similarity):
        self.similarity = similarity

    def __repr__(self):
        return str(self.similarity)


a = Cell_pattern(0.1)
b = Cell_pattern(0.5)
c = Cell_pattern(0.3)
d = Cell_pattern(0.2)

l = [a, b, c, d]

result = sorted(l, key=lambda x: x.similarity, reverse=True)[0]

# other variant without return, - mutate list
l.sort(key=lambda x: x.similarity, reverse=True)

print(type(result))
print(l[0])

