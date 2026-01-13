from dataclasses import dataclass
from datetime import timedelta
from typing import Awaitable, Callable, Optional
from p2p_framework.event_queue import EventQueue
from p2p_framework.networker import Networker
from p2p_framework.types import (
    HandlerAndData,
    MsgFrom,
    MsgTo,
    PeerConnected,
    PeerDisconnected,
)


type RequestHandler[T: MsgTo] = Callable[
    [MsgFrom[T], EventQueue, Networker], Awaitable[None]
]


@dataclass
class RequestHandlerAndData[T: MsgTo](HandlerAndData):
    handler: RequestHandler[T]
    t: type[T]


type PeriodicHandler = Callable[[EventQueue, Networker], Awaitable[None]]


@dataclass
class PeriodicHandlerAndData(HandlerAndData):
    handler: PeriodicHandler
    dt: timedelta


type WorkerHandler[T] = Callable[
    [Optional[T], EventQueue, Networker, dict], Awaitable[None]
]


@dataclass
class WorkerHandlerAndData[T](HandlerAndData):
    handler: WorkerHandler[T]
    t: Optional[type[T]]


type EventHandler[T] = Callable[[T, EventQueue, Networker], Awaitable[None]]

type Handler[T] = RequestHandler | PeriodicHandler | WorkerHandler | EventHandler


@dataclass
class EventHandlerAndData[T: MsgTo | PeerConnected | PeerDisconnected](HandlerAndData):
    handler: EventHandler[T]
    t: type[T]


class ThreadGroup:
    def __init__(self, *threads: HandlerAndData):
        self.threads = threads


class ProcessGroup:
    def __init__(self, *processes: HandlerAndData):
        self.processes = processes
