 def main():
    root = tk.Tk()
    
    # Создаем конфигурацию
    config = GameConfig(
        width=9,
        height=9,
        cell_size=24
    )
    
    # Создаем компоненты
    ui = GameUI(root, config)
    state = GameState(config)
    
    # Создаем контроллер и связываем всё вместе
    controller = GameController(ui, state)
    
    # Запускаем приложение
    root.mainloop()

if __name__ == "__main__":
    main()