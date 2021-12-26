
from src.pvector import pvector
from src.pmap import pmap

if __name__ == '__main__':
    m = pmap(a=2, b=3)
    m1 = m.set('a', 4)
    print(m)
    print(m1)
