import math

import numpy as np

from potc import transvars

if __name__ == '__main__':
    _code = transvars({
        'complex_array': [
            1, 1.5, math.e, object(),
            float('nan'), float('+inf'), float('-inf'),
            'str', None, {1, 2, 't' * 30},
            {
                1: 2, 'c': 3,
                'g': lambda x: x ** 2,
                't': dict(c=print, z=2),
            },
            {},
            frozenset({1, 2, }),
            max, min, NotImplemented,
            range(10), 7 + 8.0j,
        ],
        'vbytes_': b'klsdjflkds\\\x00',
        'empty_str': '',
        'ba': bytearray(b'a' * 20),
        'long_list': [123, {'1', b'klsdjf'}] * 10,
        'np_object': np.array([[1, 2, ], [3, 4]]),
        'np_module': np,
    }, reformat='pep8')  # auto reformat the code
    print(_code)
