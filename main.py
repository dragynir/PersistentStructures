
from src.pvector import pvector
from src.pmap import pmap

if __name__ == '__main__':
    m = pmap()
    pairs = zip(range(3), range(3))
    for i, (k, v) in enumerate(pairs):
        m = m.set(k, v)
    print(m)
    for i, (k, v) in enumerate(pairs):
        print(k, v)
        m1 = m.remove(k)
    print(m)
