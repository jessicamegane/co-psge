import numpy as np
import copy


def tournament(population, tsize=3):
    pool = np.random.choice(population, tsize)
    pool = sorted(pool, key=lambda i: i['fitness'])
    return copy.deepcopy(pool[0])
