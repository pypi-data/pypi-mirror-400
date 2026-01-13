from dataclasses import dataclass
from multiprocessing import Queue
from typing import Iterable, Optional

from p2p_framework.types import INetAddress, MsgTo, PeerId


@dataclass
class NetworkEvent: ...


@dataclass
class Connect(NetworkEvent):
    address: INetAddress


@dataclass
class Disconnect(NetworkEvent):
    peer_id: PeerId


@dataclass
class Broadcast(NetworkEvent):
    msg: MsgTo
    exclude_peer_ids: Optional[list[PeerId]] = None


@dataclass
class Send(NetworkEvent):
    peer_id: PeerId
    msg: MsgTo


@dataclass
class Networker:
    q: Queue[NetworkEvent]

    def connect(self, address: INetAddress) -> Optional[PeerId]:
        self.q.put_nowait(Connect(address))

    def disconnect(self, address: PeerId):
        self.q.put_nowait(Disconnect(address))

    def broadcast(self, msg: MsgTo, exclude_peer_ids: Optional[list[PeerId]] = None):
        self.q.put_nowait(Broadcast(msg, exclude_peer_ids))

    def send(self, address: PeerId, msg: MsgTo):
        self.q.put_nowait(Send(address, msg))

    def get_peer_ids(self) -> Iterable[PeerId]:
        raise NotImplementedError("get_peer_ids is not implemented")

    def get_addresses(self) -> Iterable[INetAddress]:
        raise NotImplementedError("get_addresses is not implemented")
