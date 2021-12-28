from unittest import TestCase
from src.plist import plist
from enum import Enum
import random

class Operations(Enum):
    REMOVE = 1
    APPEND_BACK = 2
    APPEND_FRONT = 3
    SET = 4
    INSERT = 5


class TestPList(TestCase):

    @staticmethod
    def get_operation():
        operations = [Operations.REMOVE,
                      Operations.SET,
                      Operations.APPEND_BACK,
                      Operations.APPEND_FRONT,
                      Operations.INSERT
                      ]

        op = operations[random.randint(0, len(operations) - 1)]

        return op

    def test_brute_force(self):

        for i in range(100):
            pl = plist()
            l = []

            for j in range(100):

                op = TestPList.get_operation()

                pl_len = len(pl)
                ind = 0
                if pl_len != 0:
                    ind = random.randint(0, pl_len - 1)

                value = random.randint(0, 1000)

                print(i, j, op, ind, value)
                print(pl)
                
                if op == Operations.REMOVE:
                    if pl_len == 0:
                        continue

                    pl = pl.remove(ind)
                    l.remove(ind)

                elif op == Operations.APPEND_BACK:
                    pl = pl.append_back(value)
                    l.append(value)
                elif op == Operations.APPEND_FRONT:
                    pl = pl.append_front(value)
                    l.insert(0, value)
                elif op == Operations.SET:

                    if pl_len == 0:
                        continue
                    pl = pl.set(ind, value)
                    l[ind] = value

                elif op == Operations.INSERT:
                    pass


                self.assertEqual(l, pl.tolist())

