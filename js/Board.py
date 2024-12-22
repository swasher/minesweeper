class Compressor:
    def __init__(self):
        self.BASE62 = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        self.VALUES = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "I", "H", "F", "O"]
        self.BASES = [10, 7, 5, 5, 4, 3, 3, 1, 1, 4, 10, 8, 1]
        self.digits = []

        start = 0
        for n in self.BASES:
            self.digits.append(self.BASE62[start:start + n])
            start += n

    def compress(self, input):
        output = ""
        count = 0
        prev_char = ""
        for curr_char in input:
            if prev_char == "":
                prev_char = curr_char
                count = 1
            elif curr_char == prev_char:
                count += 1
            else:
                output += self.compress_fragment(prev_char, count)
                prev_char = curr_char
                count = 1
        output += self.compress_fragment(prev_char, count)
        return output

    def compress_fragment(self, char, length):
        index = self.VALUES.index(char)
        if index == -1:
            print(f"Unable to find the value '{char}' in the compression values array")
            return ""
        digits = self.digits[index]
        base = len(digits)
        if base == 1:
            return digits * length
        output = ""
        while length != 0:
            digit = length % base
            output = digits[digit] + output
            length = (length - digit) // base
        return output

    def decompress(self, input):
        output = ""
        count = 0
        prev_char = ""
        for test_char in input:
            index = next(i for i, element in enumerate(self.digits) if test_char in element)
            curr_char = self.VALUES[index]
            curr_count = self.digits[index].index(test_char)
            base = len(self.digits[index])
            if prev_char == "":
                prev_char = curr_char
                count = curr_count
            elif curr_char == prev_char:
                if base == 1:
                    count += 1
                else:
                    count = count * base + curr_count
            else:
                output += prev_char * count
                prev_char = curr_char
                count = curr_count if base != 1 else 1
        output += prev_char * count
        return output

    def compress_number(self, number, size):
        base = len(self.BASE62)
        output = ""
        for _ in range(size):
            digit = number % base
            output = self.BASE62[digit] + output
            number = (number - digit) // base
        return output

    def decompress_number(self, value):
        base = len(self.BASE62)
        output = 0
        for char in value:
            digit = self.BASE62.index(char)
            output = output * base + digit
        return output


