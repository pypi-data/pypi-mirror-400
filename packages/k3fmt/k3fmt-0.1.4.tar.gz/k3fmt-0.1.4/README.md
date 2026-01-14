# k3fmt

[![Action-CI](https://github.com/pykit3/k3fmt/actions/workflows/python-package.yml/badge.svg)](https://github.com/pykit3/k3fmt/actions/workflows/python-package.yml)
[![Documentation Status](https://readthedocs.org/projects/k3fmt/badge/?version=stable)](https://k3fmt.readthedocs.io/en/stable/?badge=stable)
[![Package](https://img.shields.io/pypi/pyversions/k3fmt)](https://pypi.org/project/k3fmt)

It provides with several string operation functions.

k3fmt is a component of [pykit3] project: a python3 toolkit set.


#   Name

k3fmt

It provides with several string operation functions.

#   Status

This library is considered production ready.




# Install

```
pip install k3fmt
```

# Synopsis

```python

import k3fmt

lines = [
    'hello',
    'world',
]

# add left padding to each line in a string
k3fmt.line_pad('\n'.join(lines), ' ' * 4)
# "    hello"
# "    world"


# format a multi-row line
items = ['name:',
         ['John',
          'j is my nick'
          ],

         'age:',
         26,

         'experience:',
         ['2000 THU',
          '2006 sina',
          '2010 other'
          ],
         ]

k3fmt.format_line(items, sep=' | ', aligns='llllll')
# outputs:
#    name: | John         | age: | 26 | experience: | 2000 THU
#          | j is my nick |      |    |             | 2006 sina
#          |              |      |    |             | 2010 other

```

#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>


[pykit3]: https://github.com/pykit3