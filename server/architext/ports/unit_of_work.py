from typing import Generator, Protocol, List
from architext.ports.room_repository import RoomRepository
from architext.ports.user_repository import UserRepository
from architext.core.domain.events import Event
from architext.ports.notificator import Notificator

class UnitOfWork(Protocol):
    rooms: RoomRepository
    users: UserRepository
    notifications: Notificator
    _events: List[Event] = []

    def __exit__(self, *args) -> None:
        self.rollback()

    def publish_events(self, events: List[Event]) -> None:
        self._events += events

    def collect_new_events(self) -> Generator[Event, None, None]:
        while len(self._events) > 0:
            yield self._events.pop()

    def commit(self) -> None:
        self._commit()

    def __enter__(self, *args) -> None:
        pass

    def _commit(self) -> None:
        pass
    
    def rollback(self):
        pass