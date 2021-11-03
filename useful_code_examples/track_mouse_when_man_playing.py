# import mouse
# import threading
# import time
# import win32api
#
#
# def threadFunc():
#     while True:
#         # mouse.on_click(mouse_callback())
#         mouse.on_click(lambda: print("Left Button clicked."))
#
#
#
#
# # def printit():
# #   print ("Hello, World!")
# #   threading.Timer(1.0, printit).start()
# # threading.Timer(1.0, printit).start()
#
#
# def mouse_callback():
#     print(1)
#
# # mouse.on_click()
# #
# # mouse.get_position()
#
# if __name__ == '__main__':
#     # while True:
#     #     # mouse.on_click(mouse_callback())
#     #     mouse.on_click(lambda: print("Left Button clicked."))
#     # mouse.unhook_all()
#
#
#     # # Create a Thread with a function without any arguments
#     # th = threading.Thread(target=threadFunc)
#     # th.start()
#     # th.join()
#     # mouse.unhook_all()
#
#     import ctypes
#     import time
#
#
#     def DetectClick(button, watchtime=5):
#         '''Waits watchtime seconds. Returns True on click, False otherwise'''
#         if button in (1, '1', 'l', 'L', 'left', 'Left', 'LEFT'):
#             bnum = 0x01
#         elif button in (2, '2', 'r', 'R', 'right', 'Right', 'RIGHT'):
#             bnum = 0x02
#
#         start = time.time()
#         while 1:
#             if ctypes.windll.user32.GetKeyState(bnum) not in [0, 1]:
#                 # ^ this returns either 0 or 1 when button is not being held down
#                 return True
#             elif time.time() - start >= watchtime:
#                 break
#             time.sleep(0.001)
#         return False
#
#
#     while True:
#     DetectClick('left')


from pynput import mouse

def on_move(x, y):
    print('Pointer moved to {0}'.format((x, y)))
    # pass

def on_click(x, y, button, pressed):
    print('{0} at {1}'.format(
        'Pressed' if pressed else 'Released',
        (x, y)))
    if not pressed:
        # Stop listener
        return False

def on_scroll(x, y, dx, dy):
    print('Scrolled {0} at {1}'.format('down' if dy < 0 else 'up', (x, y)))

# # Collect events until released
# with mouse.Listener(
#         on_move=on_move,
#         on_click=on_click,
#         on_scroll=on_scroll) as listener:
#     listener.join()

# ...or, in a non-blocking fashion:
listener = mouse.Listener(
    on_move=on_move,
    on_click=on_click,
    on_scroll=on_scroll)
listener.start()
