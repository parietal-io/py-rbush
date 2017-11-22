def generate_data(n=1000, size=50):
    from random import random
    data = []
    for _ in range(n):
        xmin = int(random() * (100-size))
        ymin = int(random() * (100-size))
        xmax = int(xmin + size * random())
        ymax = int(ymin + size * random())
        item = {'xmin': xmin, 'ymin': ymin, 'xmax': xmax, 'ymax': ymax}
        data.append(item)
    return data


def generate_numpy_data(n=1000, size=50):
    from numpy.random import randn
    xmin = randn(n) * (100 - size)
    ymin = randn(n) * (100 - size)
    xmax = xmin + size
    ymax = ymin + size
    return {'xmin': xmin, 'ymin': ymin, 'xmax': xmax, 'ymax': ymax}
