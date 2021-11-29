# potc

[![PyPI](https://img.shields.io/pypi/v/potc)](https://pypi.org/project/potc/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/potc)](https://pypi.org/project/potc/)
![Loc](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/HansBug/eaabf18edb37af48c7e67a9a9ec9aa8e/raw/loc.json)
![Comments](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/HansBug/eaabf18edb37af48c7e67a9a9ec9aa8e/raw/comments.json)

[![Docs Deploy](https://github.com/potc-dev/potc/workflows/Docs%20Deploy/badge.svg)](https://github.com/potc-dev/potc/actions?query=workflow%3A%22Docs+Deploy%22)
[![Code Test](https://github.com/potc-dev/potc/workflows/Code%20Test/badge.svg)](https://github.com/potc-dev/potc/actions?query=workflow%3A%22Code+Test%22)
[![Badge Creation](https://github.com/potc-dev/potc/workflows/Badge%20Creation/badge.svg)](https://github.com/potc-dev/potc/actions?query=workflow%3A%22Badge+Creation%22)
[![Package Release](https://github.com/potc-dev/potc/workflows/Package%20Release/badge.svg)](https://github.com/potc-dev/potc/actions?query=workflow%3A%22Package+Release%22)
[![codecov](https://codecov.io/gh/potc-dev/potc/branch/main/graph/badge.svg?token=XJVDP4EFAT)](https://codecov.io/gh/potc-dev/potc)

[![GitHub stars](https://img.shields.io/github/stars/potc-dev/potc)](https://github.com/potc-dev/potc/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/potc-dev/potc)](https://github.com/potc-dev/potc/network)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/potc-dev/potc)
[![GitHub issues](https://img.shields.io/github/issues/potc-dev/potc)](https://github.com/potc-dev/potc/issues)
[![GitHub pulls](https://img.shields.io/github/issues-pr/potc-dev/potc)](https://github.com/potc-dev/potc/pulls)
[![Contributors](https://img.shields.io/github/contributors/potc-dev/potc)](https://github.com/potc-dev/potc/graphs/contributors)
[![GitHub license](https://img.shields.io/github/license/potc-dev/potc)](https://github.com/potc-dev/potc/blob/master/LICENSE)

Python object to code framework, expression any python object to runnable python code.

Almost all the primitive types in python can be translated to source code format, and they will be runnable.


## Installation

You can simply install it with `pip` command line from the official PyPI site.

```shell
pip install potc
```

For more information about installation, you can refer to [Installation](https://potc-dev.github.io/potc/main/tutorials/installation/index.html).


## Documentation

The detailed documentation are hosted on [https://potc-dev.github.io/potc/main/index.html](https://potc-dev.github.io/potc/main/index.html).

Only english version is provided now, the chinese documentation is still under development.


## Quick Start

The native `potc` can transform many types, such as

```python
from potc import transobj
from easydict import EasyDict
import numpy as np

transobj(1)         # "1", int format
transobj('233')     # "'233'", str format
transobj(1.2)       # "1.2", float format
transobj([1, '2'])  # "[1, '2']", list format
transobj((1, '2'))  # "(1, '2')", tuple format
transobj({1, '2'})  # "{1, '2'}", set format  
transobj({1: '2'})  # "{1: '2'}", dict format
transobj(EasyDict(a=1, b=2))  # "EasyDict({'a': 1, 'b': 2})", external dict format
transobj(EasyDict)  # "EasyDict", type format
transobj(np)        # "numpy", module format
```

And so on, most of the native python types are covered.

In some cases, we need to translate the values into python script instead of simple expression, we can use `transvars`

```python
import math

from potc import transvars

if __name__ == '__main__':
    _code = transvars({
        'arr': [
            1, 1.5, math.e,
        ],
        'vbytes_': b'klsdjflkds\\\x00',
        'empty_str': '',
        'ba': bytearray(b'a' * 20),
    }, reformat='pep8')  # auto reformat the code
    print(_code)

```

The output should be

```python
import math

__all__ = ['arr', 'ba', 'empty_str', 'vbytes_']
arr = [1, 1.5, math.e]
ba = bytearray(b'aaaaaaaaaaaaaaaaaaaa')
empty_str = ''
vbytes_ = b'klsdjflkds\\\x00'

```

This script are runnable, can be imported directly into your python code. The import packages will also be generated (like `import math`).

In some complex cases, You can define you own rules to support more data types, such as

```python
import math

from potc import transvars
from potc.fixture import rule, Addons


class MyPair:
    def __init__(self, first, second):
        self.first = first
        self.second = second


@rule(type_=MyPair)
def mypair_support(v: MyPair, addon: Addons):
    return addon.obj(MyPair)(v.first, v.second)


if __name__ == '__main__':
    _code = transvars({
        'arr': [
            1, 1.5, math.e,
        ],
        'vbytes_': b'klsdjflkds\\\x00',
        'empty_str': '',
        'ba': bytearray(b'a' * 20),
        'c': MyPair(1, 2),
    }, trans=[mypair_support], reformat='pep8')  # auto reformat the code
    print(_code)

```

The output should be like below, the `MyPair` class is supported by the new rule.

```python
import math

from __main__ import MyPair

__all__ = ['arr', 'ba', 'c', 'empty_str', 'vbytes_']
arr = [1, 1.5, math.e]
ba = bytearray(b'aaaaaaaaaaaaaaaaaaaa')
c = MyPair(1, 2)
empty_str = ''
vbytes_ = b'klsdjflkds\\\x00'
```

For more quick start explanation and further usage, take a look at:

* [Quick Start](https://potc-dev.github.io/potc/main/tutorials/quick_start/index.html)


# Contributing

We appreciate all contributions to improve `potc`, both logic and system designs. Please refer to CONTRIBUTING.md for more guides.


# License

`potc` released under the Apache 2.0 license.

