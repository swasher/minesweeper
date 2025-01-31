"""

КОРОЧЕ, НУЖНО ПРИЙТИ К ТАКОМУ СОГЛАШЕНИЮ ВО ==ВСЕМ== ПРОЕКТЕ:

БОМБЫ - (BOMBS) - ЭТО АССЕТЫ (И СОДЕРЖИМОЕ) ЯЧЕЕК *ПОСЛЕ* ОКОНЧАНИЯ ИГРЫ, КОГДА ЮЗЕР ВЗОРВАЛСЯ

МИНЫ (MINES) - ЭТО БОМБЫ, КОТОРЫЕ МЫ ИСПОЛЬЗУЕМ В ИГРЕ TK.

Соотв,

cell.is_bomb - это если бомба после взрыва (в игре с экрана)
cell.is_mine - это спрятанная в ячейке бомба (в сете matrix.mines)

"""

# 💣🚩
# TODO При редактировании проверять поле на валидность
# TODO Сделать расширенный режим генерации поля с проверками на валидность 
# TODO пока юзер держит мышку, закрытые ячейки вокруг визуально меняем на открытые (как-бы подсвечиваем)

import os
import argparse
import time
from pathlib import Path
from win32gui import GetWindowRect, GetForegroundWindow
from enum import IntEnum

from typing import Callable
from typing import Literal

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import font
from tktooltip import ToolTip

from core.tk import TkMatrix
from core import MineMode
from core import Cell
from core import Game
from core import GameState
from core import beginner, beginner_new, intermediate, expert
from mouse_controller import MouseButton
from assets import *

from minesweepr import InconsistencyError


class Mode(IntEnum):
    play = 0
    edit = 1


class FieldConsistency(IntEnum):
    VALID = 0
    INVALID = 1
    UNKNOWN = 2


class Constants:
    MIN_GRID_SIZE = 1
    MAX_GRID_SIZE = 50
    TIMER_UPDATE_MS = 1000
    DEFAULT_CELL_SIZE = 24
    MIN_WINDOW_WIDTH = 195
    MIN_WINDOW_HEIGHT = 265

class GameTimer:
    def __init__(self, update_callback: Callable[[int], None], root):
        """
        Инициализация таймера

        Args:
            update_callback: функция, которая будет вызываться при каждом обновлении времени
                           принимает один аргумент - количество прошедших секунд
            root: главное окно Tkinter (для использования метода after)
        """
        self.seconds = 0
        self.is_running = False
        self.update_callback = update_callback
        self.root = root

    def _timer_loop(self):
        """Основной цикл таймера"""
        if self.is_running:
            self.seconds += 1
            self.update_callback(self.seconds)
            # Планируем следующий вызов через 1 секунду
            self.root.after(Constants.TIMER_UPDATE_MS, self._timer_loop)

    def start(self):
        """Запуск таймера"""
        if not self.is_running:
            self.is_running = True
            self._timer_loop()

    def stop(self):
        """Остановка таймера"""
        self.is_running = False

    def reset(self):
        """Сброс таймера"""
        self.seconds = 0
        self.is_running = False
        self.update_callback(0)

    def get_time(self) -> int:
        """Получить текущее время в секундах"""
        return self.seconds


