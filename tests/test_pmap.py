from unittest import TestCase
from src import pmap

class TestPMap(TestCase):

    # test creation
    def test_empty(self):
        m = pmap()
        self.assertEqual(len(m), 0)

    def test_not_empty(self):
        m = pmap(a=2, b=4)
        self.assertEqual(len(m), 2)

    def test_not_empty(self):
        m = pmap(a=2, b=4)
        self.assertEqual(len(m), 2)

    def test_set_new(self):
        m = pmap()

        for i, (k, v) in enumerate(zip(range(10), range(10))):
            m = m.set(k, v)
            self.assertEqual(len(m), i + 1)

    def test_set_old(self):
        m = pmap()

        for i, (k, v) in enumerate(zip(range(10), range(10))):
            m = m.set(k, v)
            m = m.set(k, v - 1)
            self.assertEqual(m[k], v - 1)

    def test_buckts_overflow(self):
        m = pmap()
        for i, (k, v) in enumerate(zip(range(11), range(11))):
            m = m.set(k, v)
        self.assertEqual(len(m), 11)

    def test_remove(self):
        m = pmap()
        pairs = zip(range(11), range(11))
        for i, (k, v) in enumerate(pairs):
            m = m.set(k, v)
        pairs = zip(range(11), range(11))
        for i, (k, v) in enumerate(pairs):
            m = m.remove(k)

        self.assertEqual(len(m), 0)

    def test_update(self):
        m = pmap(a=2, b=3)
        m1 = m.update({'a': 1, 'b': 1})
        self.assertEqual(m1['a'], 1)
        self.assertEqual(m1['b'], 1)

    def test_items(self):
        m = pmap()
        pairs = zip(range(11), range(11))
        for i, (k, v) in enumerate(pairs):
            m = m.set(k, v)

        for (k, v) in m.items():
            self.assertEqual(v, k)
