
from src.pvector import pvector

if __name__ == '__main__':
    v1 = pvector((3, 4, 5))
    v2 = v1.append(5)

    print(v1)
    print(v2.undo())

    # print(v2._versions)
