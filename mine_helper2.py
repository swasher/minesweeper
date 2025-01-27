"""
Helper module for Minesweeper game that provides overlay functionality.
"""

from pynput import mouse
import threading
import time
import win32gui
import win32api
import win32con
from typing import List, Set, Tuple

from core.screen import ScreenMatrix, find_board
from solver import multi_solver

# Global constants
BACKGROUND_COLOR = win32api.RGB(198, 198, 198)
RED = win32api.RGB(255, 0, 0)
GREEN = win32api.RGB(0, 255, 0)
BLUE = win32api.RGB(0, 0, 255)
CELL_RADIUS = 3
CELL_OFFSET = 12


class MouseListener:
    """Handles mouse events and manages overlay drawing."""

    def __init__(self):
        """Initialize the mouse listener."""
        self.listener = None
        self.worker_thread = None
        self.is_running = True
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
        print('Matrix created:')
        self.matrix.display()

    def _clear_previous_drawing(self):
        """Clear the previous overlay by drawing over it with background color."""
        background_brush = win32gui.CreateSolidBrush(BACKGROUND_COLOR)
        background_pen = win32gui.CreatePen(win32con.PS_SOLID, 0, BACKGROUND_COLOR)

        old_brush = win32gui.SelectObject(self.dc, background_brush)
        old_pen = win32gui.SelectObject(self.dc, background_pen)

        for turn in self.old_turns:
            x = turn.cell.abscoordx + CELL_OFFSET
            y = turn.cell.abscoordy + CELL_OFFSET
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

    def _draw_overlay(self, turns):
        """Draw new overlay based on solver results."""
        for turn in turns:
            if turn.probability not in (0, 1):
                continue

            color = GREEN if turn.probability == 0 else RED
            brush = win32gui.CreateSolidBrush(color)
            pen = win32gui.CreatePen(win32con.PS_SOLID, 0, color)

            old_brush = win32gui.SelectObject(self.dc, brush)
            old_pen = win32gui.SelectObject(self.dc, pen)

            x = turn.cell.abscoordx + CELL_OFFSET
            y = turn.cell.abscoordy + CELL_OFFSET
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

    def update_overlay(self):
        """Update the overlay with new solver results."""
        self.matrix.update_from_screen()
        self.matrix.display()
        turns = multi_solver(self.matrix)

        self._clear_previous_drawing()
        self._draw_overlay(turns)

        self.old_turns = turns

    def on_click(self, x: int, y: int, button, pressed: bool):
        """Handle mouse click events."""
        if not pressed:  # Only react to mouse press, not release
            return

        if self.worker_thread is None or not self.worker_thread.is_alive():
            self.worker_thread = threading.Thread(target=self.update_overlay)
            self.worker_thread.start()

    def start_listening(self):
        """Start listening for mouse events."""
        self.listener = mouse.Listener(on_click=self.on_click)
        self.listener.start()
        print("Mouse click tracking started...")

    def stop_listening(self):
        """Stop listening for mouse events and cleanup resources."""
        self.is_running = False
        if self.listener:
            self.listener.stop()
            self.listener.join()

        # Cleanup Windows resources
        win32gui.InvalidateRect(self.hwnd, None, True)
        win32gui.ReleaseDC(self.hwnd, self.dc)

        print("Tracking stopped.")


def main():
    """Main entry point of the helper application."""
    try:
        mouse_listener = MouseListener()
        mouse_listener.start_listening()

        # Keep the program running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        mouse_listener.stop_listening()


if __name__ == "__main__":
    main()
