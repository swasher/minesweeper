import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import json
import os


class MinesweeperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Minesweeper")
        self.root.geometry("250x250")
        self.grid_width = 10
        self.grid_height = 10
        self.mines = set()
        self.buttons = {}
        self.load_images()
        self.create_menu()
        self.create_grid()

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
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        size_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Size", menu=size_menu)
        size_menu.add_command(label="Beginner (9x9)", command=lambda: self.set_grid_size(9, 9))
        size_menu.add_command(label="Intermediate (16x16)", command=lambda: self.set_grid_size(16, 16))
        size_menu.add_command(label="Expert (30x16)", command=lambda: self.set_grid_size(30, 16))
        size_menu.add_command(label="Custom", command=self.set_custom_size)

    def create_grid(self):
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Button):
                widget.destroy()
        self.buttons = {}
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                btn = tk.Button(self.root, image=self.images["closed"], command=lambda x=x, y=y: self.toggle_mine(x, y), highlightthickness=0)
                btn.grid(row=x, column=y)
                self.buttons[(x, y)] = btn


    # 💣🚩
    def toggle_mine(self, x, y):
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

    def count_adjacent_mines(self, x, y):
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in self.mines:
                    count += 1
        print('adjacent mines:', count)
        return count

    def update_grid(self):
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

    def set_grid_size(self, width, height):
        self.grid_width = width
        self.grid_height = height
        self.create_grid()

    def set_custom_size(self):
        size = simpledialog.askstring("Custom Size", "Enter width and height (e.g., 10x10):")
        if size:
            try:
                width, height = map(int, size.split('x'))
                if 1 <= width <= 50 and 1 <= height <= 50:
                    self.set_grid_size(width, height)
                else:
                    messagebox.showerror("Invalid Size", "Width and height must be between 1 and 50.")
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter valid width and height separated by 'x'.")


if __name__ == "__main__":
    root = tk.Tk()
    app = MinesweeperApp(root)
    root.mainloop()