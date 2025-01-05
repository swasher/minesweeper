import tkinter as tk
from tkinter import Button
from tkinter import filedialog, messagebox, simpledialog
from dataclasses import dataclass
import json
import os
import pickle
from enum import IntEnum
from matrix import Matrix
from cell import Cell
from PIL import Image, ImageTk


class Mode(IntEnum):
    play = 0
    edit = 1


@dataclass
class Game:
    width: int
    height: int
    bombs: int


beginner = Game(9, 9, 10)
intermediate = Game(16, 16, 40)
expert = Game(30, 16, 99)



class MinesweeperApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("300x300")

        self.grid_width = 10
        self.grid_height = 10
        self.root.title(f"Minesweeper {self.grid_width}x{self.grid_height}")

        self.matrix = Matrix(width=self.grid_width, height=self.grid_height)
        self.matrix.create_game(bombs=10)

        self.mode = Mode.edit

        # deprecated
        # self.mines = set()

        self.buttons = {}
        self.load_images()
        self.create_menu()
        self.create_sidebar()
        self.grid_frame = tk.Frame(self.root)

        # Create status bar
        self.status_bar = tk.Label(self.root, text="Status: ", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky='we')
        self.update_status_bar()

        self.create_grid()
        self.px = 16  # каждая ячейка - 20х20 px в asset_tk



    def load_images(self):
        folder = 'asset/'
        asset = folder + 'asset_tk/'
        self.images = {
            "closed": tk.PhotoImage(file=asset + "closed.png"),
            "bomb": tk.PhotoImage(file=asset + "bomb.png"),
            "flag": tk.PhotoImage(file=asset + "flag.png"),
            "0": tk.PhotoImage(file=asset + "0.png"),
            "1": tk.PhotoImage(file=asset + "1.png"),
            "2": tk.PhotoImage(file=asset + "2.png"),
            "3": tk.PhotoImage(file=asset + "3.png"),
            "4": tk.PhotoImage(file=asset + "4.png"),
            "5": tk.PhotoImage(file=asset + "5.png"),
            "6": tk.PhotoImage(file=asset + "6.png"),
            "7": tk.PhotoImage(file=asset + "7.png"),
            "8": tk.PhotoImage(file=asset + "8.png"),
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
        sidebar = tk.Frame(self.root, width=100, bg='lightgrey')
        sidebar.grid(row=0, column=0, rowspan=self.grid_height, sticky='ns')

        edit_button = tk.Button(sidebar, text="Edit", command=lambda: self.set_mode(Mode.edit))
        edit_button.grid(row=0, column=0, pady=10)

        play_button = tk.Button(sidebar, text="Play", command=lambda: self.set_mode(Mode.play))
        play_button.grid(row=1, column=0, pady=10)

    def create_status_bar(self):
        statusbar = tk.Frame(self.root, width=100, bg='lightgrey')
        statusbar.pack(side=tk.BOTTOM, fill='x')

    def update_status_bar(self):
        closed_count = len(self.matrix.get_closed_cells())
        mine_count = 0
        opened_count = len(self.matrix.get_open_cells())
        flag_count = len(self.matrix.get_flag_cells())
        self.status_bar.config(text=f"Status: Closed: {closed_count}, Mines: {mine_count}, Opened: {opened_count}, Flags: {flag_count}")

    def set_mode(self, mode):
        self.mode = mode
        print(f"Mode set to: {self.mode.name}")

    def start_new_game(self, game: Game = None):
        if not game:
            size = simpledialog.askstring("Custom Size", "Enter width, height and bombs (e.g., 30x16x99):")
            try:
                width, height, bombs = map(int, size.split('x'))
                game = Game(width, height, bombs)
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter valid ints separated by 'x'.")

        self.set_custom_size(game)
        self.matrix = Matrix(self.grid_width, self.grid_height)
        self.matrix.create_game(bombs=game.bombs)
        self.update_grid()
        print(111)
        self.matrix.display()

    def set_custom_size(self, game: Game = None):
        """
        Size is string like "10x5"
        """
        width, height, bombs = game.width, game.height, game.bombs

        if 1 <= width <= 50 and 1 <= height <= 50:

            # self.set_grid_size(width, height)
            self.grid_width = width
            self.grid_height = height
            self.create_grid()

            self.root.update_idletasks()  # Ensure the grid is created before resizing
            geom_x = self.px * width + 120
            geom_y = self.px * height + 83
            geom_x = max(geom_x, 250)
            # geom_y = max(geom_y, 80)
            self.root.geometry(f"{geom_x}x{geom_y}")
            self.root.title(f"Minesweeper {self.grid_width}x{self.grid_height}")
            print(f'Successfully set grid size to {width}x{height} and window to {geom_x}x{geom_y}')
        else:
            messagebox.showerror("Invalid Size", "Width and height must be between 1 and 50.")


    def create_grid(self):
        # Clear existing buttons
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        # possible deprecated (потому что выполняется в init)
        # self.grid_frame = tk.Frame(self.root)

        # self.grid_frame.grid(row=0, column=1)
        self.grid_frame.grid(row=0, column=1, sticky='nw')

        for x in range(self.grid_height):
            for y in range(self.grid_width):
                btn = tk.Button(self.grid_frame, command=lambda x=x, y=y: self.click_cell(x, y),
                                image=self.images["closed"],
                                highlightthickness=0,
                                borderwidth=0,
                                )
                btn.grid(row=x, column=y)
                self.buttons[(x, y)] = btn

        self.update_status_bar()

    def update_grid(self, matrix=None):
        """
        Обновляет визуальное отображение в соответствии с объектом Matrix
        """
        if matrix:
            for x in range(self.grid_width):
                for y in range(self.grid_height):

                    # TODO если ячейка УЖЕ соотв. матрице, не нужно ее обновлять, это только отнимает процессорное время

                    cell = matrix.table[x][y]
                    image_name = cell.asset.name
                    if image_name in self.images:
                        img = self.images[image_name]
                        self.buttons[(x, y)].config(image=img)
        self.update_status_bar()

    def click_cell(self, x, y):
        if self.mode == Mode.play:
            # мы не можем "переключать" ячейки, а только "открывать" их, а на закрытые ставит флаг.
            # Нужна логика открытия связанных ячеек.
            # Если нажали бомбу, то игра заканчивается.
            self.play_cell(x, y)
            # self.matrix.display()
        elif self.mode == Mode.edit:
            # мы просто переключаем содержимое ячейки, включая скрытую бомбу. При этом обновляем цифры вокруг.
            cell_toggle_list = ['closed', 'opened', 'flag', 'bomb']
            # Тут проблема в том, что в Asset нет ячейки "opened". Ее надо либо добавить в ассет, либо как-то
            # обрабатывать в коде. Ее нет, потому что все открытые ячейки отображаются цифрами.
            self.toggle_cell(x, y)

    def play_cell(self, x, y):
        pass

    # 💣🚩
    def toggle_cell(self, x, y):
        if self.mode == Mode.edit:
            current_image = self.buttons[(x, y)].cget("image")
            if current_image == str(self.images["closed"]):
                self.buttons[(x, y)].config(image=self.images["mine"])
                self.mines.add((x, y))
            elif current_image == str(self.images["mine"]):
                self.buttons[(x, y)].config(image=self.images["closed"])
                self.mines.remove((x, y))
        elif self.mode == Mode.play:
            current_image = self.buttons[(x, y)].cget("image")
            if current_image == str(self.images["closed"]):
                self.buttons[(x, y)].config(image=self.images["opened"])
            elif current_image == str(self.images["opened"]):
                self.buttons[(x, y)].config(image=self.images["mine"])
            elif current_image == str(self.images["mine"]):
                self.buttons[(x, y)].config(image=self.images["flag"])
            else:
                self.buttons[(x, y)].config(image=self.images["closed"])

            # Update only the toggled cell
            if (x, y) not in self.mines:
                adjacent_mines = self.count_adjacent_mines(x, y)
                if adjacent_mines > 0:
                    self.buttons[(x, y)].config(image=self.images[str(adjacent_mines)])
                else:
                    self.buttons[(x, y)].config(image=self.images["opened"])

        self.update_status_bar()

    def save_matrix(self):
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
            self.update_grid(self.matrix)
            print("Field loaded successfully!")

    # deprecated
    # def count_adjacent_mines(self, x, y):
    #     count = 0
    #     for dx in [-1, 0, 1]:
    #         for dy in [-1, 0, 1]:
    #             if dx == 0 and dy == 0:
    #                 continue
    #             if (x + dx, y + dy) in self.mines:
    #                 count += 1
    #     # print('adjacent mines:', count)
    #     return count



    # deprecated
    # def set_grid_size(self, width, height):
    #     self.grid_width = width
    #     self.grid_height = height
    #     self.create_grid()




if __name__ == "__main__":
    root = tk.Tk()
    app = MinesweeperApp(root)
    root.mainloop()