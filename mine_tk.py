"""

КОРОЧЕ, НУЖНО ПРИЙТИ К ТАКОМУ СОГЛАШЕНИЮ ВО ==ВСЕМ== ПРОЕКТЕ:

БОМБЫ - (BOMBS) - ЭТО АССЕТЫ (И СОДЕРЖИМОЕ) ЯЧЕЕК *ПОСЛЕ* ОКОНЧАНИЯ ИГРЫ, КОГДА ЮЗЕР ВЗОРВАЛСЯ

МИНЫ (MINES) - ЭТО БОМБЫ, КОТОРЫЕ МЫ ИСПОЛЬЗУЕМ В ИГРЕ TK.

Соотв,

cell.is_bomb - это если бомба после взрыва (в игре с экрана)
cell.is_mine - это спрятанная в ячейке бомба (в сете matrix.mines)

"""

# 💣🚩
# TODO В Play mode можно перейти, только если был включен bomb mode
# TODO После загрузки Pickle устанавливать ??? режим
# TODO При редактировании проверять поле на валидность
# TODO Сделать расширенный режим генерации поля с проверками на валидность 

import os
import pickle
import threading
import time
from pathlib import Path
from win32gui import GetWindowRect, GetForegroundWindow
from enum import IntEnum
from typing import Callable

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tktooltip import ToolTip

from asset import *
from classes import PlayMatrix
from classes import Cell
from classes import Game
from classes import GameState
from classes import beginner, beginner_new, intermediate, expert
from mouse_controller import MouseButton


class Mode(IntEnum):
    play = 0
    edit = 1


asset_dir = Path(__file__).resolve().parent / 'asset' / 'asset_svg'


class GameTimer:
    def __init__(self, update_callback: Callable[[int], None]):
        """
        Инициализация таймера

        Args:
            update_callback: функция, которая будет вызываться при каждом обновлении времени
                           принимает один аргумент - количество прошедших секунд
        """
        self.seconds = 0
        self.is_running = False
        self.update_callback = update_callback
        self.timer_thread = None
        self._lock = threading.Lock()

    def _timer_loop(self):
        """Основной цикл таймера, выполняющийся в отдельном потоке"""
        while True:
            with self._lock:
                if not self.is_running:
                    break
                self.seconds += 1
                # Вызываем callback для обновления отображения
                self.update_callback(self.seconds)
            time.sleep(1)

    def start(self):
        """Запуск таймера"""
        with self._lock:
            if not self.is_running:
                self.is_running = True
                self.timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
                self.timer_thread.start()

    def stop(self):
        """Остановка таймера"""
        # with self._lock:
        #     self.is_running = False
        # if self.timer_thread:
        #     self.timer_thread.join()
        with self._lock:
            self.is_running = False

    def reset(self):
        """Сброс таймера"""
        with self._lock:
            self.seconds = 0
            self.is_running = False
        if self.timer_thread:
            self.timer_thread.join()
        self.update_callback(0)

    def get_time(self) -> int:
        """Получить текущее время в секундах"""
        with self._lock:
            return self.seconds


class MinesweeperApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("300x300")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)  # Bind the close event

        self.current_game = beginner
        self.grid_width = self.current_game.width
        self.grid_height = self.current_game.height
        self.cell_size = 24  # размер ячейки в px
        self.root.title(f"Minesweeper {self.grid_width}x{self.grid_height}")

        self.use_timer = True
        self.timer = GameTimer(self.update_timer_display)

        self.matrix = PlayMatrix()  # we need matrix initialized matrix for create status bar
        self.matrix.initialize(height=self.grid_height, width=self.grid_width)
        self.matrix.create_new_game(n_bombs=self.current_game.bombs)

        self.mode = Mode.edit
        self.mines_is_known = True
        self.load_images()

        self.create_top_frame()
        self.create_status_bar()
        self.create_menu()
        
        # Add this line to properly place the grid_frame
        self.grid_frame = tk.Frame(self.root)
        self.grid_frame.grid(row=1, column=1, sticky='nw')  # Add grid configuration
        
        self.cells = {}
        self.create_canvas()
        self.fill_canvas()
        self.create_sidebar()
        self.create_fresh_board(game=beginner)

        # Bind canvas events
        self.canvas.bind("<Button-1>", self.on_canvas_click_left)
        self.canvas.bind("<Button-3>", self.on_canvas_click_right)

    def load_images(self):
        self.images = {
            "closed": tk.PhotoImage(file=asset.closed.filename),
            "bomb": tk.PhotoImage(file=asset.bomb.filename),
            "bomb_red": tk.PhotoImage(file=asset.bomb_red.filename),
            "bomb_wrong": tk.PhotoImage(file=asset.bomb_wrong.filename),
            "flag": tk.PhotoImage(file=asset.flag.filename),
            "there_is_bomb": tk.PhotoImage(file=asset.there_is_bomb.filename),
            "0": tk.PhotoImage(file=asset.n0.filename),
            "1": tk.PhotoImage(file=asset.n1.filename),
            "2": tk.PhotoImage(file=asset.n2.filename),
            "3": tk.PhotoImage(file=asset.n3.filename),
            "4": tk.PhotoImage(file=asset.n4.filename),
            "5": tk.PhotoImage(file=asset.n5.filename),
            "6": tk.PhotoImage(file=asset.n6.filename),
            "7": tk.PhotoImage(file=asset.n7.filename),
            "8": tk.PhotoImage(file=asset.n8.filename),
            "led0": tk.PhotoImage(file=asset.led0.filename),
            "led1": tk.PhotoImage(file=asset.led1.filename),
            "led2": tk.PhotoImage(file=asset.led2.filename),
            "led3": tk.PhotoImage(file=asset.led3.filename),
            "led4": tk.PhotoImage(file=asset.led4.filename),
            "led5": tk.PhotoImage(file=asset.led5.filename),
            "led6": tk.PhotoImage(file=asset.led6.filename),
            "led7": tk.PhotoImage(file=asset.led7.filename),
            "led8": tk.PhotoImage(file=asset.led8.filename),
            "led9": tk.PhotoImage(file=asset.led9.filename),
            "face_smile": tk.PhotoImage(file=asset.smile.filename),
            "face_win": tk.PhotoImage(file=asset.win.filename),
            "face_fail": tk.PhotoImage(file=asset.fail.filename),
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

        # Right frame for timer
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
        self.sidebar = tk.Frame(self.root, width=83, padx=3, bg='lightgrey')
        self.sidebar.grid(row=1, column=0, rowspan=self.grid_height, sticky='ns')
        self.sidebar.grid_propagate(False)  # Prevent the sidebar from resizing based on its children

        self.edit_button = tk.Button(master=self.sidebar, text="Edit mode", command=lambda: self.set_mode(Mode.edit))
        self.edit_button.grid(row=0, column=0, pady=5)
        ToolTip(self.edit_button, msg="Для Edit Mode нужно установить соотв. Bomb Mode")

        self.checkbutton_mik = tk.Checkbutton(master=self.sidebar, text="", command=self.update_mines_is_known_button)
        self.checkbutton_mik.grid(row=2, column=0, pady=5)
        ToolTip(self.checkbutton_mik, msg="Mines is known. ON - Мы устанавливаем бомбы, цифры ставятся автоматически."
                                          " OFF - Мы устанавливаем цифры, положение бомб в матрице неопределено")
        self.checkbutton_mik.select() if self.checkbutton_mik else self.checkbutton_mik.deselect()

        self.label_mik_mode = tk.Label(self.sidebar, text="(Set Bombs)")
        self.label_mik_mode.grid(row=3, column=0, pady=5)

        self.play_button = tk.Button(master=self.sidebar, text="Play mode", command=lambda: self.set_mode(Mode.play))
        self.play_button.grid(row=4, column=0, pady=5)
        ToolTip(self.play_button, msg="Выходим из режима редактирования, и можем 'играть' в текущее поле")

        if self.mode == Mode.edit:
            self.edit_button.config(font=("Helvetica", 10, "bold"))
            self.play_button.config(font=("Helvetica", 10, "normal"))
        elif self.mode == Mode.play:
            self.edit_button.config(font=("Helvetica", 10, "normal"))
            self.play_button.config(font=("Helvetica", 10, "bold"))

    def create_status_bar(self):
        self.status_bar_frame = tk.Frame(self.root)
        self.status_bar_frame.grid(row=2, column=1, sticky='ns')
        self.status_bar = tk.Label(self.status_bar_frame, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky='we')

    def create_canvas(self):
        self.canvas = tk.Canvas(
            self.grid_frame,
            width=self.grid_width * self.cell_size,
            height=self.grid_height * self.cell_size,
            highlightthickness=0,  # Remove border
            bg='lightgray'  # Add background color to see canvas bounds
        )
        self.canvas.grid(row=0, column=0, sticky='nw')

    def fill_canvas(self):
        """Create grid using canvas instead of buttons"""
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
        if self.matrix.get_state == GameState.win:
            self.status_bar.config(text="You win!")
        elif self.matrix.get_state == GameState.fail:
            self.status_bar.config(text="You lose!")
        else:
            closed_count = len(self.matrix.get_closed_cells())
            mine_count = len(self.matrix.get_mined_cells())
            opened_count = len(self.matrix.get_open_cells())
            flag_count = len(self.matrix.get_flag_cells())
            self.status_bar.config(text=f"Closed:{closed_count}, Mines:{mine_count}, Open:{opened_count}, Flags:{flag_count}")



    def on_canvas_click_left(self, event):
        """Handle left click on canvas"""
        x, y = self.get_cell_from_coords(event.x, event.y)
        if x is not None and y is not None:
            self.click_cell(event, x, y, MouseButton.left)

    def on_canvas_click_right(self, event):
        """Handle right click on canvas"""
        x, y = self.get_cell_from_coords(event.x, event.y)
        if x is not None and y is not None:
            self.click_cell(event, x, y, MouseButton.right)

    def get_cell_from_coords(self, canvas_x, canvas_y):
        """Convert canvas coordinates to grid coordinates"""
        grid_x = int(canvas_y // self.cell_size)
        grid_y = int(canvas_x // self.cell_size)

        if 0 <= grid_x < self.grid_height and 0 <= grid_y < self.grid_width:
            return grid_x, grid_y
        return None, None


    def update_grid(self):
        """
        Обновляет визуальное отображение в соответствии с объектом Matrix
        """
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                cell = self.matrix.table[row][col]
                image_name = cell.content.name
                cell_id = self.cells[(row, col)]['id']

                if image_name in self.images:
                    if (self.mode == Mode.edit and self.mines_is_known is True
                            and cell.is_closed and cell.is_mine):
                        img = self.images['there_is_bomb']
                    else:
                        img = self.images[image_name]

                    # Update cell image
                    self.canvas.itemconfig(cell_id, image=img)
                else:
                    raise Exception(f"Image not found: {image_name}")

        self.update_status_bar()

    def update_mines_is_known_button(self):
        if self.mines_is_known:
            response = messagebox.askyesno("Warning",
                                           "Это удалит все установленные мины с поля.")
            if response:
                self.mines_is_known = not self.mines_is_known
                self.checkbutton_mik.deselect()
                self.switch_to_mik_off()
        else:
            response = messagebox.askyesno("Warning",
                                           "Все цифры станут просто открытыми ячейками (0). Можно расставить бомбы")
            if response:
                self.mines_is_known = not self.mines_is_known
                self.checkbutton_mik.select()
                self.switch_to_mik_on()

    def switch_to_mik_on(self):
        """
        Переключение в режим "расстановка бомб"
        """
        # значит, у нас дана матрица с закрытыми ячейками и числами....
        # нам нужно все числа превратить в n0
        digits = self.matrix.get_digit_cells()
        for d in digits:
            d.content = asset.n0

        self.label_mik_mode.config(text="(Set Bombs)")

        self.update_grid()

    def switch_to_mik_off(self):
        """
        Переключение в режим "расстановка чисел"
        """
        # Нам нужно убрать все "установленные бомбы"
        self.matrix.mines = set()
        self.label_mik_mode.config(text="(Set Digits)")
        self.update_grid()

    def set_mode(self, mode):
        """
        Switch from Edit to Play mode and back.
        :param mode:
        :return:
        """
        self.mode = mode
        print(f"Mode set to: {self.mode.name}")

        # Update button fonts
        if self.mode == Mode.edit:
            self.edit_button.config(font=("Helvetica", 10, "bold"))
            self.play_button.config(font=("Helvetica", 10, "normal"))
            self.images["there_is_bomb"] = tk.PhotoImage(file=asset_dir.joinpath("there_is_bomb.png"))
        elif self.mode == Mode.play:
            self.edit_button.config(font=("Helvetica", 10, "normal"))
            self.play_button.config(font=("Helvetica", 10, "bold"))
            self.images["there_is_bomb"] = tk.PhotoImage(file=asset_dir.joinpath("closed.png"))
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
        if self.use_timer:
            self.timer.stop()

    def set_win(self):
        self.set_smile(GameState.win)
        if self.use_timer:
            self.timer.stop()

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
        self.matrix = PlayMatrix()
        self.matrix.initialize(self.grid_width, self.grid_height)
        self.matrix.create_new_game(n_bombs=game.bombs)
        print('State:', self.matrix.get_state.name)
        self.set_smile(self.matrix.get_state)

        self.update_grid()
        self.matrix.display()

    def set_custom_size(self, game: Game = None):
        """
        Size is string like "10x5"
        """
        width, height, bombs = game.width, game.height, game.bombs

        if 1 <= width <= 50 and 1 <= height <= 50:

            self.current_game = game
            self.grid_width = width
            self.grid_height = height

            # Update canvas size
            self.canvas.config(
                width=self.grid_width * self.cell_size,
                height=self.grid_height * self.cell_size
            )
            self.fill_canvas()

            self.root.update_idletasks()  # Ensure the grid is created before resizing
            geom_x = self.cell_size * width + self.sidebar.winfo_width()
            geom_y = self.cell_size * height + self.status_bar_frame.winfo_height() + self.top_frame.winfo_height()
            # geom_x = max(geom_x, 250)
            # geom_y = max(geom_y, 80)
            self.root.geometry(f"{geom_x}x{geom_y}")
            self.root.title(f"Minesweeper {self.grid_width}x{self.grid_height}")
            print(f'Successfully set grid size to {width}x{height} and window to {geom_x}x{geom_y}')
        else:
            messagebox.showerror("Invalid Size", "Width and height must be between 1 and 50.")

    def click_cell(self, event, x: int, y: int, button: MouseButton):
        if self.matrix.get_state == GameState.waiting:
            self.matrix.set_state(GameState.playing)
            if self.use_timer:
                self.timer.start()

        if self.matrix.get_state == GameState.playing:
            # print(f'Clicked: {button.name}')
            if self.mode == Mode.play:
                self.play_cell(x, y, button)
            elif self.mode == Mode.edit:
                # В режиме Mines is known - ON мы просто переключаем содержимое ячейки, включая скрытую бомбу. При этом обновляем цифры вокруг.
                # В режиме Mines is known - OFF мы переключаем цифры в пустых ячейках
                if self.mines_is_known:
                    self.edit_cell_bomb_mode(x, y, button)
                else:
                    self.edit_cell_digit_mode(x, y, button)

            self.update_grid()
            self.update_status_bar()

    def play_cell(self, x, y, button):
        current_cell = self.matrix.table[x][y]
        print(f'Click: {button}')

        if button == MouseButton.left:
            self.matrix.play_left_button(current_cell)
        elif button == MouseButton.right:
            self.matrix.play_right_button(current_cell)
        else:
            raise Exception('Unknown button')

        if self.matrix.get_state == GameState.fail:
            print('Gave over')
            self.set_fail()
        if self.matrix.get_state == GameState.win:
            self.set_win()

    #
    # В МАЙН.ТК ОСТАЛОСЬ ПРОВЕРИТЬ ТОЛЬКО ЭТИ ДВА МЕТОДА
    # ОСТАЛЬНОЕ В ЛОГИКЕ MATRIX play_left_button И play_right_button
    #

    def edit_cell_bomb_mode(self, x, y, button):
        """
        тут немного говно-код. Потому что нам нужно итерировать состояние ячейки по нескольким ассетам ПЛЮС
        закрытая ячейка с бомбой. Для этого введен псевдо-ассет there_is_bomb, который на самом деле является
        ЗАКРЫТОЙ ЯЧЕЙКОЙ плюс мина в matrix.mines.
        """
        cell: Cell = self.matrix.table[x][y]
        content = self.matrix.table[x][y].content
        is_mined = cell.is_mine

        match content, is_mined, button:
            case asset.closed, False, MouseButton.left:
                # закрытая - ставим мину (ассет при этом не меняется - остается closed)
                cell.set_mine()
            case asset.closed, True, MouseButton.left:
                # мина -> открываем
                cell.remove_mine()
                cell.asset = asset.n0
            case _, False, MouseButton.left:
                # открытая -> закрываем
                cell.asset = asset.closed
            case asset.flag, _, MouseButton.right:
                # удаляем флаг
                cell.remove_flag()
            case asset.closed, _, MouseButton.right:
                # устанавливаем флаг
                cell.set_flag()

        # обновляем цифры вокруг
        cells_to_update = self.matrix.around_opened_cells(cell)
        for c in cells_to_update:
            mines = len(self.matrix.around_mined_cells(c))
            c.content = asset.open_cells[mines]

        # и в самой ячейке (если она открылась)
        if cell.is_empty:
            mines = len(self.matrix.around_mined_cells(cell))
            cell.content = asset.open_cells[mines]

    def edit_cell_digit_mode(self, x, y, button):


        # =-----

        cell: Cell = self.matrix.table[x][y]
        content = self.matrix.table[x][y].content
        rotating_states = [asset.closed, asset.n0, asset.n1, asset.n2, asset.n3, asset.n4, asset.n5, asset.n6, asset.n7,
                           asset.n8]

        print(f'Is flag: {content==asset.flag}')
        match content, button:

            case asset.flag, MouseButton.right:
                # удаляем флаг
                cell.remove_flag()
                print('rem f')

            case content, MouseButton.right:
                # устанавливаем флаг
                cell.set_flag()
                print('set f')

            case content, MouseButton.left:
                if content in rotating_states:
                    next_asset = rotating_states[(rotating_states.index(content) + 1) % len(rotating_states)]
                    cell.content = next_asset
                    print('Assign:', cell.content)
                pass

            case _:
                print('None equals')


    def update_mine_counter(self):
        count = len(self.matrix.get_mined_cells()) - len(self.matrix.get_flag_cells())
        count_str = f"{count:03d}"
        for i, digit in enumerate(count_str):
            self.mine_counter[i].config(image=self.images[f"led{digit}"])

    # """
    # Four methods for clock's
    # """
    # def update_timer(self, elapsed_time):
    #     time_str = f"{elapsed_time:03d}"
    #     for i, digit in enumerate(time_str):
    #         self.timer[i].config(image=self.images[f"led{digit}"])
    #
    #
    # def start_timer(self):
    #     if self.timer_thread and self.timer_thread.is_alive():
    #         self.timer_running = False
    #         self.timer_thread.join()
    #
    #     self.start_time = time.time()
    #     self.timer_running = True
    #     self.timer_thread = threading.Thread(target=self.update_timer_thread)
    #     self.timer_thread.start()
    #
    # def update_timer_thread(self):
    #     while self.timer_running:
    #         elapsed_time = int(time.time() - self.start_time)
    #         self.root.after(1000, self.update_timer, elapsed_time)
    #         time.sleep(1)
    #
    # def stop_timer(self):
    #     self.timer_running = False
    #     if self.timer_thread:
    #         self.timer_thread.join()
    #
    # def reset_timer(self):
    #     count_str = f"{0:03d}"
    #     for i, digit in enumerate(count_str):
    #         self.mine_counter[i].config(image=self.images[f"led{digit}"])
    # """
    # END
    # """

    """
    новые методы для таймера
    """
    def update_timer_display(self, seconds: int):
        # Обновление отображения времени в интерфейсе
        time_str = f"{seconds:03d}"
        for i, digit in enumerate(time_str):
            self.led_timer[i].config(image=self.images[f"led{digit}"])
    """
    end
    """


    def save_matrix(self):

        # method 1
        # w, h = self.root.winfo_reqwidth(), self.root.winfo_reqheight()
        # x, y = self.root.winfo_rootx(), self.root.winfo_rootx()

        # method 2
        # coordinates = self.root.geometry()
        # size, x, y = coordinates.split('+')
        # x, y = int(x), int(y)
        # w, h = map(int, size.split('x'))
        # print(coordinates)
        # print(w, h)
        # print(x, y)

        # method 3
        (x1, y1, x2, y2) = GetWindowRect(GetForegroundWindow())

        # -----------
        # remove 9 px as shadow
        self.matrix.region_x1 = x1+9
        self.matrix.region_y1 = y1
        self.matrix.region_x2 = x2-9
        self.matrix.region_y2 = y2-9
        self.matrix.save(mode="tk")

    def load_matrix(self):
        file_path = filedialog.askopenfilename(
            initialdir=os.path.dirname(__file__),
            filetypes=[("Pickle files", "*.pickle")])
        if file_path:
            with open(file_path, 'rb') as inp:
                self.matrix = pickle.load(inp)
                self.matrix.display()

            w, h = self.matrix.width, self.matrix.height
            g = Game(w, h, bombs=0)
            self.set_custom_size(g)
            self.update_grid()
            print("Field loaded successfully!")

    def on_closing(self):
        self.timer.stop()  # Stop the timer thread
        self.root.destroy()  # Close the application


if __name__ == "__main__":
    root = tk.Tk()
    app = MinesweeperApp(root)
    root.mainloop()
