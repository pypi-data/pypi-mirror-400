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

print("respect priority ratio: counts:", repr(count))

while True:
    try:
        val = pq.get()
    except k3priorityqueue.Empty:
        break
    count[val] = count.get(val, 0) + 1
    print(val)

print("consumed all: counts:", repr(count))
