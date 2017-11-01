
def generate_data(n,size=50):
    '''
    '''
    from random import random
    data = []
    for _ in range(n):
        xmin = int(random() * (100-size))
        ymin = int(random() * (100-size))
        xmax = xmin + size * random()
        ymax = ymin + size * random()
        item = {'xmin': xmin, 'ymin': ymin, 'xmax': xmax, 'ymax': ymax}
        data.append(item)
    return data
