 class GameUI:
    """Отвечает только за визуальное отображение"""
    def __init__(self, root: tk.Tk, config: GameConfig):
        self.root = root
        self.config = config
        
        # Создаем компоненты UI
        self.top_panel = TopPanel(root)
        self.grid_panel = GridPanel(root)
        self.status_bar = StatusBar(root)
        
    def update_cell(self, row: int, col: int, content: CellContent):
        """Обновляет отображение конкретной ячейки"""
        self.grid_panel.update_cell(row, col, content)
        
    def update_mine_counter(self, count: int):
        """Обновляет счетчик мин"""
        self.top_panel.update_mine_counter(count)
        
    def bind_cell_click(self, callback: Callable):
        """Привязывает обработчик клика по ячейке"""
        self.grid_panel.bind_click(callback)