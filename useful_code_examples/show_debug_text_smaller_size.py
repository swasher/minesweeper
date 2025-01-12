# попытка уменьщить размер текста, но не завелось

def show_debug_text(self):
    """
    Показывает текст на ячейках, который содержится в каждой ячейке в debug_text, в пределах ограниченной области.
    Убирает текст после нажатия любой клавиши, восстанавливая исходное состояние области.
    """
    # Координаты области
    x1, y1, x2, y2 = self.region_x1, self.region_y1, self.region_x2, self.region_y2
    width = x2 - x1
    height = y2 - y1

    # Получаем контекст устройства для области экрана
    hdesktop = win32gui.GetDesktopWindow()
    desktop_dc = win32gui.GetWindowDC(hdesktop)

    # Создаем контекст устройства для сохранения области
    mem_dc = win32ui.CreateDCFromHandle(desktop_dc)
    save_dc = mem_dc.CreateCompatibleDC()

    # Создаем битмап для сохранения области
    save_bitmap = win32ui.CreateBitmap()
    save_bitmap.CreateCompatibleBitmap(mem_dc, width, height)
    save_dc.SelectObject(save_bitmap)

    # Сохраняем область экрана в битмап
    save_dc.BitBlt((0, 0), (width, height), mem_dc, (x1, y1), win32con.SRCCOPY)

    font_params = {
        'height': 16,
        'width': 0,
        'escapement': 0,
        'orientation': 0,
        'weight': win32con.FW_NORMAL,
        'italic': False,
        'underline': False,
        # 'strikeout': False,
        'charset': win32con.ANSI_CHARSET,
        # 'out_precision': win32con.OUT_TT_PRECIS,
        # 'clip_precision': win32con.CLIP_DEFAULT_PRECIS,
        'quality': win32con.DEFAULT_QUALITY,
        # 'pitch_and_family': win32con.DEFAULT_PITCH | win32con.FF_DONTCARE,
        'name': "Arial"
    }

    try:
        # Создаем шрифт с меньшим размером
        font_height = 12  # Высота шрифта (в пикселях)
        hfont = win32ui.CreateFont(font_params)

        # Устанавливаем шрифт в контексте устройства
        old_font = save_dc.SelectObject(hfont)

        # Рисуем текст поверх экрана
        for row in self.table:
            for cell in row:
                if cell.debug_text is not None:
                    rect = (
                        cell.abscoordx,
                        cell.abscoordy,
                        cell.abscoordx + cell.w,
                        cell.abscoordy + cell.h
                    )

                    # Рисуем текст только если ячейка попадает в область
                    if (
                            rect[0] >= x1 and rect[1] >= y1 and
                            rect[2] <= x2 and rect[3] <= y2
                    ):
                        win32gui.DrawText(desktop_dc, cell.debug_text, -1, rect, win32con.DT_LEFT)
                        cell.debug_text = None

        # Ждем нажатия клавиши
        # keyboard.wait('space')
        keyboard.read_event()

        # Восстанавливаем старый шрифт после рисования
        save_dc.SelectObject(old_font)
        # Восстанавливаем область экрана из сохраненного битмапа
        mem_dc.BitBlt((x1, y1), (width, height), save_dc, (0, 0), win32con.SRCCOPY)

    finally:
        # Очистка ресурсов
        win32gui.DeleteObject(save_bitmap.GetHandle())
        save_dc.DeleteDC()
        mem_dc.DeleteDC()
        win32gui.ReleaseDC(hdesktop, desktop_dc)
