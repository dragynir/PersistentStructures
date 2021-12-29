from itertools import chain
from .pvector import pvector


class PMap(object):

    __slots__ = ('_size', '_buckets', '__weakref__', '_cached_hash')

    def __new__(cls, size, buckets):
        self = super(PMap, cls).__new__(cls)
        self._size = size
        # pvector с (key, value) парами
        self._buckets = buckets
        return self

    @staticmethod
    def _get_bucket(buckets, key):
        """
            Get bucket by key
        """
        index = hash(key) % len(buckets)
        bucket = buckets[index]
        return index, bucket

    @staticmethod
    def _getitem(buckets, key):
        """
            Get item by key
        """
        _, bucket = PMap._get_bucket(buckets, key)
        if bucket:
            for k, v in bucket:
                if k == key:
                    return v
        raise KeyError(key)

    @staticmethod
    def _contains(buckets, key):
        """
            Check for item with key
        """
        _, bucket = PMap._get_bucket(buckets, key)
        if bucket:
            for k, _ in bucket:
                if k == key:
                    return True
            return False
        return False

    def __getitem__(self, key):
        return PMap._getitem(self._buckets, key)

    def __contains__(self, key):
        return self._contains(self._buckets, key)

    def __iter__(self):
        return self.iterkeys()

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as e:
            raise AttributeError(
                "{0} has no attribute '{1}'".format(type(self).__name__, key)
            ) from e

    def _undo(self):
        self._buckets = self._buckets.undo()
        self._size = len(list(self.iterkeys()))

    def undo(self):
        self._undo()
        return self

    def _redo(self):
        self._buckets = self._buckets.redo()
        self._size = len(list(self.iterkeys()))

    def redo(self):
        self._redo()
        return self

    def iterkeys(self):
        """
            Iter pmap keys
        """
        for k, _ in self.iteritems():
            yield k

    def itervalues(self):
        """
            Iter pmap values
        """
        for _, v in self.iteritems():
            yield v

    def iteritems(self):
        """
            Iter pmap items: (key, value)
        """
        for bucket in self._buckets:
            if bucket:
                for k, v in bucket:
                    yield k, v

    def values(self):
        return pvector(self.itervalues())

    def keys(self):
        return pvector(self.iterkeys())

    def items(self):
        return pvector(self.iteritems())

    def __len__(self):
        return self._size

    def __repr__(self):
        return 'pmap({0})'.format(str(dict(self)))

    def __str__(self):
        return self.__repr__()

    def __hash__(self):
        if not hasattr(self, '_cached_hash'):
            self._cached_hash = hash(frozenset(self.iteritems()))
        return self._cached_hash

    def set(self, key, val):
        """
            Set value by key
        """
        return self.evolver().set(key, val).persistent()

    def remove(self, key):
        """
            Remove element by key
        """
        return self.evolver().remove(key).persistent()

    def update(self, *maps):
        """
            Update map values by keys
        """
        return self.update_with(lambda l, r: r, *maps)

    def update_with(self, update_fn, *maps):
        evolver = self.evolver()
        for map in maps:
            for key, value in map.items():
                evolver.set(key, update_fn(evolver[key], value) if key in evolver else value)

        return evolver.persistent()

    class _Evolver(object):
        __slots__ = ('_buckets_evolver', '_size', '_original_pmap')

        def __init__(self, original_pmap):
            self._original_pmap = original_pmap
            self._buckets_evolver = original_pmap._buckets.evolver()
            self._size = original_pmap._size

        def __getitem__(self, key):
            return PMap._getitem(self._buckets_evolver, key)

        def __setitem__(self, key, val):
            self.set(key, val)

        def set(self, key, val):
            # buckets overflow
            if len(self._buckets_evolver) < 0.67 * self._size:
                self._reallocate(2 * len(self._buckets_evolver))

            kv = (key, val)
            # находим бакет элемента
            index, bucket = PMap._get_bucket(self._buckets_evolver, key)
            if bucket:
                for k, v in bucket:
                    if k == key:
                        # находим элемент в бакете
                        if v is not val:
                            # создаем новый бакет (копируем и выставляем новое значение по ключу)
                            # заменяем бакет в pvector evolver
                            new_bucket = [(k2, v2) if k2 != k else (k2, val) for k2, v2 in bucket]
                            self._buckets_evolver[index] = new_bucket

                        return self
                # ключа нет в бакете - создаем новый бакет с доп парой (key, value)
                new_bucket = [kv]
                new_bucket.extend(bucket)
                self._buckets_evolver[index] = new_bucket
                self._size += 1
            else:
                # бакет не найден, создаем новый
                self._buckets_evolver[index] = [kv]
                self._size += 1

            return self

        def _reallocate(self, new_size):
            # увеличиваем кол-во бакетов в два раза
            new_list = new_size * [None]
            buckets = self._buckets_evolver.persistent()
            for k, v in chain.from_iterable(x for x in buckets if x):
                index = hash(k) % new_size
                if new_list[index]:
                    new_list[index].append((k, v))
                else:
                    new_list[index] = [(k, v)]
            # создаем новый pvector для бакетов
            self._buckets_evolver = pvector().evolver()
            self._buckets_evolver.extend(new_list)

        def is_dirty(self):
            """
                Check evolver for modifications
            """
            return self._buckets_evolver.is_dirty()

        def persistent(self):
            """
                Create persistent pmap form evolver view
            """
            if self.is_dirty():
                self._original_pmap = PMap(self._size, self._buckets_evolver.persistent())

            return self._original_pmap

        def __len__(self):
            return self._size

        def __contains__(self, key):
            return PMap._contains(self._buckets_evolver, key)

        def remove(self, key):
            # находим бакет с элементом
            index, bucket = PMap._get_bucket(self._buckets_evolver, key)

            if bucket:
                # создаем новый бакет без значения с ключом key
                new_bucket = [(k, v) for (k, v) in bucket if k != key]
                if len(bucket) > len(new_bucket):
                    # ключ был в бакете
                    self._buckets_evolver[index] = new_bucket if new_bucket else None
                    self._size -= 1
                    return self

            raise KeyError('{0}'.format(key))

    def evolver(self):
        return self._Evolver(self)


def mapping(initial):
    size = 8

    # создаем бакеты для хранения массивов пар (key, value)
    buckets = size * [None]

    # для каждого ключа вычисляем номер бакета и добавляем по индексу
    for k, v in initial.items():
        h = hash(k)
        index = h % size
        bucket = buckets[index]

        if bucket:
            bucket.append((k, v))
        else:
            buckets[index] = [(k, v)]

    # создаем pvector, который хранит бакеты
    return PMap(len(initial), pvector().extend(buckets))

_EMPTY_PMAP = mapping({})


def pmap(**kwargs):
    return mapping(kwargs)
