import time
from random import randint

from rbush import Rbush

sample_size = [100,500,1000,5000,10000]#,50000]

left_limit = 0
right_limit = 100000
bottom_limit = 0
top_limit = 100000

def generate_data(n):
    range_minX = int(right_limit*0.5)
    range_minY = int(top_limit*0.5)
    data = []
    for _ in range(n):
        minX = randint(left_limit,range_minX)
        maxX = randint(range_minX,right_limit)
        minY = randint(bottom_limit,range_minY)
        maxY = randint(range_minY,top_limit)
        item = {'minX': minX, 'minY': minY, 'maxX': maxX, 'maxY': maxY}
        data.append(item)
    return data

def run_items_insertion():
    import json

    print("Sample_size  insert  remove    bulk  search")
    for n in sample_size:
        data = generate_data(n)

        tree = Rbush()

        # insertion
        tic = time.time()

        for item in data:
            tree.insert(item)

        tac = time.time()
        insertion = tac-tic

        # fileout = 'tree_items_insertion_full_{:d}.json'.format(n)
        # with open(fileout,'w') as fp:
        #     json.dump(tree.toJSON(),fp)

        # removal
        tic = time.time()

        for item in data:
            tree.remove(item)

        tac = time.time()
        removal = tac-tic

        # fileout = 'tree_items_insertion_empty_{:d}.json'.format(n)
        # with open(fileout,'w') as fp:
        #     json.dump(tree.toJSON(),fp)


        # Bulk load
        tic = time.time()

        tree.load(data)

        tac = time.time()
        bulk = tac-tic

        # Search item
        i = randint(0,len(data))
        item = data[i]
        tic = time.time()

        _item = tree.search(item)

        tac = time.time()
        search = tac-tic

        print('{:11d} {:06.5f} {:06.5f} {:06.5f} {:06.5f}'.format(
                n,insertion,removal,bulk,search))
#
# class Timer:
#   def __init__(self):
#     self.start = time.time()
#
#   def restart(self):
#     self.start = time.time()
#
#   def get_time_hhmmss(self):
#     end = time.time()
#     m, s = divmod(end - self.start, 60)
#     h, m = divmod(m, 60)
#     time_str = "%02d:%02d:%02d" % (h, m, s)
#     return time_str
