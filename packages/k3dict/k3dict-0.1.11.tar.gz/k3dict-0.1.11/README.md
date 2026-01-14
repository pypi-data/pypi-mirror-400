# k3dict

[![Action-CI](https://github.com/pykit3/k3dict/actions/workflows/python-package.yml/badge.svg)](https://github.com/pykit3/k3dict/actions/workflows/python-package.yml)
[![Documentation Status](https://readthedocs.org/projects/k3dict/badge/?version=stable)](https://k3dict.readthedocs.io/en/stable/?badge=stable)
[![Package](https://img.shields.io/pypi/pyversions/k3dict)](https://pypi.org/project/k3dict)

It provides with several dict operation functions.

k3dict is a component of [pykit3] project: a python3 toolkit set.


k3dict

It provides with several dict operation functions.

#   Status

This library is considered production ready.




# Install

```
pip install k3dict
```

# Synopsis

```python

import k3dict

mydict = {'a':
              {'a.a': 'v-a.a',
               'a.b': {'a.b.a': 'v-a.b.a'},
               'a.c': {'a.c.a': {'a.c.a.a': 'v-a.c.a.a'}}
               }
          }

# depth-first iterative the dict
for rst in k3dict.depth_iter(mydict):
    print(rst)

# output:
#     (['a', 'a.c', 'a.c.a', 'a.c.a.a'], 'v-a.c.a.a')
#     (['a', 'a.b', 'a.b.a'], 'v-a.b.a')
#     (['a', 'a.a'], 'v-a.a')

for rst in k3dict.breadth_iter(mydict):
    print(rst)

# output:
#     (['a'],                            {'a.c': {'a.c.a': {'a.c.a.a': 'v-a.c.a.a'}}, 'a.b': {'a.b.a': 'v-a.b.a'}
#                                           , 'a.a': 'v-a.a'})
#     (['a', 'a.a'],                     'v-a.a')
#     (['a', 'a.b'],                     {'a.b.a': 'v-a.b.a'})
#     (['a', 'a.b', 'a.b.a'],            'v-a.b.a')
#     (['a', 'a.c'],                     {'a.c.a': {'a.c.a.a': 'v-a.c.a.a'}})
#     (['a', 'a.c', 'a.c.a'],            {'a.c.a.a': 'v-a.c.a.a'})
#     (['a', 'a.c', 'a.c.a', 'a.c.a.a'], 'v-a.c.a.a')
#

records = [
    {"event": 'log in',
     "time": {"hour": 10, "minute": 30, }, },

    {"event": 'post a blog',
     "time": {"hour": 10, "minute": 40, }, },

    {"time": {"hour": 11, "minute": 20, }, },

    {"event": 'log out',
     "time": {"hour": 11, "minute": 20, }, },
]

get_event = k3dict.make_getter('event', default="NOTHING DONE")
get_time = k3dict.make_getter('time.$field')

for record in records:

    ev = get_event(record)

    tm = "%d:%d" % (get_time(record, {"field": "hour"}),
                    get_time(record, {"field": "minute"}))

    print("{ev:<12}   at {tm}".format(ev=ev, tm=tm))

# output:
# log in         at 10:30
# post a blog    at 10:40
# NOTHING DONE   at 11:20
# log out        at 11:20

```

#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>


[pykit3]: https://github.com/pykit3