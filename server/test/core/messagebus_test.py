from architext.core.adapters.fake_uow import FakeUnitOfWork
from architext.core.messagebus import MessageBus
from architext.core.commands import Command
from unittest.mock import Mock
import pytest # type: ignore


def test_command_handler_is_called() -> None:
    class SomeCommand(Command[str]):
        pass

    fakeHandler = Mock()
    bus = MessageBus(command_handlers={SomeCommand: fakeHandler})
    bus.handle(FakeUnitOfWork(), SomeCommand())

    assert fakeHandler.called


def test_command_without_handlers_raises_exception():
    class SomeCommand(Command[str]):
        pass
    
    bus = MessageBus({})

    with pytest.raises(KeyError):
        bus.handle(FakeUnitOfWork(), SomeCommand())


@pytest.mark.skip(reason="to do")
def test_event_without_handlers_gracefully_does_nothing():
    pass

