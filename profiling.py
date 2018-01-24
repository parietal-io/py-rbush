#!/usr/bin/env python

import cProfile
import pstats

import pyximport
pyximport.install()

from rbush.data import generate_data_array
import rbush

def runme():
    data = generate_data_array(100000)
    r = rbush.RBush()
    r.load(data)
    dt = generate_data_array(1000)
    for i in range(len(dt)):
        _ = r.search(*tuple(dt[i]))


cProfile.runctx('runme()', globals(), locals(), 'profile.prof')
#cProfile.run('runme()', globals(), locals(), 'profile.prof')

s = pstats.Stats('profile.prof')
s.strip_dirs().sort_stats('time').print_stats()

