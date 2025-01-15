 class GameState:
    """Хранит состояние игры"""
    def __init__(self, config: GameConfig):
        self.matrix = PlayMatrix(config.width, config.height)
        self.mode = Mode.play
        self.mine_mode = MineMode.PREDEFINED
        self.game_status = GameStatus.waiting
        
    @property
    def mine_count(self) -> int:
        return len(self.matrix.get_mined_cells())


from typing import List, Callable



class GameState:

    """Хранит состояние игры"""

    def __init__(self, config: GameConfig):

        self.matrix = PlayMatrix(config.width, config.height)

        self.mode = Mode.play

        self.mine_mode = MineMode.PREDEFINED

        self.game_status = GameStatus.waiting

        self._observers: List[Callable] = []

        

    @property

    def mine_count(self) -> int:

        return len(self.matrix.get_mined_cells()) 

        

    def add_observer(self, callback: Callable):

        self._observers.append(callback)

        

    def notify_observers(self):

        for callback in self._observers:

            callback()

            

    def click_cell(self, cell: Cell):

        # Изменяем состояние

        self.matrix.click_play_left_button(cell)

        # Уведомляем наблюдателей

        self.notify_observers() 