class MinesweeperApp:
    def __init__(self, root, matrix_file=None):
        self.root = root
        root.resizable(False, False)
        self.root.geometry("300x300")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)  # Bind the close event

        # Определение шрифтов
        self.segoe_normal = font.Font(family="Segoe UI", size=10, weight="normal")
        self.segoe_bold = font.Font(family="Segoe UI", size=10, weight="bold")

        self.current_game = beginner
        self.grid_width = self.current_game.width
        self.grid_height = self.current_game.height
        self.cell_size = Constants.DEFAULT_CELL_SIZE  # размер ячейки в px
        self.root.title(f"Minesweeper {self.grid_width}x{self.grid_height}")

        self.timer = GameTimer(self.update_timer_display, root)

        self.matrix = TkMatrix(height=self.grid_height, width=self.grid_width)
        self.matrix.create_new_game(n_bombs=self.current_game.bombs)

        self.edit_mode = Mode.edit
        self._edit_mode = tk.BooleanVar(value=False)
        # self._mine_mode_var = tk.IntVar(value=MineMode.PREDEFINED)  # доступ к свойсву Matrix.mine_mode осуществляется через прокси сеттер-геттер MinesweeperApp.mine_mode
        self._consistency = FieldConsistency.UNKNOWN
        self._show_probability = tk.BooleanVar(value=False)

        self.load_images()
        self.cells = {}

        self.create_top_frame()
        self.create_sidebar()
        self.create_status_bar()
        self.create_menu()
        self.create_canvas()

        self.create_fresh_board(game=beginner)
        self.update_mine_counter()

        # Bind canvas events
        # self.canvas.bind("<Button-1>", self.on_canvas_click_left)
        self.canvas.bind("<Button-2>", self.on_canvas_click_middle)  # for testing purpose
        self.canvas.bind("<Button-3>", self.on_canvas_click_right)

        # Add new mouse press/release bindings
        # Левую кнопку мы отдельно обрабатываем нажатия и отпускания.
        # При нажатии подсвечиваем вокруг закрытые ячейки, а при отпускании выполняем логику.
        # Так же если нажата закрытая ячейка, то на время нажатия она становится n0 (вдавленной)
        self.canvas.bind("<ButtonPress-1>", self.on_left_mouse_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_left_mouse_release)

        if matrix_file:
            self.load_matrix(matrix_file)

        # Добавляем словарь для хранения внешних обработчиков событий
        # ДЛЯ ВНЕШНЕЙ ПОДСВЕТКИ ЯЧЕЕК
        self.external_handlers = {
            'on_cell_highlight': None,
            'on_cell_click': None,
            'on_game_state_change': None
        }

    @property
    def mine_mode(self) -> MineMode:
        """GETTER. Возвращает режим расположения мин
        Фактически proxy к свойству основного объекта Matrix.
        """
        return self.matrix.mine_mode

    @mine_mode.setter
    def mine_mode(self, mode: MineMode):
        """SETTER. Устанавливает режим расположения мин
        Фактически proxy к свойству основного объекта Matrix.
        """
        self.matrix.mine_mode = mode
        # deprecated self._mine_mode_var.set(mode.value)

    @property
    def consistency(self) -> FieldConsistency:
        """GETTER. Возвращает состояние игрового поля"""
        return self._consistency

    @consistency.setter
    def consistency(self, value: FieldConsistency):
        """SETTER. Устанавливает состояние игрового поля"""
        self._consistency = value
        self.consistency_label = value.name

    def load_images(self):
        self.images = {
            "closed": tk.PhotoImage(file=closed.filename),
            "bomb": tk.PhotoImage(file=bomb.filename),
            "bomb_red": tk.PhotoImage(file=bomb_red.filename),
            "bomb_wrong": tk.PhotoImage(file=bomb_wrong.filename),
            "flag": tk.PhotoImage(file=flag.filename),
            "there_is_bomb": tk.PhotoImage(file=there_is_bomb.filename),
            "there_is_bomb_": tk.PhotoImage(file=there_is_bomb.filename),
            "0": tk.PhotoImage(file=n0.filename),
            "1": tk.PhotoImage(file=n1.filename),
            "2": tk.PhotoImage(file=n2.filename),
            "3": tk.PhotoImage(file=n3.filename),
            "4": tk.PhotoImage(file=n4.filename),
            "5": tk.PhotoImage(file=n5.filename),
            "6": tk.PhotoImage(file=n6.filename),
            "7": tk.PhotoImage(file=n7.filename),
            "8": tk.PhotoImage(file=n8.filename),
            "led0": tk.PhotoImage(file=led0.filename),
            "led1": tk.PhotoImage(file=led1.filename),
            "led2": tk.PhotoImage(file=led2.filename),
            "led3": tk.PhotoImage(file=led3.filename),
            "led4": tk.PhotoImage(file=led4.filename),
            "led5": tk.PhotoImage(file=led5.filename),
            "led6": tk.PhotoImage(file=led6.filename),
            "led7": tk.PhotoImage(file=led7.filename),
            "led8": tk.PhotoImage(file=led8.filename),
            "led9": tk.PhotoImage(file=led9.filename),
            "face_smile": tk.PhotoImage(file=smile.filename),
            "face_win": tk.PhotoImage(file=win.filename),
            "face_fail": tk.PhotoImage(file=fail.filename),
        }

    def create_top_frame(self):
        self.top_frame = tk.Frame(self.root, padx=3, pady=3)
        self.top_frame.grid(row=0, column=0, columnspan=2, sticky='we')

        # Left frame for mine counter
        self.left_frame = tk.Frame(self.top_frame, bg='lightgrey')
        self.left_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.mine_counter = [tk.Label(self.left_frame, image=self.images["led0"]) for _ in range(3)]
        for i, label in enumerate(self.mine_counter):
            label.pack(side=tk.LEFT)

        # Center frame for smile
        self.center_frame = tk.Frame(self.top_frame, bg='lightgrey')
        self.center_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.smile = tk.Button(self.center_frame,
                               image=self.images["face_smile"],
                               highlightthickness=0,
                               borderwidth=0,
                               command=lambda: self.create_fresh_board(game=self.current_game))
        self.smile.pack(expand=True)

        # Right frame for LED timer
        self.right_frame = tk.Frame(self.top_frame, bg='lightgrey')
        self.right_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.led_timer = [tk.Label(self.right_frame, image=self.images["led0"]) for _ in range(3)]
        for label in reversed(self.led_timer):
            label.pack(side=tk.RIGHT)

    def create_menu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)
        file_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save matrix", command=self.save_matrix)
        file_menu.add_command(label="Load matrix", command=self.load_matrix)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        size_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="New game", menu=size_menu)
        size_menu.add_command(label="Beginner (9x9)", command=lambda: self.create_fresh_board(game=beginner))
        size_menu.add_command(label="Intermediate (16x16)", command=lambda: self.create_fresh_board(game=intermediate))
        size_menu.add_command(label="Expert (30x16)", command=lambda: self.create_fresh_board(game=expert))
        size_menu.add_command(label="Custom", command=self.create_fresh_board)

    def create_sidebar(self):
        self.sidebar = tk.Frame(self.root, width=83, height=200, padx=3, bg='lightgrey')

        # self.sidebar.grid(row=1, column=0, rowspan=self.grid_height, sticky='ns')
        # Добавляем rowspan и sticky
        self.sidebar.grid(row=1, column=0, rowspan=1, sticky='nsw')  # rowspan=1 вместо self.grid_height

        self.sidebar.grid_propagate(False)  # Prevent the sidebar from resizing based on its children

        # Edit mode button
        self.edit_button = tk.Button(master=self.sidebar,
                                     text="Edit mode",
                                     font=self.segoe_bold,
                                     command=lambda: self.switch_edit_mode(Mode.edit))
        self.edit_button.grid(row=0, column=0, pady=5)
        ToolTip(self.edit_button, msg="Для Edit Mode нужно установить соотв. Mines Mode. Левая кнопка - ставить флаги.")

        # Mine mode checkbox
        self.label_mine_mode = tk.Label(self.sidebar, text="Mine Mode", bg='lightgrey')
        self.label_mine_mode.grid(row=2, column=0, pady=(0, 0))

        self.checkbutton_mine_mode = tk.Checkbutton(master=self.sidebar, text="",
                                                    command=self.switch_mine_mode,
                                                    # variable=self._mine_mode_var,
                                                    bg='lightgrey',
                                                    onvalue=MineMode.UNDEFINED.value,
                                                    offvalue=MineMode.PREDEFINED.value
                                                    )
        self.checkbutton_mine_mode.grid(row=3, column=0, pady=0)
        ToolTip(self.checkbutton_mine_mode, msg="ON - Мы устанавливаем мины, цифры ставятся автоматически."
                                          " OFF - Мы устанавливаем цифры, положение мин в матрице неопределено")
        self.checkbutton_mine_mode.select() if self.mine_mode == MineMode.PREDEFINED else self.checkbutton_mine_mode.deselect()

        # Play mode button
        self.play_button = tk.Button(master=self.sidebar,
                                     text="Play mode",
                                     font=self.segoe_normal,
                                     command=lambda: self.switch_edit_mode(Mode.play)
                                     )
        self.play_button.grid(row=4, column=0, pady=5)
        ToolTip(self.play_button, msg="Выходим из режима редактирования, и можем 'играть' в текущее поле")

        # Probability checkbox
        self.checkbutton_showprob = tk.Checkbutton(master=self.sidebar, text="Prob.", variable=self._show_probability, command=self.switch_probality, bg='lightgrey')
        self.checkbutton_showprob.grid(row=5, column=0, pady=0)
        ToolTip(self.checkbutton_showprob, msg="Показывать вероятность мины в каждой клетке")

        # Consistency Label
        self.consistency_label_head = tk.Label(self.sidebar, text="Consistency:", bg='lightgrey')
        self.consistency_label = tk.Label(self.sidebar, text="GOOD", bg='lightgrey')
        self.consistency_label_head.grid(row=6, column=0, pady=(0, 0))
        self.consistency_label.grid(row=7, column=0, pady=(0, 0))

    def create_status_bar(self):
        self.status_bar_frame = tk.Frame(self.root)
        self.status_bar_frame.grid(row=2, column=0, columnspan=2, sticky='ew')

        self.status_bar = tk.Label(self.status_bar_frame, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        # self.status_bar.grid(row=0, column=0, sticky='nsew')
        self.status_bar.pack(fill=tk.X)  # Используем pack вместо grid для label

    def create_canvas(self):
        # Add this line to properly place the grid_frame
        self.grid_frame = tk.Frame(self.root)
        # self.grid_frame.grid(row=1, column=1, sticky='nw')
        # Добавляем rowspan
        self.grid_frame.grid(row=1, column=1, rowspan=1, sticky='nw')  # rowspan=1

        # В canvas располагаются собственно ячейки
        self.canvas = tk.Canvas(
            self.grid_frame,
            width=self.grid_width * self.cell_size,
            height=self.grid_height * self.cell_size,
            highlightthickness=0,  # Remove border
            bg='lightgray'  # Add background color to see canvas bounds
        )
        self.canvas.grid(row=0, column=0, sticky='nw')

    def create_fresh_board(self, game: Game = None):
        print('Starting new game')
        if not game:
            size = simpledialog.askstring("Custom Size", "Enter width, height and bombs (e.g., 30x16x99):")
            try:
                width, height, bombs = map(int, size.split('x'))
                game = Game(width, height, bombs)
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter valid ints separated by 'x'.")

        self.timer.reset()
        self.set_custom_size(game)
        self.matrix = TkMatrix(self.grid_width, self.grid_height, game.bombs)
        self.matrix.create_new_game(n_bombs=game.bombs)
        print('State:', self.matrix.game_state.name)
        self.set_smile(self.matrix.game_state)

        self.update_mine_counter()
        self.update_grid()
        self.matrix.display()

    def set_custom_size(self, game: Game = None):
        """
        Инициализирует размеры игрового поля для размеров игры game.
        """
        width, height, bombs = game.width, game.height, game.bombs

        if (Constants.MIN_GRID_SIZE <= width <= Constants.MAX_GRID_SIZE
                and Constants.MIN_GRID_SIZE <= height <= Constants.MAX_GRID_SIZE):

            self.current_game = game
            self.grid_width = width
            self.grid_height = height

            # canvas_width = max(, 200)
            # canvas_height = max(, 200)

            # Update canvas size
            self.canvas.config(
                width=self.grid_width * self.cell_size,
                height=self.grid_height * self.cell_size
            )
            self.fill_canvas()

            self.root.update_idletasks()  # Ensure the grid is created before resizing
            geom_x = self.cell_size * width + self.sidebar.winfo_width()
            geom_y = self.cell_size * height + self.status_bar_frame.winfo_height() + self.top_frame.winfo_height()
            geom_x = max(geom_x, Constants.MIN_WINDOW_WIDTH)
            geom_y = max(geom_y, Constants.MIN_WINDOW_HEIGHT)
            self.root.geometry(f"{geom_x}x{geom_y}")
            self.root.title(f"Minesweeper {self.grid_width}x{self.grid_height}")
            print(f'Successfully set grid size to {width}x{height} and window to {geom_x}x{geom_y}')
        else:
            messagebox.showerror("Invalid Size", "Width and height must be between 1 and 50.")

    def fill_canvas(self):
        """Create grid using canvas"""
        # Clear existing canvas items
        self.canvas.delete("all")

        # Update canvas size
        self.canvas.config(
            width=self.grid_width * self.cell_size,
            height=self.grid_height * self.cell_size
        )

        # Create cells
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                # Calculate pixel coordinates
                x1 = col * self.cell_size  # Changed from y to col
                y1 = row * self.cell_size  # Changed from x to row
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                # Create cell image on canvas
                cell_id = self.canvas.create_image(
                    x1,  # Left coordinate
                    y1,  # Top coordinate
                    image=self.images["closed"],
                    anchor="nw",  # Anchor to top-left corner
                    tags=f"cell_{row}_{col}"  # Changed from x,y to row,col
                )

                # Store cell coordinates for later reference
                self.cells[(row, col)] = {
                    'id': cell_id,
                    'coords': (x1, y1, x2, y2)
                }

        # Force update
        self.canvas.update()

    def update_status_bar(self):
        if self.matrix.game_state == GameState.win:
            self.status_bar.config(text="You win!")
        elif self.matrix.game_state == GameState.fail:
            self.status_bar.config(text="You lose!")
        else:
            closed_count = self.matrix.get_closed_cells_count
            mine_count = self.matrix.get_total_mines
            opened_count = self.matrix.get_opened_cells_count
            flag_count = self.matrix.get_flagged_cells_count
            self.status_bar.config(text=f"Closed:{closed_count}, Mines:{mine_count}, Open:{opened_count}, Flags:{flag_count}")

    def update_grid(self):
        """
        Обновляет визуальное отображение в соответствии с объектом Matrix
        """
        print('Updating grid...')
        print('Probab is', self._show_probability.get())
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                cell = self.matrix.table[row][col]
                image_name = cell.content.name
                cell_id = self.cells[(row, col)]['id']

                if image_name in self.images:
                    cell_is_closed = cell.is_closed
                    if self.edit_mode == Mode.edit and self.mine_mode == MineMode.PREDEFINED and cell_is_closed and cell.is_mined:
                        img = self.images['there_is_bomb']
                    else:
                        img = self.images[image_name]

                    # Update cell image
                    self.canvas.itemconfig(cell_id, image=img)
                else:
                    raise Exception('Not acceptable image')

                # Удаляем старый текст и точки вероятности (если есть)
                self.canvas.delete(f"prob_{row}_{col}")
                self.canvas.delete(f"dot_{row}_{col}")

                if self._show_probability.get() and cell.is_closed:
                    # Добавляем текст с вероятностью
                    if cell.probability is not None:
                        x1, y1, x2, y2 = self.cells.get((row, col))['coords']
                        # Вычисляем центр ячейки
                        center_x = (x1 + x2) / 2
                        center_y = (y1 + y2) / 2

                        if cell.probability == 1.0:
                            # Красная точка для вероятности 1.0
                            self.canvas.create_oval(
                                center_x - 2, center_y - 2,
                                center_x + 2, center_y + 2,
                                fill="red",
                                outline="",
                                tags=f"dot_{row}_{col}"
                            )
                        elif cell.probability == 0.0:
                            # Зеленая точка для вероятности 0.0
                            self.canvas.create_oval(
                                center_x - 2, center_y - 2,
                                center_x + 2, center_y + 2,
                                fill="green",
                                outline="",
                                tags=f"dot_{row}_{col}"
                            )
                        elif cell.probability is not None:
                            # Текст с вероятностью для остальных значений
                            self.canvas.create_text(
                                center_x,
                                center_y,
                                text=f"{cell.probability:.2f}",
                                font=("Arial", 6),
                                fill="black",
                                tags=f"prob_{row}_{col}"
                            )

        self.update_status_bar()

    def update_mine_counter(self):
        count = self.matrix.get_remaining_mines_count
        count_str = f"{count:03d}"
        print(f'Mines for LED: {count_str}')
        for i, digit in enumerate(count_str):
            try:
                self.mine_counter[i].config(image=self.images[f"led{digit}"])
            except:
                print('ERROR! Невозможно преобразовать get_remaining_mines_count в LED. Value:', count)

    def update_timer_display(self, seconds: int):
        # Обновление отображения времени в интерфейсе
        time_str = f"{seconds:03d}"
        for i, digit in enumerate(time_str):
            self.led_timer[i].config(image=self.images[f"led{digit}"])

    def update_total_mines(self):
        self.matrix.total_mines = len(self.matrix.mines)

    def switch_probality(self):
        """
        Значение чекбокса хранится в self._show_probability, а переключение осуществляется автоматом, потому что эта переменная указана в свойствах чекбокса.
        """
        if self._show_probability.get():
            # При включении чекбокса обновляем вероятности
            self.matrix.solve()
        self.update_grid()

    def switch_mine_mode(self):
        if self.matrix.mine_mode == MineMode.PREDEFINED:
            response = messagebox.askyesno("Warning",
                                           "Это удалит все установленные мины с поля.")
            if response:
                self.mine_mode = MineMode.UNDEFINED
                self.checkbutton_mine_mode.deselect()

                self.matrix.mines = set()
                self.label_mine_mode.config(text="(Set Digits)")
                self.update_grid()

                print("Switched to mine mode: OFF")
        else:
            response = messagebox.askyesno("Warning",
                                           "Все цифры станут просто открытыми ячейками (0). Можно будет расставить бомбы")
            if response:
                self.mine_mode = MineMode.PREDEFINED
                self.checkbutton_mine_mode.select()

                digit_cells = self.matrix.get_digit_cells()
                for cell in digit_cells:
                    cell.content = n0
                self.label_mine_mode.config(text="(Set Bombs)")
                self.update_grid()

                print("Switched to mine mode: ON")

    def switch_edit_mode(self, mode: Mode):
        """
        Switch from Edit to Play mode and back.
        :param mode: New mode to set
        """
        # Проверка валидности смены режима
        if mode == self.edit_mode:
            return

        if mode == Mode.play and self.mine_mode == MineMode.UNDEFINED:
            print("Cannot switch to play mode: mines are not defined")
            return

        if mode == Mode.edit:
            self.timer.stop()
        if mode == Mode.play and self.matrix.game_state is GameState.playing:
            self.timer.start()

        # Обновление режима
        print(f"Switch mode to: {mode.name}")
        self.edit_mode = mode

        # Обновление UI
        edit_font = self.segoe_bold if mode == Mode.edit else self.segoe_normal
        play_font = self.segoe_bold if mode == Mode.play else self.segoe_normal
        # self.edit_button.config(font=("Helvetica", 10, edit_font))

        self.edit_button.config(font=edit_font)
        self.play_button.config(font=play_font)

        # Управление доступностью чекбокса
        self.checkbutton_mine_mode.config(state='normal' if mode == Mode.edit else 'disabled')

        if mode == Mode.edit:
            self.images["there_is_bomb"] = self.images["there_is_bomb_"]
        else:
            self.images["there_is_bomb"] = self.images['closed']

        self.update_grid()

    def set_smile(self, state: GameState):
        match state:
            case GameState.playing:
                self.smile.config(image=self.images['face_smile'])
            case GameState.win:
                self.smile.config(image=self.images['face_win'])
            case GameState.fail:
                self.smile.config(image=self.images['face_fail'])
            case GameState.waiting:
                self.smile.config(image=self.images['face_smile'])

    def set_fail(self):
        self.set_smile(GameState.fail)
        self.update_grid()
        self.timer.stop()

    def set_win(self):
        self.set_smile(GameState.win)
        self.timer.stop()

    # def on_canvas_click_left(self, event):
    #     """Handle left click on canvas"""
    #     cell = self.get_cell_from_coords(event.x, event.y)
    #     if cell is not None:
    #         self.click_cell(event, cell, MouseButton.left)

    def on_canvas_click_right(self, event):
        """Handle right click on canvas"""
        cell = self.get_cell_from_coords(event.x, event.y)
        if cell is not None:
            self.click_cell(event, cell, MouseButton.right)

    def on_canvas_click_middle(self, event):
        """
        Тест подстветки ячеек.
        """
        print('Middle click')
        cell = self.get_cell_from_coords(event.x, event.y)
        item_id = self.canvas.find_closest(event.x, event.y)
        self.highlight_cell(cell.row, cell.col)

    def on_left_mouse_press(self, event):
        """Handle mouse press - show neighboring cells as pressed"""
        if self.edit_mode == Mode.play and self.matrix.game_state in [GameState.playing, GameState.waiting]:
            cell = self.get_cell_from_coords(event.x, event.y)

            # если зажата закрытая ячейка, мы просто визуально показываем ее "зажатой"
            if cell and cell.is_closed:
                cell_id = self.cells[(cell.row, cell.col)]['id']
                self.canvas.itemconfig(cell_id, image=self.images["0"])

            # если зажата цифра, мы "прожимаем" закрытые ячейки вокруг на время зажатия кнопки мыши
            if cell and cell.is_digit:
                neighbors = self.matrix.around_closed_cells(cell)
                for neighbor in neighbors:
                    if neighbor.is_closed and not neighbor.is_flag:
                        cell_id = self.cells[(neighbor.row, neighbor.col)]['id']
                        self.canvas.itemconfig(cell_id, image=self.images["0"])

    def on_left_mouse_release(self, event):
        """Handle mouse release - restore original cell images and run logic"""
        # выполнить логику по нажатию на ячейку
        cell = self.get_cell_from_coords(event.x, event.y)
        if cell is not None:
            self.click_cell(event, cell, MouseButton.left)

    def click_cell(self, event, cell: Cell, button: MouseButton):
        if self.matrix.game_state == GameState.waiting:
            self.matrix.game_state = GameState.playing
            if self.edit_mode == Mode.play:
                self.timer.start()

        if self.matrix.game_state == GameState.playing:
            if self.edit_mode == Mode.play:

                # run logic
                if button == MouseButton.left:
                    self.matrix.click_play_left_button(cell)
                elif button == MouseButton.right:
                    self.matrix.click_play_right_button(cell)
                else:
                    raise Exception('Unknown button')

                # after the logic had run, we checked a new game state
                if self.matrix.game_state == GameState.fail:
                    print('Gave over')
                    self.set_fail()
                if self.matrix.game_state == GameState.win:
                    self.set_win()

            elif self.edit_mode == Mode.edit:
                # В режиме Mines is known - ON мы просто переключаем содержимое ячейки, включая скрытую бомбу. При этом обновляем цифры вокруг.
                # В режиме Mines is known - OFF мы переключаем цифры в пустых ячейках
                if self.mine_mode == MineMode.PREDEFINED:
                    self.matrix.click_cell_when_mines_predefined(cell, button)
                else:
                    self.matrix.click_cell_when_mines_undefined(cell, button)

            if self._show_probability.get():
                try:
                    self.matrix.solve()
                except InconsistencyError:
                    self.consistency = FieldConsistency.INVALID

            self.update_total_mines()
            self.update_grid()
            self.update_mine_counter()
            self.update_status_bar()

        if self._show_probability.get():
            try:
                self.matrix.solve()
            except InconsistencyError:
                self.consistency = FieldConsistency.INVALID



    def save_matrix(self):
        self.matrix.save()

    def load_matrix(self, matrix_file=None):

        # TODO Тут много общего с create_fresh_board(), надо как-то оптимизировать

        save_storage_dir = Path(__file__).resolve().parent / 'saves'

        if not matrix_file:
            matrix_file = filedialog.askopenfilename(
                initialdir=os.path.dirname(__file__) + '/saves',
                filetypes=[("txt", "*.txt")]
            )

        file_path = save_storage_dir / matrix_file

        if matrix_file:
            self.matrix.load(file_path)
            w, h = self.matrix.width, self.matrix.height
            game = Game(w, h, bombs=0)

            self.timer.reset()
            self.set_custom_size(game)
            self.update_mine_counter()
            self.matrix.game_state = GameState.waiting
            self.set_smile(self.matrix.game_state)
            self.update_grid()

            # self.mine_mode = ...
            print('Matrix mine mode', self.matrix.mine_mode.name)
            print('Self mine mode', self.mine_mode.name)

            """
            ПОСЛЕ ЗАГРУЗКИ МАТРИЦЫ НУЖНО ПЕРЕКЛЮЧАТЬСЯ
            - ЕСЛИ UNDEFINED
              -> ИЗ ЛЮБОГО РЕЖИМА В -> EDIT UNDEFINED
            - ЕСЛИ PREDEFINED
              - PLAY -> ОСТАЕТСЯ PLAY
              - EDIT -> ПЕРЕКЛЮЧАЕТСЯ НА EDIT PREDEFINED
            """

        print("Field loaded successfully!")
        self.switch_edit_mode(mode=Mode.play)

    def on_closing(self):
        self.timer.stop()  # Stop the timer thread
        self.root.destroy()  # Close the application

    ##########################
    # Методы обеспечивающие внешнюю подсветку ячеек
    ##########################

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
        self.canvas.tag_raise(highlight, self.cells[(row, col)]['id'])

        # Уведомляем внешний обработчик
        if self.external_handlers['on_cell_highlight']:
            self.external_handlers['on_cell_highlight'](row, col, color)

        # Убираем подсветку через указанное время
        self.root.after(duration_ms, lambda: self.canvas.delete('highlight'))

    def get_window_info(self) -> dict:
        """
        Возвращает информацию об окне приложения.
        Используется в технологии подсветки ячеек, если она не взлетит, то можно убрать.
        """
        return {
            'width': self.grid_width,
            'height': self.grid_height,
            'window_rect': GetWindowRect(GetForegroundWindow()),
            'cell_size': self.cell_size
        }

    ##########################
    # END BLOCK
    ##########################

    def get_cell_from_coords(self, canvas_x, canvas_y) -> Cell | None:
        """Convert canvas coordinates to grid coordinates"""
        grid_x = int(canvas_y // self.cell_size)
        grid_y = int(canvas_x // self.cell_size)

        if 0 <= grid_x < self.grid_height and 0 <= grid_y < self.grid_width:
            cell = self.matrix.table[grid_x][grid_y]
            return cell
        return None


def main(load_matrix=None):
    root = tk.Tk()
    app = MinesweeperApp(root, load_matrix)
    root.mainloop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Minesweeper editor and game.")
    parser.add_argument('--matrix', type=str, help='Load the matrix from file')
    args = parser.parse_args()

    main(args.matrix)  # Запускаем приложение с параметром из командной строки
