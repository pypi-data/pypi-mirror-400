# k3priorityqueue

[![Action-CI](https://github.com/pykit3/k3priorityqueue/actions/workflows/python-package.yml/badge.svg)](https://github.com/pykit3/k3priorityqueue/actions/workflows/python-package.yml)
[![Documentation Status](https://readthedocs.org/projects/k3priorityqueue/badge/?version=stable)](https://k3priorityqueue.readthedocs.io/en/stable/?badge=stable)
[![Package](https://img.shields.io/pypi/pyversions/k3priorityqueue)](https://pypi.org/project/k3priorityqueue)

priorityQueue is a queue with priority support

k3priorityqueue is a component of [pykit3] project: a python3 toolkit set.


PriorityQueue is a queue with priority support:

The numbers of items it pops from each producer matches exactly the ratio of their priority:
If the priorities of 3 producer A, B and C are 1, 3 and 7, and it runs long
enough, it is expected that the number of items popped from A, B and C are
1:3:7.

import k3priorityqueue

producers = (
    # id, priority, iterable
    (1, 1, [1] * 10),
    (2, 2, [2] * 10),
    (3, 3, [3] * 10),
)
pq = k3priorityqueue.PriorityQueue()
for pid, prio, itr in producers:
    pq.add_producer(pid, prio, itr)

count = {}
for _ in range(12):
    val = pq.get()
    count[val] = count.get(val, 0) + 1
    print(val)

print('respect priority ratio: counts:', repr(count))

while True:
    try:
        val = pq.get()
    except k3priorityqueue.Empty as e:
        break
    count[val] = count.get(val, 0) + 1
    print(val)

print('consumed all: counts:', repr(count))




# Install

```
pip install k3priorityqueue
```

# Synopsis

```python

import k3priorityqueue

producers = (
    # id, priority, iterable
    (1, 1, [1] * 10),
    (2, 2, [2] * 10),
    (3, 3, [3] * 10),
)
pq = k3priorityqueue.PriorityQueue()
for pid, prio, itr in producers:
    pq.add_producer(pid, prio, itr)

count = {}
for _ in range(12):
    val = pq.get()
    count[val] = count.get(val, 0) + 1
    print(val)

print('respect priority ratio: counts:', repr(count))

while True:
    try:
        val = pq.get()
    except k3priorityqueue.Empty as e:
        break
    count[val] = count.get(val, 0) + 1
    print(val)

print('consumed all: counts:', repr(count))
```

#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>


[pykit3]: https://github.com/pykit3