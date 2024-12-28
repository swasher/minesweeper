import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import json
import os
import pickle
from enum import IntEnum
from matrix import Matrix
from cell import Cell

beginner = '9x9'
intermediate = '16x16'
expert = '30x16'


class Mode(IntEnum):
    play = 0
    edit = 1


class MinesweeperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Minesweeper")
        self.root.geometry("300x300")
        self.grid_width = 10
        self.grid_height = 10
        self.mode = Mode.edit
        self.mines = set()
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
        self.px = 20  # каждая ячейка - 20х20 px в asset_tk


    def load_images(self):
        self.images = {
            "closed": tk.PhotoImage(file="asset_tk/closed.png"),
            "opened": tk.PhotoImage(file="asset_tk/0.png"),
            "mine": tk.PhotoImage(file="asset_tk/bomb.png"),
            "flag": tk.PhotoImage(file="asset_tk/flagged.png"),
            "1": tk.PhotoImage(file="asset_tk/1.png"),
            "2": tk.PhotoImage(file="asset_tk/2.png"),
            "3": tk.PhotoImage(file="asset_tk/3.png"),
            "4": tk.PhotoImage(file="asset_tk/4.png"),
            "5": tk.PhotoImage(file="asset_tk/5.png"),
            "6": tk.PhotoImage(file="asset_tk/6.png"),
            "7": tk.PhotoImage(file="asset_tk/7.png"),
            "8": tk.PhotoImage(file="asset_tk/8.png"),
        }

    def create_menu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)
        file_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save", command=self.save_field)
        file_menu.add_command(label="Load", command=self.load_field)
        file_menu.add_command(label="Load matrix", command=self.load_matrix)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        size_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Size", menu=size_menu)
        size_menu.add_command(label="Beginner (9x9)", command=lambda: self.set_custom_size(size=beginner))
        size_menu.add_command(label="Intermediate (16x16)", command=lambda: self.set_custom_size(size=intermediate))
        size_menu.add_command(label="Expert (30x16)", command=lambda: self.set_custom_size(size=expert))
        size_menu.add_command(label="Custom", command=self.set_custom_size)

    def create_sidebar(self):
        sidebar = tk.Frame(self.root, width=100, bg='lightgrey')
        sidebar.grid(row=0, column=0, rowspan=self.grid_height, sticky='ns')

        edit_button = tk.Button(sidebar, text="Edit", command=lambda: self.set_mode(Mode.edit))
        edit_button.grid(row=0, column=0, pady=10)

        play_button = tk.Button(sidebar, text="Play", command=lambda: self.set_mode(Mode.play))
        play_button.grid(row=1, column=0, pady=10)

    def update_status_bar(self):
        closed_count = sum(1 for btn in self.buttons.values() if btn.cget("image") == str(self.images["closed"]))
        mine_count = len(self.mines)
        opened_count = sum(1 for btn in self.buttons.values() if btn.cget("image") == str(self.images["opened"]))
        flag_count = sum(1 for btn in self.buttons.values() if btn.cget("image") == str(self.images["flag"]))
        self.status_bar.config(text=f"Status: Closed: {closed_count}, Mines: {mine_count}, Opened: {opened_count}, Flags: {flag_count}")


    def set_mode(self, mode):
        self.mode = mode
        print(f"Mode set to: {self.mode}")

    def create_grid(self):
        # Clear existing buttons
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        self.grid_frame = tk.Frame(self.root)
        # self.grid_frame.grid(row=0, column=1)
        self.grid_frame.grid(row=0, column=1, sticky='nw')

        for x in range(self.grid_width):
            for y in range(self.grid_height):
                btn = tk.Button(self.grid_frame, command=lambda x=x, y=y: self.toggle_mine(x, y),
                                image=self.images["closed"],
                                highlightthickness=0,
                                borderwidth=0,
                                )
                btn.grid(row=x, column=y)
                self.buttons[(x, y)] = btn

        self.update_status_bar()

    # 💣🚩
    def toggle_mine(self, x, y):
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

    def save_field(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'w') as file:
                json.dump(list(self.mines), file)
            messagebox.showinfo("Save Field", "Field saved successfully!")

    def load_field(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'r') as file:
                self.mines = set(tuple(mine) for mine in json.load(file))
            self.update_grid()
            messagebox.showinfo("Load Field", "Field loaded successfully!")

    def load_matrix(self):
        file_path = filedialog.askopenfilename(filetypes=[("Pickle files", "*.pickle")])
        if file_path:
            with open(file_path, 'rb') as inp:
                matrix = pickle.load(inp)
                matrix.display()

            self.update_grid(matrix)
            print("Field loaded successfully!")

    def count_adjacent_mines(self, x, y):
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in self.mines:
                    count += 1
        # print('adjacent mines:', count)
        return count

    def update_grid(self, matrix=None):
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                if (x, y) in self.mines:
                    # self.buttons[(x, y)].config(text="M")
                    self.buttons[(x, y)].config(image=self.images["mine"])
                else:
                    # self.buttons[(x, y)].config(text="")
                    # self.buttons[(x, y)].config(image=self.images["closed"])
                    adjacent_mines = self.count_adjacent_mines(x, y)
                    if adjacent_mines > 0:
                        self.buttons[(x, y)].config(image=self.images[str(adjacent_mines)])
                    else:
                        self.buttons[(x, y)].config(image=self.images["opened"])

        if matrix:
            pass

        self.update_status_bar()

    def set_grid_size(self, width, height):
        self.grid_width = width
        self.grid_height = height
        self.create_grid()

    def set_custom_size(self, size: str = None):
        if not size:
            size = simpledialog.askstring("Custom Size", "Enter width and height (e.g., 10x10):")
        try:
            width, height = map(int, size.split('x'))
            if 1 <= width <= 50 and 1 <= height <= 50:
                self.set_grid_size(width, height)
                self.root.update_idletasks()  # Ensure the grid is created before resizing
                geom_x = self.px * width + 100
                geom_y = self.px * height + 30
                self.root.geometry(f"{geom_x}x{geom_y}")
                print(f'Successfully set grid size to {width}x{height} and window to {geom_x}x{geom_y}')
            else:
                messagebox.showerror("Invalid Size", "Width and height must be between 1 and 50.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid width and height separated by 'x'.")


if __name__ == "__main__":
    root = tk.Tk()
    app = MinesweeperApp(root)
    root.mainloop()