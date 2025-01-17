"""
Testing gaussian function for randomize time beetween clicks

Look at action there:
https://replit.com/@swasher/Gaussian-distribution-for-Minesweeper-mouse-duration
"""
import os
import numpy as np
import matplotlib.pyplot as plt
os.environ['MPLCONFIGDIR'] = os.getcwd() + "/configs/"


mu = 0.5     # Значение в "центре" колокола
sigma = 0.1  # Значения " по бокам" колокола, то есть отклонение от центра
s = np.random.normal(mu, sigma, 1000)


count, bins, ignored = plt.hist(s, 30, density=True)
plt.plot(bins, 1/(sigma * np.sqrt(2 * np.pi)) *
               np.exp( - (bins - mu)**2 / (2 * sigma**2) ),
         linewidth=2, color='r')

plt.show()
print(type(s))

for i in s:
  print(f'{i:2f}')



def gauss_duration():
    """
    NOT USED
    Testing gaussian function for randomize time beetween clicks

    Look at action there:
    https://replit.com/@swasher/Gaussian-distribution-for-Minesweeper-mouse-duration

    В данный момент для скорости мыши используется mouse.human_mouse_speed
    """
    if config.mouse_duration > 0:
        mu = config.mouse_duration      # Значение в "центре" колокола
        sigma = config.mouse_gaussian   # Значения " по бокам" колокола, то есть отклонение от центра
        # deprecated
        # gauss = np.random.normal(mu, sigma, 1000)
        # gauss = gauss[gauss > config.minimum_delay]     # remove all negative and very small
        # return random.choice(gauss)
        gauss = abs(random.gauss(mu, sigma))
        return gauss
    else:
        return 0


if __name__ == '__main__':
    from timeit import Timer
    t = Timer(lambda: gauss_duration())
    print(t.timeit(number=1000))
