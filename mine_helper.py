"""
Helper module for Minesweeper game that provides one-time Ctrl-triggered overlay functionality.
"""

from pynput import mouse, keyboard
import threading
import time
import win32gui
import win32api
import win32con
from typing import List, Set, Tuple

from core.screen import ScreenMatrix, find_board
from minesweepr import solver


# Global constants
BACKGROUND_COLOR = win32api.RGB(198, 198, 198)
RED = win32api.RGB(255, 0, 0)
GREEN = win32api.RGB(0, 255, 0)
CELL_RADIUS = 3
CELL_OFFSET = 12
PAUSE_KEY = keyboard.Key.scroll_lock
VIEW_KEY = keyboard.Key.ctrl_l

class MinesweeperOverlay:
    """Handles mouse and keyboard events, manages overlay drawing."""

    def __init__(self):
        """Initialize the overlay manager."""
        self.mouse_listener = None
        self.keyboard_listener = None
        self.is_running = True
        self.overlay_drawn = False
        self.ctrl_pressed = False
        self.is_paused = False  # Добавляем флаг для приостановки
        self.current_turns = []
        self.old_turns = []

        # Initialize Windows drawing context
        self.hwnd = win32gui.GetDesktopWindow()
        self.dc = win32gui.GetDC(0)

        # Initialize game board dimensions
        self._init_board_dimensions()

    def _init_board_dimensions(self):
        """Initialize the game board dimensions."""
        col_values, row_values, region = find_board()
        self.x1, self.y1, self.x2, self.y2 = region
        self.width = self.x2 - self.x1
        self.height = self.y2 - self.y1
        self.matrix = ScreenMatrix(row_values, col_values, region)
        print('Matrix created.')
        # self.matrix.display()

    def _clear_previous_drawing(self):
        """Clear the previous overlay by drawing over it with background color."""
        print('Clearing previous drawing.')
        self.overlay_drawn = False
        background_brush = win32gui.CreateSolidBrush(BACKGROUND_COLOR)
        background_pen = win32gui.CreatePen(win32con.PS_SOLID, 0, BACKGROUND_COLOR)

        old_brush = win32gui.SelectObject(self.dc, background_brush)
        old_pen = win32gui.SelectObject(self.dc, background_pen)

        # for turn in self.old_turns:
        #     x = turn.cell.abscoordx + CELL_OFFSET
        #     y = turn.cell.abscoordy + CELL_OFFSET
        #     win32gui.Ellipse(self.dc,
        #                      x - CELL_RADIUS,
        #                      y - CELL_RADIUS,
        #                      x + CELL_RADIUS,
        #                      y + CELL_RADIUS)

        for cell in self.matrix.get_closed_cells():
            if cell.probability not in [0, 1]:
                continue

            x = cell.abscoordx + CELL_OFFSET
            y = cell.abscoordy + CELL_OFFSET
            win32gui.Ellipse(self.dc,
                             x - CELL_RADIUS,
                             y - CELL_RADIUS,
                             x + CELL_RADIUS,
                             y + CELL_RADIUS)


        # Cleanup GDI objects
        win32gui.SelectObject(self.dc, old_brush)
        win32gui.SelectObject(self.dc, old_pen)
        win32gui.DeleteObject(background_brush)
        win32gui.DeleteObject(background_pen)

    def _draw_overlay(self):
        """Draw new overlay based on minesweepr probability solve."""
        self.matrix.update_from_screen()
        self.matrix.solve()

        self.overlay_drawn = True
        for cell in self.matrix.get_closed_cells():
            if cell.probability not in [0, 1]:
                continue

            color = GREEN if cell.probability == 0 else RED
            brush = win32gui.CreateSolidBrush(color)
            pen = win32gui.CreatePen(win32con.PS_SOLID, 0, color)

            old_brush = win32gui.SelectObject(self.dc, brush)
            old_pen = win32gui.SelectObject(self.dc, pen)

            x = cell.abscoordx + CELL_OFFSET
            y = cell.abscoordy + CELL_OFFSET
            win32gui.Ellipse(self.dc,
                             x - CELL_RADIUS,
                             y - CELL_RADIUS,
                             x + CELL_RADIUS,
                             y + CELL_RADIUS)

            # Cleanup GDI objects
            win32gui.SelectObject(self.dc, old_brush)
            win32gui.SelectObject(self.dc, old_pen)
            win32gui.DeleteObject(brush)
            win32gui.DeleteObject(pen)

    def analyze_screen(self):
        # """Analyze the screen and update turns."""
        # print('1')
        # a = time.perf_counter()
        # self.matrix.update_from_screen()
        # print(f'Screen analyzed. {time.perf_counter() - a}s')
        #
        # # self.current_turns = multi_solver(self.matrix)
        # # self.matrix.display()
        # a = time.perf_counter()
        # self.matrix.solve()
        # print(f'Matrix solved. {time.perf_counter() - a}s')
        pass

    def on_ctrl_key(self, is_pressed):
        if self.is_paused:
            return  # Если приостановлено, ничего не делаем

        if is_pressed and not self.ctrl_pressed:
            self.ctrl_pressed = True
            threading.Thread(target=self._draw_overlay).start()
        elif not is_pressed and self.ctrl_pressed:
            self.ctrl_pressed = False
            threading.Thread(target=self._clear_previous_drawing).start()

    def on_click(self, x: int, y: int, button, pressed: bool):
        """Handle mouse click events."""
        if self.is_paused:
            return  # Если приостановлено, ничего не делаем

        if not pressed:  # Only react to mouse press, not release -> switch to release
            # return
            threading.Thread(target=self.analyze_screen).start()

    def on_pause_key(self, key):
        """Handle PAUSE key events."""
        if key == PAUSE_KEY:
            self.is_paused = not self.is_paused
            print(f"Tracking {'paused' if self.is_paused else 'resumed'}.")

    def on_key_event(self, key, is_press):
        """Handle key events by calling both on_ctrl_key and on_pause_key."""

        if is_press:
            if key == VIEW_KEY:
                self.on_ctrl_key(True)
            elif key == PAUSE_KEY:
                self.on_pause_key(key)
        else:
            if key == VIEW_KEY:
                self.on_ctrl_key(False)

    def start_listening(self):
        """Start listening for mouse and keyboard events."""
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.keyboard_listener = keyboard.Listener(
            on_press=lambda key: self.on_key_event(key, True),
            on_release=lambda key: self.on_key_event(key, False)
        )

        self.mouse_listener.start()
        self.keyboard_listener.start()
        print("Mouse and keyboard tracking started...")

    def start_listening1(self):
        """Start listening for mouse and keyboard events."""
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.keyboard_listener = keyboard.Listener(
            on_press=lambda key: self.on_ctrl_key(True) if key == VIEW_KEY else None,
            on_release=lambda key: self.on_ctrl_key(False) if key == VIEW_KEY else None,
        )

        self.mouse_listener.start()
        self.keyboard_listener.start()
        print("Mouse and keyboard tracking started...")

    def stop_listening(self):
        """Stop listening for events and cleanup resources."""
        self.is_running = False
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener.join()

        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener.join()

        # Cleanup Windows resources
        win32gui.InvalidateRect(self.hwnd, None, True)
        win32gui.ReleaseDC(self.hwnd, self.dc)

        print("Tracking stopped.")


def main():
    """Main entry point of the helper application."""
    try:
        overlay_manager = MinesweeperOverlay()
        overlay_manager.start_listening()

        # Keep the program running
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        overlay_manager.stop_listening()


if __name__ == "__main__":
    main()
