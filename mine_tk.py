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

import pickle
from pathlib import Path
from win32gui import GetWindowRect, GetForegroundWindow
from enum import IntEnum
from dataclasses import dataclass

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tktooltip import ToolTip

import asset
from matrix import Matrix
from cell import Cell


class Mode(IntEnum):
    play = 0
    edit = 1


class State(IntEnum):
    playing = 0
    win = 1
    fail = 2


class Mouse(IntEnum):
    left = 0
    right = 1
    both = 2


@dataclass
class Game:
    width: int
    height: int
    bombs: int


beginner = Game(9, 9, 10)
intermediate = Game(16, 16, 40)
expert = Game(30, 16, 99)
default_game = beginner

# config.assets =

# asset_dir = 'asset/asset_svg/'
asset_dir = Path(__file__).resolve().parent / 'asset' / 'asset_svg'


class MinesweeperApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("300x300")

        self.grid_width = default_game.width
        self.grid_height = default_game.height
        self.px = 24  # размер ячейки в px
        self.root.title(f"Minesweeper {self.grid_width}x{self.grid_height}")

        self.matrix = Matrix()  # we need matrix initialized matrix for create status bar
        self.matrix.initialize_without_screen(height=self.grid_height, width=self.grid_width)
        self.matrix.create_new_game(n_bombs=10)

        self.buttons = {}
        self.mode = Mode.edit
        self.state = State.playing
        self.mines_is_known = True
        self.load_images()

        self.create_status_bar()
        self.create_menu()
        self.grid_frame = tk.Frame(self.root)
        self.create_grid()
        self.create_sidebar()

        self.start_new_game(game=beginner)

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
        }

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
        size_menu.add_command(label="Beginner (9x9)", command=lambda: self.start_new_game(game=beginner))
        size_menu.add_command(label="Intermediate (16x16)", command=lambda: self.start_new_game(game=intermediate))
        size_menu.add_command(label="Expert (30x16)", command=lambda: self.start_new_game(game=expert))
        size_menu.add_command(label="Custom", command=self.start_new_game)

    def create_sidebar(self):
        self.sidebar = tk.Frame(self.root, width=83, padx=3, bg='lightgrey')
        self.sidebar.grid(row=0, column=0, rowspan=self.grid_height, sticky='ns')
        self.sidebar.grid_propagate(False)  # Prevent the sidebar from resizing based on its children

        self.edit_button = tk.Button(master=self.sidebar, text="Edit mode", command=lambda: self.set_mode(Mode.edit))
        self.edit_button.grid(row=0, column=0, pady=5)
        ToolTip(self.edit_button, msg="Для Edit Mode нужно установить соотв. Bomb Mode")

        # self.label_mik = tk.Label(self.sidebar, text="Bomb mode:")
        # self.label_mik.grid(row=1, column=0, pady=5)

        self.checkbutton_mik = tk.Checkbutton(master=self.sidebar, text="", command=self.update_mines_is_known)
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
        self.status_bar_frame.grid(row=1, column=1, sticky='ns')
        self.status_bar = tk.Label(self.status_bar_frame, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky='we')

    def create_grid(self):
        # Clear existing buttons
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        self.grid_frame.grid(row=0, column=1, sticky='nw')

        for x in range(self.grid_height):
            for y in range(self.grid_width):
                btn = tk.Button(self.grid_frame,
                                # command=lambda x=x, y=y: self.click_cell(x, y, 'aaa'),
                                image=self.images["closed"],
                                highlightthickness=0,
                                borderwidth=0,
                                )
                btn.bind("<Button-1>", lambda event, x=x, y=y: self.click_cell(event, x, y, Mouse.left))
                btn.bind("<Button-3>", lambda event, x=x, y=y: self.click_cell(event, x, y, Mouse.right))
                btn.grid(row=x, column=y)
                self.buttons[(x, y)] = btn

    def update_status_bar(self):
        if self.get_state == State.win:
            self.status_bar.config(text="You win!")
        elif self.get_state == State.fail:
            self.status_bar.config(text="You lose!")
        else:
            closed_count = len(self.matrix.get_closed_cells())
            mine_count = len(self.matrix.get_mined_cells())
            opened_count = len(self.matrix.get_open_cells())
            flag_count = len(self.matrix.get_flag_cells())
            self.status_bar.config(text=f"Closed:{closed_count}, Mines:{mine_count}, Open:{opened_count}, Flags:{flag_count}")

    def update_grid(self):
        """
        Обновляет визуальное отображение в соответствии с объектом Matrix
        """
        for x in range(self.grid_height):
            for y in range(self.grid_width):

                # TODO если ячейка УЖЕ соотв. матрице, не нужно ее обновлять, это только отнимает процессорное время

                cell = self.matrix.table[x][y]
                image_name = cell.asset.name
                button = self.buttons[(x, y)]

                if image_name in self.images:

                    if (self.mode == Mode.edit and self.mines_is_known is True
                            and cell.is_closed and cell.is_mine):
                        img = self.images['there_is_bomb']
                    else:
                        img = self.images[image_name]

                    button.config(image=img)
                else:
                    raise Exception(f"Image not found: {image_name}")

        self.update_status_bar()

    def update_mines_is_known(self):
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
            d.asset = asset.n0

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

    def start_new_game(self, game: Game = None):
        if not game:
            size = simpledialog.askstring("Custom Size", "Enter width, height and bombs (e.g., 30x16x99):")
            try:
                width, height, bombs = map(int, size.split('x'))
                game = Game(width, height, bombs)
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter valid ints separated by 'x'.")

        self.set_custom_size(game)
        self.matrix = Matrix()
        self.matrix.initialize_without_screen(self.grid_width, self.grid_height)
        self.matrix.create_new_game(n_bombs=game.bombs)

        self.set_state(State.playing)
        self.update_grid()
        # self.matrix.display()

    def set_custom_size(self, game: Game = None):
        """
        Size is string like "10x5"
        """
        width, height, bombs = game.width, game.height, game.bombs

        if 1 <= width <= 50 and 1 <= height <= 50:

            self.grid_width = width
            self.grid_height = height
            self.create_grid()

            self.root.update_idletasks()  # Ensure the grid is created before resizing
            geom_x = self.px * width + self.sidebar.winfo_width()
            geom_y = self.px * height + self.status_bar_frame.winfo_height()
            geom_x = max(geom_x, 250)
            # geom_y = max(geom_y, 80)
            self.root.geometry(f"{geom_x}x{geom_y}")
            self.root.title(f"Minesweeper {self.grid_width}x{self.grid_height}")
            print(f'Successfully set grid size to {width}x{height} and window to {geom_x}x{geom_y}')
        else:
            messagebox.showerror("Invalid Size", "Width and height must be between 1 and 50.")

    def click_cell(self, event, x: int, y: int, button: Mouse):
        if self.get_state == State.playing:
            # print(f'Clicked: {button.name}')
            if self.mode == Mode.play:
                # мы не можем "переключать" ячейки, а только "открывать" их, а на закрытые ставит флаг.
                # Нужна логика открытия связанных ячеек.
                # Если нажали бомбу, то игра заканчивается.
                self.play_cell(x, y, button)
                # self.matrix.display()
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

        if button == Mouse.left:
            fail = self.matrix.play_left_button(current_cell)
        elif button == Mouse.right:
            fail = self.matrix.play_right_button(current_cell)
        else:
            raise Exception('Unknown button')

        if fail:
            print('FAIL')
            self.set_state(State.fail)
        else:
            if len(self.matrix.get_closed_cells()) == 0:
                self.set_state(State.win)
                print('WIN')

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
        current_asset = self.matrix.table[x][y].asset
        is_mined = cell.is_mine
        print('Mined?', is_mined)
        print('Before match cell is:', cell, cell.asset)

        match current_asset, is_mined, button:
            case asset.closed, False, Mouse.left:
                print('left1')
                # закрытая - ставим мину (ассет при этом не меняется - остается closed)
                cell.set_mine()
            case asset.closed, True, Mouse.left:
                print('left2')
                # мина -> открываем
                cell.remove_mine()
                cell.asset = asset.n0
            case _, False, Mouse.left:
                print('left3')
                # открытая -> закрываем
                cell.asset = asset.closed
            case asset.flag, _, Mouse.right:
                print('right1')
                cell.remove_flag()
            case asset.closed, _, Mouse.right:
                print('right2')
                cell.set_flag()

        # обновляем цифры вокруг
        cells_to_update = self.matrix.around_opened_cells(cell)
        for c in cells_to_update:
            mines = len(self.matrix.around_mined_cells(c))
            c.asset = asset.open_cells[mines]

        # и в самой ячейке (если она открылась)
        if cell.is_empty:
            mines = len(self.matrix.around_mined_cells(cell))
            cell.asset = asset.open_cells[mines]

        print('After match cell is:', cell, cell.asset)

    def edit_cell_digit_mode(self, x, y, button):
        if button == Mouse.left:
            cell_toggle_list = [asset.closed, asset.n0, asset.n1, asset.n2, asset.n3, asset.n4, asset.n5, asset.n6, asset.n7, asset.n8]
        elif button == Mouse.right:
            cell_toggle_list = [asset.closed, asset.flag]
        else:
            raise Exception('Unknown button')

        current_asset = self.matrix.table[x][y].asset

        # Find the index of c in the list
        try:
            current_index = cell_toggle_list.index(current_asset)
        except ValueError:
            current_index = 0
        # Calculate the next index, wrapping around if necessary
        next_index = (current_index + 1) % len(cell_toggle_list)
        # Get the next item
        next_item = cell_toggle_list[next_index]

        self.matrix.table[x][y].asset = next_item

    def set_state(self, state: State):
        self.state = state

    @property
    def get_state(self):
        return self.state

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
        self.matrix.save()

    def load_matrix(self):
        file_path = filedialog.askopenfilename(filetypes=[("Pickle files", "*.pickle")])
        if file_path:
            with open(file_path, 'rb') as inp:
                self.matrix = pickle.load(inp)
                self.matrix.display()

            w, h = self.matrix.width, self.matrix.height
            g = Game(w, h, bombs=0)
            self.set_custom_size(g)
            self.update_grid()
            print("Field loaded successfully!")


if __name__ == "__main__":
    root = tk.Tk()
    app = MinesweeperApp(root)
    root.mainloop()
