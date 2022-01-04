# potc_dict

A simple demo of `potc` plugin.

## Installation

Just install this demo plugin by source code

```shell
git clone https://github.com/potc-dev/potc.git
cd potc/plugins/potc_dict
pip install .
```

## Effect show

We prepare a python script named `test_data.py`, like this

```python
import math

b = {
    'a': {'a': 3, 'b': None, 'c': math.e},
    'b': (3, 4, 'dfg'),
    'x0': {'a': 3, '02': 4, None: 2},
}

```

Before the installation mentioned above, we try to export the `b` in `test_data.py` by the following CLI command

```shell
potc export -v 'test_data.b'
```

We can get this dumped source code.

```python
import math

__all__ = ['b']
b = {
    'a': {
        'a': 3,
        'b': None,
        'c': math.e
    },
    'b': (3, 4, 'dfg'),
    'x0': {
        'a': 3,
        '02': 4,
        None: 2
    }
}
```

BUT, after the installation, **we try the CLI command which is exactly the same again, we get the new code**

```python
import math
from builtins import dict

__all__ = ['b']
b = dict(a=dict(a=3, b=None, c=math.e),
         b=(3, 4, 'dfg'),
         x0={
             'a': 3,
             '02': 4,
             None: 2
         })
```



That is all of this demo. **When you need to build your own plugin, maybe this demo can help you :smile:.**



