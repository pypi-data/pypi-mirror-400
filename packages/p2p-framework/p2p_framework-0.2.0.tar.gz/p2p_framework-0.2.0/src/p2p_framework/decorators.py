from dataclasses import dataclass
from datetime import timedelta
from typing import Callable, Optional

from p2p_framework.types import (
    MsgTo,
    PeerConnected,
    PeerDisconnected,
)
from p2p_framework.decorator_types import (
    PeriodicHandler,
    PeriodicHandlerAndData,
    RequestHandler,
    RequestHandlerAndData,
    WorkerHandler,
    WorkerHandlerAndData,
    EventHandler,
    EventHandlerAndData,
)


def request_handler[T: MsgTo](
    name: str,
    msg_type: type[T],
) -> Callable[[RequestHandler[T]], RequestHandlerAndData]:
    def decorator(func: RequestHandler[T]) -> RequestHandlerAndData:
        from p2p_framework.service import MAPPINGS

        MAPPINGS[name] = func
        return RequestHandlerAndData(name, func, msg_type)

    return decorator


def periodic(
    name: str, dt: timedelta
) -> Callable[[PeriodicHandler], PeriodicHandlerAndData]:

    def decorator(func: PeriodicHandler) -> PeriodicHandlerAndData:
        from p2p_framework.service import MAPPINGS

        MAPPINGS[name] = func
        return PeriodicHandlerAndData(name, func, dt)

    return decorator


def worker[T](name: str, listen_for: Optional[type[T]]):
    def decorator(func: WorkerHandler[T]) -> WorkerHandlerAndData[T]:
        from p2p_framework.service import MAPPINGS

        MAPPINGS[name] = func
        return WorkerHandlerAndData(name, func, listen_for)

    return decorator


def event_handler[T: MsgTo | PeerConnected | PeerDisconnected](name: str, t: type[T]):
    def decorator(func: EventHandler[T]) -> EventHandlerAndData[T]:
        from p2p_framework.service import MAPPINGS

        MAPPINGS[name] = func
        return EventHandlerAndData(name, func, t)

    return decorator
