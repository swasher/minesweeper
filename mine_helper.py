from pynput import mouse
import threading
import time

from core.screen import ScreenMatrix
from core.screen import find_board


def do_something():
    """
    Пример функции, которая будет выполняться при клике мыши.
    В данном случае просто выводит сообщение и имитирует некоторую работу.
    """
    matrix.update()
    matrix.display()

class MouseListener:
    def __init__(self):
        self.listener = None
        self.worker_thread = None
        self.is_running = True

    def on_click(self, x, y, button, pressed):
        """Обработчик события клика мыши"""
        if pressed:  # Реагируем только на нажатие, не на отпускание
            # Запускаем обработку в отдельном потоке
            if self.worker_thread is None or not self.worker_thread.is_alive():
                self.worker_thread = threading.Thread(target=do_something)
                self.worker_thread.start()

    def start_listening(self):
        """Запуск прослушивания событий мыши"""
        self.listener = mouse.Listener(on_click=self.on_click)
        self.listener.start()
        print("Отслеживание кликов мыши запущено...")

    def stop_listening(self):
        """Остановка прослушивания"""
        self.is_running = False
        if self.listener:
            self.listener.stop()
            self.listener.join()
        print("Отслеживание остановлено.")

if __name__ == "__main__":
    col_values, row_values, region = find_board()

    matrix = ScreenMatrix(row_values, col_values, region)
    print('Matrix creted:')
    matrix.display()

    try:
        # Создаем и запускаем прослушиватель
        mouse_listener = MouseListener()
        mouse_listener.start_listening()

        # Держим программу запущенной
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Корректное завершение при нажатии Ctrl+C
        mouse_listener.stop_listening()
