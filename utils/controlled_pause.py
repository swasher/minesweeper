import time
import msvcrt


def controlled_pause(t=5):
    """
    Пауза длительностью t секунд.
    Можно остановить обратный отсчет, нажав любую клавишу.
    :param t:
    :return:
    """
    pressed = False
    print(f'Wait {t:.1f} sec, or type for pause')
    for i in range(round(t*10), 0, -1):
        if msvcrt.kbhit():
            # key = msvcrt.getch()
            pressed = True
            break
        print(f'\b\b\b{i/10:.1f}', end='')
        time.sleep(0.1)
    print('\b\b\b', end='')

    if pressed:
        print('Wait for key press')
        k = False
        while not k:
            k = msvcrt.kbhit()
