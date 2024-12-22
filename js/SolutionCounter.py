class SolutionCounter:
    SMALL_COMBINATIONS = [
        [1], [1, 1], [1, 2, 1], [1, 3, 3, 1], [1, 4, 6, 4, 1], [1, 5, 10, 10, 5, 1],
        [1, 6, 15, 20, 15, 6, 1], [1, 7, 21, 35, 35, 21, 7, 1], [1, 8, 28, 56, 70, 56, 28, 8, 1]
    ]

    def __init__(self, board, all_witnesses, all_witnessed, squares_left, mines_left):
        self.board = board
        self.witnessed = all_witnessed
        self.pruned_witnesses = []
        self.mines_left = mines_left
        self.tiles_off_edge = squares_left - len(all_witnessed)
        self.min_total_mines = mines_left - self.tiles_off_edge
        self.max_total_mines = mines_left
        self.boxes = []
        self.box_witnesses = []
        self.mask = []
        self.working_probs = []
        self.held_probs = []
        self.off_edge_mine_tally = 0
        self.final_solutions_count = 0
        self.clear_count = 0
        self.local_clears = []
        self.valid_web = True
        self.invalid_reasons = []
        self.recursions = 0

        if mines_left < 0:
            self.valid_web = False
            self.invalid_reasons.append("Not enough mines left to complete the board.")
            return

        pruned = 0
        for wit in all_witnesses:
            box_wit = BoxWitness(self.board, wit)
            if box_wit.mines_to_find < 0:
                self.invalid_reasons.append(f"Tile {wit.as_text()} value '{wit.get_value()}' is too small? Or a neighbour too large?")
                self.valid_web = False
            if box_wit.mines_to_find > len(box_wit.tiles):
                self.invalid_reasons.append(f"Tile {wit.as_text()} value '{wit.get_value()}' is too large? Or a neighbour too small?")
                self.valid_web = False

            duplicate = False
            for w in self.box_witnesses:
                if w.equivalent(box_wit):
                    if w.tile.get_value() - board.adjacent_found_mine_count(w.tile) != box_wit.tile.get_value() - board.adjacent_found_mine_count(box_wit.tile):
                        self.invalid_reasons.append(f"Tiles {w.tile.as_text()} and {box_wit.tile.as_text()} are contradictory.")
                        self.valid_web = False
                    duplicate = True
                    break
            if not duplicate:
                self.pruned_witnesses.append(box_wit)
            else:
                pruned += 1
            self.box_witnesses.append(box_wit)

        uid = 0
        for tile in self.witnessed:
            count = sum(1 for wit in all_witnesses if tile.is_adjacent(wit))
            found = False
            for box in self.boxes:
                if box.fits(tile, count):
                    box.add(tile)
                    found = True
                    break
            if not found:
                self.boxes.append(Box(self.box_witnesses, tile, uid))
                uid += 1

        least_mines_needed = 0
        for box in self.boxes:
            box.calculate(self.mines_left)
            least_mines_needed += box.min_mines

        if least_mines_needed > mines_left:
            self.valid_web = False
            self.invalid_reasons.append(f"{mines_left} mines left is not enough mines left to complete the board.")

    def process(self):
        if not self.valid_web:
            self.final_solutions_count = 0
            self.clear_count = 0
            return

        self.mask = [False] * len(self.boxes)
        self.held_probs.append(ProbabilityLine(len(self.boxes), 1))
        self.working_probs.append(ProbabilityLine(len(self.boxes), 1))

        next_witness = self.find_first_witness()
        while next_witness is not None:
            for box in next_witness.new_boxes:
                self.mask[box.uid] = True

            self.working_probs = self.merge_probabilities(next_witness)
            if not self.working_probs:
                self.invalid_reasons.append(f"Problem near {next_witness.box_witness.tile.as_text()}?")
                self.held_probs = []
                break

            next_witness = self.find_next_witness(next_witness)

        if self.held_probs:
            self.calculate_box_probabilities()
        else:
            self.final_solutions_count = 0
            self.clear_count = 0

    def merge_probabilities(self, nw):
        new_probs = []
        for pl in self.working_probs:
            missing_mines = nw.box_witness.mines_to_find - self.count_placed_mines(pl, nw)
            if missing_mines < 0:
                continue
            elif missing_mines == 0:
                new_probs.append(pl)
            elif not nw.new_boxes:
                continue
            else:
                result = self.distribute_missing_mines(pl, nw, missing_mines, 0)
                new_probs.extend(result)

        nw.box_witness.processed = True
        for box in nw.new_boxes:
            box.processed = True

        boundary_boxes = [box for box in self.boxes if any(w.processed for w in box.box_witnesses) and any(not w.processed for w in box.box_witnesses)]
        sorter = MergeSorter(boundary_boxes)
        new_probs = self.crunch_by_mine_count(new_probs, sorter)
        return new_probs

    def count_placed_mines(self, pl, nw):
        return sum(pl.allocated_mines[box.uid] for box in nw.old_boxes)

    def distribute_missing_mines(self, pl, nw, missing_mines, index):
        self.recursions += 1
        if self.recursions % 1000 == 0:
            print(f"Solution Counter recursion = {self.recursions}")

        result = []
        if len(nw.new_boxes) - index == 1:
            if nw.new_boxes[index].max_mines < missing_mines or nw.new_boxes[index].min_mines > missing_mines or pl.mine_count + missing_mines > self.max_total_mines:
                return result
            result.append(self.extend_probability_line(pl, nw.new_boxes[index], missing_mines))
            return result

        max_to_place = min(nw.new_boxes[index].max_mines, missing_mines)
        for i in range(nw.new_boxes[index].min_mines, max_to_place + 1):
            npl = self.extend_probability_line(pl, nw.new_boxes[index], i)
            r1 = self.distribute_missing_mines(npl, nw, missing_mines - i, index + 1)
            result.extend(r1)
        return result

    def extend_probability_line(self, pl, new_box, mines):
        modified_tiles_count = len(new_box.tiles) - new_box.empty_tiles
        combination = SolutionCounter.SMALL_COMBINATIONS[modified_tiles_count][mines]
        new_solution_count = pl.solution_count * combination
        result = ProbabilityLine(len(self.boxes), new_solution_count)
        result.mine_count = pl.mine_count + mines
        result.mine_box_count = [pl.mine_box_count[i] * combination for i in range(len(pl.mine_box_count))]
        result.mine_box_count[new_box.uid] = mines * new_solution_count
        result.allocated_mines = pl.allocated_mines[:]
        result.allocated_mines[new_box.uid] = mines
        return result

    def store_probabilities(self):
        if not self.working_probs:
            self.held_probs = []
            return

        crunched = self.working_probs
        result = []
        for pl in crunched:
            for epl in self.held_probs:
                npl = ProbabilityLine(len(self.boxes))
                npl.mine_count = pl.mine_count + epl.mine_count
                if npl.mine_count <= self.max_total_mines:
                    npl.solution_count = pl.solution_count * epl.solution_count
                    for k in range(len(npl.mine_box_count)):
                        w1 = pl.mine_box_count[k] * epl.solution_count
                        w2 = epl.mine_box_count[k] * pl.solution_count
                        npl.mine_box_count[k] = w1 + w2
                    result.append(npl)

        result.sort(key=lambda a: a.mine_count)
        self.held_probs = []
        if not result:
            self.invalid_reasons.append(f"{self.mines_left} mines left is not enough to complete the board?")
            return

        mc = result[0].mine_count
        npl = ProbabilityLine(len(self.boxes))
        npl.mine_count = mc
        for pl in result:
            if pl.mine_count != mc:
                self.held_probs.append(npl)
                mc = pl.mine_count
                npl = ProbabilityLine(len(self.boxes))
                npl.mine_count = mc
            npl.solution_count += pl.solution_count
            for j in range(len(pl.mine_box_count)):
                npl.mine_box_count[j] += pl.mine_box_count[j]
        self.held_probs.append(npl)

    def crunch_by_mine_count(self, target, sorter):
        if not target:
            return target

        target.sort(key=lambda a: sorter.compare(a, b))
        result = []
        current = None
        for pl in target:
            if current is None:
                current = pl
            elif sorter.compare(current, pl) != 0:
                result.append(current)
                current = pl
            else:
                self.merge_line_probabilities(current, pl)
        result.append(current)
        return result

    def merge_line_probabilities(self, npl, pl):
        npl.solution_count += pl.solution_count
        for i in range(len(pl.mine_box_count)):
            if self.mask[i]:
                npl.mine_box_count[i] += pl.mine_box_count[i]

    def find_first_witness(self):
        for box_wit in self.box_witnesses:
            if not box_wit.processed:
                return NextWitness(box_wit)
        return None

    def find_next_witness(self, prev_witness):
        best_todo = 99999
        best_witness = None
        for box in self.boxes:
            if box.processed:
                for w in box.box_witnesses:
                    if not w.processed:
                        todo = sum(1 for b1 in w.boxes if not b1.processed)
                        if todo == 0:
                            return NextWitness(w)
                        elif todo < best_todo:
                            best_todo = todo
                            best_witness = w
        if best_witness is not None:
            return NextWitness(best_witness)

        nw = self.find_first_witness()
        self.store_probabilities()
        self.working_probs = [ProbabilityLine(len(self.boxes), 1)]
        self.mask = [False] * len(self.boxes)
        if not self.held_probs:
            return None
        return nw

    def calculate_box_probabilities(self):
        empty_box = [True] * len(self.boxes)
        total_tally = 0
        outside_tally = 0
        for pl in self.held_probs:
            if pl.mine_count >= self.min_total_mines:
                mult = combination(self.mines_left - pl.mine_count, self.tiles_off_edge)
                outside_tally += mult * (self.mines_left - pl.mine_count) * pl.solution_count
                total_tally += mult * pl.solution_count
                for j in range(len(empty_box)):
                    if pl.mine_box_count[j] != 0:
                        empty_box[j] = False

        if total_tally == 0:
            self.invalid_reasons.append(f"{self.mines_left} mines left is too many to place on the board?")

        if total_tally > 0:
            for i, box in enumerate(self.boxes):
                if empty_box[i]:
                    self.clear_count += len(box.tiles)
                    self.local_clears.extend(box.tiles)

        if self.tiles_off_edge != 0:
            self.off_edge_mine_tally = outside_tally // self.tiles_off_edge
        else:
            self.off_edge_mine_tally = 0

        self.final_solutions_count = total_tally

    def set_must_be_empty(self, tile):
        box = self.get_box(tile)
        if box is None:
            self.tiles_off_edge -= 1
            self.min_total_mines = max(0, self.mines_left - self.tiles_off_edge)
        else:
            box.increment_empty_tiles()
        return True

    def get_box(self, tile):
        for box in self.boxes:
            if box.contains(tile):
                return box
        return None

    def get_local_clears(self):
        return self.local_clears