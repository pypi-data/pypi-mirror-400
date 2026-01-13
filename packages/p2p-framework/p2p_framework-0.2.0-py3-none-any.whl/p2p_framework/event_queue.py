from dataclasses import dataclass
from multiprocessing import Queue
from random import choice

from p2p_framework.types import MsgTo


@dataclass
class EventQueue:
    group_data: dict[type, dict[str, Queue]]

    def put(self, obj: object) -> bool:
        """
        Sends obj to a random event handler for type(obj)
        """
        t: type = type(obj)
        qs = self.group_data[t]
        random_q = choice(list(qs.values()))
        random_q.put_nowait(obj)
        return True

    def broadcast(self, obj: MsgTo) -> bool:
        """
        Broadcasts obj to all event handlers for type(obj)
        """
        t: type = type(obj)
        qs = self.group_data[t]
        for q in qs.values():
            q.put_nowait(obj)
        return True
