class Tile:
    def __init__(self, x, y, index):
        self.x = x
        self.y = y
        self.is_covered = True
        self.value = 0
        self.is_flagged = False
        self.found_bomb = False
        self.is_bomb = None  # This gets set when the game is lost
        self.exploded = False  # This gets set if this tile was the one clicked
        self.index = index

        self.on_edge = False
        self.hint = False
        self.probability = -1  # Probability of being safe
        self.hint_text = ""
        self.has_hint = False

        self.efficiency_value = ""  # The value we need to be chordable
        self.efficiency_probability = 0  # The probability of being that value
        self.efficiency_text = ""

        # Is there a mine adjacent to this tile? Set as part of the No flag efficiency logic
        self.adjacent_mine = False

        self.skull = False  # Used when hardcore rule triggers

        self.inflate = False  # Used when constructing a compressed board

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def is_adjacent(self, tile):
        dx = abs(self.x - tile.x)
        dy = abs(self.y - tile.y)

        # Adjacent and not equal
        return dx < 2 and dy < 2 and not (dx == 0 and dy == 0)

    def is_equal(self, tile):
        return self.x == tile.x and self.y == tile.y

    def as_text(self):
        return f"({self.x},{self.y})"

    def get_hint_text(self):
        if not self.has_hint:
            return ""
        else:
            return self.hint_text + self.efficiency_text

    def get_has_hint(self):
        return self.has_hint

    def set_probability(self, prob, progress, safety2):
        self.probability = prob
        self.has_hint = True

        if prob == 1:
            self.hint_text = "Clear"
        elif prob == 0:
            self.hint_text = "Mine"
        elif progress is None:
            self.hint_text = f"\n{prob * 100:.2f}% safe"
        else:
            self.hint_text = (
                f"\n{prob * 100:.2f}% safe"
                f"\n{safety2 * 100:.2f}% 2nd safety"
                f"\n{progress * 100:.2f}% progress"
            )

    def set_value_probability(self, value, probability):
        self.efficiency_value = value
        self.efficiency_probability = probability

        self.efficiency_text = f"\n{probability * 100:.2f}% value '{value}'"

    def clear_hint(self):
        self.on_edge = False
        self.has_hint = False
        self.hint_text = ""
        self.efficiency_value = None
        self.efficiency_probability = 0
        self.efficiency_text = ""
        self.probability = -1

    def set_on_edge(self):
        self.on_edge = True

    def is_covered(self):
        return self.is_covered

    def set_covered(self, covered):
        self.is_covered = covered

    def set_value(self, value):
        self.value = value
        self.is_covered = False

    def set_value_only(self, value):
        if self.is_flagged:
            print(f"{self.as_text()} assigning a value {value} to a flagged tile!")

        self.value = value

    def get_value(self):
        return self.value

    def rotate_value(self, delta):
        new_value = self.value + delta

        if new_value < 0:
            new_value = 8
        elif new_value > 8:
            new_value = 0

        self.set_value(new_value)

    def toggle_flag(self):
        self.is_flagged = not self.is_flagged

    def is_flagged(self):
        return self.is_flagged

    def set_found_bomb(self):
        self.found_bomb = True

    def unset_found_bomb(self):
        self.found_bomb = False

    def is_solver_found_bomb(self):
        return self.found_bomb

    def set_bomb(self, bomb):
        self.is_bomb = bomb

    def set_bomb_exploded(self):
        self.is_bomb = True
        self.exploded = True

    def is_bomb(self):
        return self.is_bomb

    def set_skull(self, is_skull):
        self.skull = is_skull

    def is_skull(self):
        return self.skull
