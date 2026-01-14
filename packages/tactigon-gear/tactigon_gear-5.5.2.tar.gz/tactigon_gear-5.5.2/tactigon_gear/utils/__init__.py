from uuid import uuid4
from queue import Full, Empty
from multiprocessing import get_context
from multiprocessing.queues import Queue

class RollingQueue(Queue):
    def __init__(self, maxsize: int = 0):
        ctx = get_context()
        Queue.__init__(self, maxsize=maxsize, ctx=ctx)

    def put(self, obj, block: bool = True, timeout: float | None = None):
        try:
            Queue.put(self, obj, block, timeout)
        except Full as e:
            Queue.get_nowait(self)
            Queue.put(self, obj, block, timeout)

class AdvancedQueue(Queue):
    _item_list = []

    def __init__(self, maxsize: int = 0):
        ctx = get_context()
        Queue.__init__(self, maxsize=maxsize, ctx=ctx)

    def put(self, item: any, block: bool = True, timeout: float | None = None) -> str: #type: ignore
        _uuid = uuid4().hex
        Queue.put(self, (_uuid, item), block, timeout)
        self._item_list.append(_uuid)
        return _uuid

    def get(self, block: bool = True, timeout: float | None = None):
        _uuid, item = Queue.get(self, block, timeout)
        self._item_list.pop(self._item_list.index(_uuid))
        return item

    def check(self, item: str) -> bool:
        return item not in self._item_list