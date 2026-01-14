"""
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
"""

from importlib.metadata import version

__version__ = version("k3priorityqueue")

from .priorityqueue import (
    Empty,
    Producer,
    PriorityQueue,
    default_priority,
)

__all__ = [
    "Empty",
    "Producer",
    "PriorityQueue",
    "default_priority",
]
