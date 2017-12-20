import numpy as np


def generate_numpy_data(n=1000, size=50):
    from numpy.random import randn
    xmin = randn(n) * size
    ymin = randn(n) * size
    xmax = xmin + (size * randn(n))
    ymax = ymin + (size * randn(n))
    return {'xmin': xmin, 'ymin': ymin, 'xmax': xmax, 'ymax': ymax}


def generate_data_array(n=1000, size=50):
    # from numpy.random import randn
    # xmin = randn(n) * (100 - size)
    # ymin = randn(n) * (100 - size)
    # xmax = xmin + size
    # ymax = ymin + size
    # arrays = {'xmin': xmin, 'ymin': ymin, 'xmax': xmax, 'ymax': ymax}
    arrays = generate_numpy_data(n, size)
    data = np.array([arrays['xmin'],
                     arrays['ymin'],
                     arrays['xmax'],
                     arrays['ymax']]).T
    return data


def generate_data_record(n=1000, size=50):
    data = generate_data_array(n, size).T
    xmin = data[0]
    ymin = data[1]
    xmax = data[2]
    ymax = data[3]
    rec = np.rec.fromarrays([xmin, ymin, xmax, ymax],
                            names=['xmin', 'ymin', 'xmax', 'ymax'])
    return rec


def generate_data_items(n=1000, size=50):
    arrays = generate_numpy_data(n, size)
    data = []
    for i in range(n):
        data.append({'xmin': arrays['xmin'][i],
                     'ymin': arrays['ymin'][i],
                     'xmax': arrays['xmax'][i],
                     'ymax': arrays['ymax'][i]})
    return data
