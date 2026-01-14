
class BidirectionalStrIntMap(object):
    ''' Dictionary with bidirectional str<->int lookup.
    '''

    def __init__(self):
        self._dict = {}

    def __getitem__(self, key):
        if isinstance(key, int):
            if key not in self._dict.values():
                raise IndexError(key)
            return list(self._dict.keys())[list(self._dict.values()).index(key)]
        elif isinstance(key, str):
            if key not in self._dict:
                raise KeyError(key)
            return self._dict[key]
        else:
            raise TypeError(key)

    def __contains__(self, key):
        return key in self._dict or key in self._dict.values()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        s = f'{type(self).__name__}: {{ \n'
        for k, v in self._dict.items():
            s += f' {v: 4d} (0x{v:02x}): {k}\n'
        s += '}'
        return s

    def keys(self):
        return self._dict.keys()

    def values(self):
        return self._dict.values()

    def items(self):
        return self._dict.items()
