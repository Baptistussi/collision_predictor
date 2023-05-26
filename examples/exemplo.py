import numpy as np
import pandas as pd
from matplotlib import pyplot

def move():
    x = 0
    while True:
        yield x
        x += 1

def measure(x):
    return np.random.normal(x, 1)


m = move()
ts = [measure(next(m)) for _ in range(100)]
tsdf = pd.DataFrame(ts)
tsdf.plot()
pyplot.show()


A = np.array(
    [ [1, 2],
    [0, 1] ]
    )