class Board:
    def __init__(self, id, width, height, num_bombs, seed, game_type):
        self.MAX = 4294967295

        self.id = id
        self.game_type = game_type
        self.width = width
        self.height = height
        self.num_bombs = num_bombs
        self.seed = seed

        self.tiles = []
        self.started = False
        self.bombs_left = self.num_bombs

        self.init_tiles()

        self.gameover = False
        self.won = False

        self.high_density = False

        self.compressor = Compressor()

    def is_started(self):
        return self.started

    def set_game_lost(self):
        self.gameover = True

    def set_game_won(self):
        self.gameover = True
        self.won = True

    def is_gameover(self):
        return self.gameover

    def get_id(self):
        return self.id

    def set_started(self):
        if self.started:
            print("Logic error: starting the same game twice")
            return
        self.started = True

    def set_high_density(self, tiles_left, mines_left):
        self.high_density = mines_left * 5 > tiles_left * 2

    def is_high_density(self):
        return self.high_density

    def xy_to_index(self, x, y):
        return y * self.width + x

    def get_tile_xy(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return None
        index = self.xy_to_index(x, y)
        return self.tiles[index]

    def get_tile(self, index):
        return self.tiles[index]

    # true if number of flags == tiles value
    # and number of unrevealed > 0
    def can_chord(self, tile):
        flag_count = 0
        covered_count = 0
        for adj_tile in self.get_adjacent(tile):
            if adj_tile.is_flagged():
                flag_count += 1
            if adj_tile.is_covered() and not adj_tile.is_flagged():
                covered_count += 1
        return flag_count == tile.get_value() and covered_count > 0

    def adjacent_found_mine_count(self, tile):
        mine_count = 0
        for adj_tile in self.get_adjacent(tile):
            if adj_tile.is_solver_found_bomb():
                mine_count += 1
        return mine_count

    def adjacent_flags_placed(self, tile):
        flag_count = 0
        for adj_tile in self.get_adjacent(tile):
            if adj_tile.is_flagged():
                flag_count += 1
        return flag_count

    def adjacent_covered_count(self, tile):
        covered_count = 0
        for adj_tile in self.get_adjacent(tile):
            if adj_tile.is_covered() and not adj_tile.is_solver_found_bomb():
                covered_count += 1
        return covered_count

    def get_message_header(self):
        return {
            "id": self.id,
            "width": self.width,
            "height": self.height,
            "mines": self.num_bombs,
            "seed": self.seed,
            "gametype": self.game_type
        }

    def get_adjacent(self, tile):
        col = tile.x
        row = tile.y

        first_row = max(0, row - 1)
        last_row = min(self.height - 1, row + 1)

        first_col = max(0, col - 1)
        last_col = min(self.width - 1, col + 1)

        result = []

        for r in range(first_row, last_row + 1):
            for c in range(first_col, last_col + 1):
                if not (r == row and c == col):
                    index = self.width * r + c
                    result.append(self.tiles[index])

        return result

    def get_flags_placed(self):
        tally = 0
        for tile in self.tiles:
            if tile.is_flagged():
                tally += 1
        return tally

    def init_tiles(self):
        for y in range(self.height):
            for x in range(self.width):
                self.tiles.append(Tile(x, y, y * self.width + x))

    def set_all_zero(self):
        for tile in self.tiles:
            tile.set_value(0)

    def has_safe_tile(self):
        for tile in self.tiles:
            if tile.get_has_hint() and tile.probability == 1:
                return True
        return False

    def get_safe_tiles(self):
        result = []
        for tile in self.tiles:
            if tile.get_has_hint() and tile.probability == 1:
                result.append(Action(tile.get_x(), tile.get_y(), 1, ACTION_CLEAR))
        return result

    def reset_for_analysis(self, flag_is_mine, find_obvious_mines):
        for tile in self.tiles:
            if not tile.is_covered() and tile.is_flagged():
                print(f"{tile.as_text()} is flagged but not covered! Resetting to covered.")
                tile.set_covered(True)
            tile.found_bomb = flag_is_mine if tile.is_flagged() else False

        if not find_obvious_mines:
            return None

        for tile in self.tiles:
            if tile.is_covered():
                if self.is_tile_a_mine(tile):
                    tile.set_found_bomb()
                continue

            adj_tiles = self.get_adjacent(tile)
            flag_count = 0
            covered_count = 0
            for adj_tile in adj_tiles:
                if adj_tile.is_covered():
                    covered_count += 1
                if adj_tile.is_flagged():
                    flag_count += 1

            if covered_count > 0 and tile.get_value() == covered_count:
                for adj_tile in adj_tiles:
                    if adj_tile.is_covered():
                        adj_tile.set_found_bomb()
            elif tile.get_value() < flag_count:
                print(f"{tile.as_text()} is over flagged")
            elif tile.get_value() > covered_count:
                print(f"{tile.as_text()} has an invalid value of {tile.get_value()} with only {covered_count} surrounding covered tiles")
                return tile

        return None

    def is_tile_a_mine(self, tile):
        adj_tiles = self.get_adjacent(tile)
        witness_count = 0
        for adj_tile in adj_tiles:
            if adj_tile.is_covered():
                continue
            witness_count += 1
            if not self.check_witness(adj_tile):
                return False
        return witness_count > 0

    def check_witness(self, tile):
        adj_tiles = self.get_adjacent(tile)
        covered_count = 0
        for adj_tile in adj_tiles:
            if adj_tile.is_covered():
                covered_count += 1
        return covered_count > 0 and tile.get_value() == covered_count

    def get_hash_value(self):
        hash_value = (31 * 31 * 31 * self.num_bombs + 31 * 31 * self.get_flags_placed() + 31 * self.width + self.height) % self.MAX
        for tile in self.tiles:
            if tile.is_flagged():
                hash_value = (31 * hash_value + 13) % self.MAX
            elif tile.is_covered():
                hash_value = (31 * hash_value + 12) % self.MAX
            else:
                hash_value = (31 * hash_value + tile.get_value()) % self.MAX
        return hash_value

    def get_state_data(self):
        pass  # Implement this method if needed

    def find_auto_move(self):
        result = {}
        for tile in self.tiles:
            if tile.is_flagged() or tile.is_covered():
                continue
            adj_tiles = self.get_adjacent(tile)
            needs_work = False
            flag_count = 0
            covered_count = 0
            for adj_tile in adj_tiles:
                if adj_tile.is_covered() and not adj_tile.is_flagged():
                    needs_work = True
                if adj_tile.is_flagged():
                    flag_count += 1
                elif adj_tile.is_covered():
                    covered_count += 1
            if needs_work:
                if tile.get_value() == flag_count:
                    for adj_tile in adj_tiles:
                        if adj_tile.is_covered() and not adj_tile.is_flagged():
                            result[adj_tile.index] = Action(adj_tile.get_x(), adj_tile.get_y(), 1, ACTION_CLEAR)
                elif tile.get_value() == flag_count + covered_count:
                    for adj_tile in adj_tiles:
                        if adj_tile.is_covered() and not adj_tile.is_flagged():
                            adj_tile.set_found_bomb()
                            result[adj_tile.index] = Action(adj_tile.get_x(), adj_tile.get_y(), 0, ACTION_FLAG)
        return list(result.values())

    def get_format_mbf(self):
        if self.width > 255 or self.height > 255:
            print("Board too large to save as MBF format")
            return None

        length = 4 + 2 * self.num_bombs
        mbf = bytearray(length)
        mbf[0] = self.width
        mbf[1] = self.height
        mbf[2] = self.num_bombs // 256
        mbf[3] = self.num_bombs % 256

        mines_found = 0
        index = 4
        for tile in self.tiles:
            if tile.is_flagged():
                mines_found += 1
                if index < length:
                    mbf[index] = tile.get_x()
                    mbf[index + 1] = tile.get_y()
                    index += 2

        if mines_found != self.num_bombs:
            print(f"Board has incorrect number of mines. board={self.num_bombs}, found={mines_found}")
            return None

        print(mbf)
        return mbf

    def get_position_data(self):
        new_line = "\n"
        data = f"{self.width}x{self.height}x{self.num_bombs}{new_line}"
        for y in range(self.height):
            for x in range(self.width):
                tile = self.get_tile_xy(x, y)
                if tile.is_flagged():
                    data += "F"
                elif tile.is_covered() or tile.is_bomb():
                    data += "H"
                else:
                    data += str(tile.get_value())
            data += new_line
        return data

    def get_simple_compressed_data(self):
        pass  # Implement this method if needed

    def get_compressed_data(self, reduce_mines):
        pass  # Implement this method if needed