
from src.pvector import pvector
from src.pmap import pmap
from src.plist import plist

if __name__ == '__main__':
    l = plist()

    l1 = l.append_back(1)
    l2 = l1.append_back(2)
    l3 = l2.set(1, 3)
    l4 = l3.append_back(4)

    print(2)
    # l2.append_back(2)
