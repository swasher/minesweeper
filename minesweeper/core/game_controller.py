from typing import Callable
from functools import debounce
from enum import Enum

class GameController:
    """
    Контроллер игры, управляющий взаимодействием между UI и игровым состоянием.
    Реализует паттерн MVC, где:
    - Model: GameState
    - View: GameUI
    - Controller: GameController
    """
    def __init__(self, ui: GameUI, state: GameState):
        self.ui = ui
        self.state = state
        
        # Подписываемся на изменения состояния
        self.state.add_observer(self.on_state_changed)
        
        # Связываем обработчики UI событий
        self.ui.bind_cell_click(self.on_cell_click)
        self.ui.top_panel.bind_reset(self.on_reset_click)
        self.ui.top_panel.bind_mode_change(self.on_mode_change)
        self.ui.bind_menu_new_game(self.on_new_game)
        self.ui.bind_menu_save(self.on_save_game)
        self.ui.bind_menu_load(self.on_load_game)
        
        # Инициализируем начальное состояние UI
        self.update_ui()

    def on_state_changed(self):
        """Вызывается при любом изменении состояния игры"""
        self.update_ui()
        self.check_game_end()

    @debounce(0.1)  # Предотвращаем слишком частое обновление UI
    def update_ui(self):
        """Синхронизирует UI с текущим состоянием игры"""
        # Обновляем игровое поле
        for row in range(self.state.matrix.height):
            for col in range(self.state.matrix.width):
                cell = self.state.matrix.table[row][col]
                self.ui.update_cell(row, col, cell.content)
        
        # Обновляем счетчики и статусы
        self.ui.update_mine_counter(self.state.mine_count)
        self.ui.update_game_status(self.state.game_status)
        self.ui.update_mode(self.state.mode)
        self.ui.update_mine_mode(self.state.mine_mode)
        
        # Обновляем состояние кнопок
        self.ui.update_controls_state(
            can_save=self.state.game_status != GameStatus.waiting,
            can_edit=self.state.game_status != GameStatus.fail
        )

    def on_cell_click(self, row: int, col: int, button: MouseButton):
        """Обработчик клика по ячейке"""
        try:
            cell = self.state.matrix.table[row][col]
            
            if self.state.game_status == GameStatus.waiting:
                self.state.start_game()
            
            if button == MouseButton.left:
                self.handle_left_click(cell)
            elif button == MouseButton.right:
                self.handle_right_click(cell)
            elif button == MouseButton.middle:
                self.handle_middle_click(cell)
                
        except Exception as e:
            self.ui.show_error(f"Error processing click: {str(e)}")

    def handle_left_click(self, cell: Cell):
        """Обработка левого клика мыши"""
        if self.state.mode == Mode.play:
            if not cell.is_flag:  # Нельзя открывать ячейки с флагом
                self.state.click_cell(cell)
        else:  # Mode.edit
            if self.state.mine_mode == MineMode.PREDEFINED:
                self.state.toggle_mine(cell)
            else:
                self.state.increment_digit(cell)

    def handle_right_click(self, cell: Cell):
        """Обработка правого клика мыши"""
        if self.state.mode == Mode.play:
            self.state.toggle_flag(cell)
        else:  # Mode.edit
            if self.state.mine_mode == MineMode.PREDEFINED:
                self.state.remove_mine(cell)
            else:
                self.state.decrement_digit(cell)

    def handle_middle_click(self, cell: Cell):
        """Обработка среднего клика мыши (колесико)"""
        if self.state.mode == Mode.play and cell.is_digit:
            self.state.chord_click(cell)

    def on_reset_click(self):
        """Обработчик нажатия кнопки сброса (смайлик)"""
        self.state.reset_game()

    def on_mode_change(self, new_mode: Mode):
        """Обработчик смены режима игры"""
        if self.can_change_mode(new_mode):
            self.state.mode = new_mode
            self.update_ui()
        else:
            self.ui.show_error("Cannot change mode in current game state")

    def on_new_game(self, config: GameConfig):
        """Обработчик создания новой игры"""
        self.state.create_new_game(config)

    def on_save_game(self):
        """Обработчик сохранения игры"""
        try:
            self.state.save_game()
            self.ui.show_info("Game saved successfully")
        except Exception as e:
            self.ui.show_error(f"Error saving game: {str(e)}")

    def on_load_game(self, file_path: str):
        """Обработчик загрузки игры"""
        try:
            self.state.load_game(file_path)
            self.ui.show_info("Game loaded successfully")
        except Exception as e:
            self.ui.show_error(f"Error loading game: {str(e)}")

    def check_game_end(self):
        """Проверяет условия окончания игры"""
        if self.state.game_status == GameStatus.win:
            self.ui.show_win_dialog()
        elif self.state.game_status == GameStatus.fail:
            self.ui.show_fail_dialog()

    def can_change_mode(self, new_mode: Mode) -> bool:
        """Проверяет, можно ли переключить режим"""
        if new_mode == Mode.edit:
            return self.state.game_status != GameStatus.fail
        return True
