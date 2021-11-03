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
