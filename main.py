
from src.pvector import pvector
from src.pmap import pmap

if __name__ == '__main__':
    m = pmap(a=2)
    m1 = m.set('a', 3)
    print(m)
    print(m1)
    m2 = m1.undo()
    print(m2)
    print(m2.redo())
