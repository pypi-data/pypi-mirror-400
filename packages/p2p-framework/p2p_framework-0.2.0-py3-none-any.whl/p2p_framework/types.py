from abc import ABC
from dataclasses import dataclass


@dataclass
class MsgTo(ABC): ...


type PeerId = int


@dataclass(frozen=True)
class PeerConnected:
    peer_id: PeerId
    address: INetAddress
    inbound: bool


@dataclass(frozen=True)
class PeerDisconnected:
    peer_id: PeerId
    address: INetAddress
    reason: str


@dataclass(frozen=True)
class INetAddress:
    host: str
    port: int


@dataclass
class HandlerAndData(ABC):
    name: str


@dataclass
class MsgFrom[T: MsgTo](ABC):
    peer_id: PeerId
    msg: T
