import tkinter as tk
from mine_tk import MinesweeperApp
import time


def on_highlight(row, col, color):
    print(f"Cell highlighted: {row}, {col} with color {color}")


def main():
    root = tk.Tk()
    app = MinesweeperApp(root)

    # Регистрируем обработчик событий
    app.register_handler('on_cell_highlight', on_highlight)

    # Получаем информацию об окне
    # BY SWASHER: это непонятно, зачем нужно, нигде не используется
    window_info = app.get_window_info()
    print(f"Window size: {window_info['width']}x{window_info['height']}")

    # Запускаем подсветку ячеек в отдельном потоке
    def highlight_cells():
        time.sleep(2)  # Ждем, пока окно откроется
        for row in range(3):
            for col in range(3):
                app.highlight_cell(row, col, color='red', duration_ms=200)
                time.sleep(0.3)

    import threading
    threading.Thread(target=highlight_cells, daemon=True).start()

    # Запускаем главный цикл
    root.mainloop()


if __name__ == "__main__":
    main()



##########################
# SAMPLE MINESWEEPER CLASS
##########################

class MinesweeperApp:
    def __init__(self, root, matrix_file=None):
        # ... существующий код ...

        # Добавляем словарь для хранения внешних обработчиков событий
        self.external_handlers = {
            'on_cell_highlight': None,
            'on_cell_click': None,
            'on_game_state_change': None
        }

    def register_handler(self, event_name: str, handler_function):
        """
        Регистрирует внешний обработчик событий

        Args:
            event_name: Название события ('on_cell_highlight', 'on_cell_click', 'on_game_state_change')
            handler_function: Функция-обработчик
        """
        if event_name in self.external_handlers:
            self.external_handlers[event_name] = handler_function

    def highlight_cell(self, row: int, col: int, color: str = 'yellow', duration_ms: int = 500):
        """
        Подсвечивает указанную ячейку

        Args:
            row: Номер строки
            col: Номер столбца
            color: Цвет подсветки (любой валидный цвет Tkinter)
            duration_ms: Продолжительность подсветки в миллисекундах
        """
        if not (0 <= row < self.grid_height and 0 <= col < self.grid_width):
            raise ValueError(f"Invalid cell coordinates: {row}, {col}")

        coords = self.cells[(row, col)]['coords']

        # Удаляем старую подсветку
        self.canvas.delete('highlight')

        # Создаем новую подсветку
        highlight = self.canvas.create_rectangle(
            coords[0], coords[1], coords[2], coords[3],
            fill=color,
            stipple='gray50',
            tags='highlight'
        )

        self.canvas.tag_lower(highlight, self.cells[(row, col)]['id'])

        # Уведомляем внешний обработчик
        if self.external_handlers['on_cell_highlight']:
            self.external_handlers['on_cell_highlight'](row, col, color)

        # Убираем подсветку через указанное время
        self.root.after(duration_ms, lambda: self.canvas.delete('highlight'))

    def get_window_info(self) -> dict:
        """Возвращает информацию об окне приложения"""
        return {
            'width': self.grid_width,
            'height': self.grid_height,
            'window_rect': GetWindowRect(GetForegroundWindow()),
            'cell_size': self.cell_size
        }