import queue
import threading

import k3heap

default_priority = 10.0

Empty = queue.Empty


class Producer(object):
    """
    An internal class which tracks consumption state.
    It provides with a `get()` method to retrieve and item from it.
    It has an attribute `priority` to specify its priority.

    A `Producer` instance is able to compare to another with operator `<`:

    -   `a<b` is defined by: a is less consumed and would cost less for each
        consumption:
        The comparison key is: `(1/priority * nr_of_get, 1/priority)`.

    Thus a smaller `Producer` means it is less consumed and should be consumed first.
    Attributes:
        get():                      Returns an item.
        set_priority(float):        Set producer priority
        set_iterable(set_iterable): Set producer iterable
    """

    def __init__(self, producer_id, priority, iterable):
        self.consumed = 0
        self.iterable_lock = threading.RLock()
        self.stat = {"get": 0}
        self.cmp_key = (0, 0)

        self.producer_id = producer_id
        self.set_priority(priority)
        self.set_iterable(iterable)

    def get(self):
        with self.iterable_lock:
            try:
                val = next(self.iterable)
                self.stat["get"] += 1
                self.consume()
                return val
            except StopIteration:
                raise Empty("no more item in " + str(self))

    def set_priority(self, priority):
        priority = float(priority)

        if priority <= 0:
            raise ValueError("priority can not be less or euqal 0: " + str(priority))

        self.priority = priority
        self.item_cost = default_priority / float(self.priority)
        self.cmp_key = (self.consumed, self.item_cost)

    def set_iterable(self, iterable):
        self.iterable = iter(iterable)

    def consume(self):
        self.consumed += self.item_cost
        self.cmp_key = (self.consumed, self.item_cost)

    def __str__(self):
        return "[{producer_id}={priority} c={consumed}]".format(
            producer_id=self.producer_id,
            priority=self.priority,
            consumed=self.consumed,
        )

    def __lt__(self, b):
        return self.cmp_key < b.cmp_key


class PriorityQueue(object):
    """
    A queue managing several `Producer` instances.
    It produces items by `Producer.priority`.

    Internally, there are two heap to store producers.
    One of them for all consumable producers, the other is for all empty producers.

    When `PriorityQueue.get()` is called and it found that a producer becomes empty,
    it remove it from the consumable heap and put it into the empty producer heap
    and will never try to get an item from it again.

    To re-enable a producer, call `PriorityQueue.add_producer()` with the same
    `producer_id`.
    """

    def __init__(self):
        self.producer_by_id = {}

        # empty_heap: stores all empty Producer.
        #             Empty produer means it has raised an Empty exception when
        #             calling Producer.get().
        #             `Empty` exception raised means it has no more item to
        #             produce.
        #
        # consumable_heap: stores all non-empty Producer, less consumed
        #             Producer is at high position in heap.
        self.empty_heap = k3heap.RefHeap()
        self.consumable_heap = k3heap.RefHeap()

        self.heap_lock = threading.RLock()

    def add_producer(self, producer_id, priority, iterable):
        """
        Add a new producer or reset an existent producer.
            add_producer(int,float,iter)
        :arg
            producer_id: is provided as identity of a producer.

            priority: specifies the priority of this producer, priority also acts as the weight of
                      item to produce.
            iterable: is an producer implementation: it could be anything that can be used in a
                       `for-in` loop, such as `[1, 2, 3]`, or `range(10)`.
        """
        with self.heap_lock:
            if producer_id not in self.producer_by_id:
                p = Producer(producer_id, priority, iterable)
                self.producer_by_id[producer_id] = p
            else:
                # if exist, update its priority and iterable.
                p = self.producer_by_id[producer_id]
                p.set_priority(priority)
                p.set_iterable(iterable)

            # Every time add a (may be existent) queue, treat it as consumable
            self._remove_from_heaps(p)
            self.consumable_heap.push(p)

    def remove_producer(self, producer_id, ignore_not_found=False):
        """
        Remove a producer by its id.
        remove_producer(int,bool)
        Args:
            producer_id: specifies the id of a producer to remove.
            ignore_not_found: if it is `False`, raies a `KeyError` when such a `producer_id` not fou
            Defaults to `False`
        """
        with self.heap_lock:
            if producer_id not in self.producer_by_id and ignore_not_found:
                return

            p = self.producer_by_id[producer_id]
            self._remove_from_heaps(p)

            del self.producer_by_id[producer_id]

    def _remove_from_heaps(self, producer):
        try:
            self.empty_heap.remove(producer)
        except k3heap.NotFound:
            pass

        try:
            self.consumable_heap.remove(producer)
        except k3heap.NotFound:
            pass

    def get(self):
        """
        Returns an item.
        """
        while True:
            with self.heap_lock:
                try:
                    p = self.consumable_heap.get()
                except k3heap.Empty:
                    raise Empty("no more queue has any item")

                try:
                    # NOTE: if p.iterable blocks, everything is blocked
                    val = p.get()

                except Empty:
                    self.consumable_heap.remove(p)
                    self.empty_heap.push(p)

                    # try next consumable queue
                    continue

                self.consumable_heap.sift(p)

                return val

    def __str__(self):
        qs = []
        for cq in self.producer_by_id.values():
            qs.append(str(cq))

        return " ".join(qs)
