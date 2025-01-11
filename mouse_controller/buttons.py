from enum import IntEnum


class MouseButton(IntEnum):
    left = 0
    right = 1
    both = 2

    def __str__(self):
        return f'{self.__class__.__name__}.{self.name}'

    @classmethod
    def _missing_(cls, value):
        if type(value) is str:
            value = value.lower()
            if value in dir(cls):
                return cls[value]
