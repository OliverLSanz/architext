from unittest.mock import Mock
from architext.core.adapters.fake_uow import FakeUnitOfWork
from architext.core.commands import EnterWorld, TraverseExit, TraverseExitResult, CreateInitialData, CreateConnectedRoom, CreateUser
from architext.core.domain.entities.world import DEFAULT_WORLD
from architext.core import Architext
import pytest # type: ignore
from architext.core.domain.entities.user import User
from architext.core.domain.entities.room import Room
from architext.core.domain.entities.exit import Exit
from architext.core.domain.entities.world import World
from architext.core.domain.events import UserChangedRoom
from architext.core.messagebus import MessageBus


@pytest.fixture
def architext() -> Architext:
    uow = FakeUnitOfWork()
    rabbithole_world = World(
        id="rabbithole",
        name="Down The Rabbit Hole",
        description="A magical place.",
        initial_room_id="rabbitholeroom",
        owner_user_id=None
    )
    rabbithole_room = Room(
        id="rabbitholeroom",
        name="A really big room",
        description="It seems you drank something that made you small.",
        world_id="rabbithole"
    )
    outer_world = World(
        id="outer",
        name="Outer Wilds",
        description="Let's explore the universe!",
        initial_room_id="outerroom",
        owner_user_id=None
    )
    outer_room = Room(
        id="outerroom",
        name="Space",
        description="You are floating in the vastness of the universe, alone.",
        world_id="outer"
    )
    oliver = User(
        id="oliver",
        name="Oliver",
        email="oliver@example.com",
        room_id="rabbitholeroom",
        password_hash=b"asdasd"
    )
    rabbit = User(
        id="rabbituser",
        name="Rabbit",
        email="rabbit@example.com",
        room_id="rabbitholeroom",
        password_hash=b"asdasd"
    )
    explorer = User(
        id="explorer",
        name="Feldspar",
        email="feldspar@example.com",
        room_id="outerroom",
        password_hash=b"asdasd"
    )
    uow.worlds.save_world(rabbithole_world)
    uow.worlds.save_world(outer_world)
    uow.rooms.save_room(rabbithole_room)
    uow.rooms.save_room(outer_room)
    uow.users.save_user(oliver)
    uow.users.save_user(rabbit)
    uow.users.save_user(explorer)
    return Architext(uow)

def test_enter_world_success(architext: Architext):
    architext.handle(EnterWorld(world_id="outer"), client_user_id="oliver")

    oliver = architext._uow.users.get_user_by_id("oliver")
    assert oliver is not None
    assert oliver.room_id == "outerroom"
    room = architext._uow.rooms.get_room_by_id(oliver.room_id)
    assert room is not None
    assert room.world_id == "outer"
    world = architext._uow.worlds.get_world_by_id(room.world_id)
    assert world is not None
    assert world.name == "Outer Wilds"


@pytest.mark.skip(reason="TODO")
def test_enter_world_that_does_not_exist(uow: FakeUnitOfWork, message_bus: MessageBus):
    with pytest.raises(ValueError, match="User is not in a room."):
        message_bus.handle(uow, TraverseExit(exit_name="To Kitchen"), client_user_id="not_in_room")


@pytest.mark.skip(reason="TODO")
def test_user_changed_room_event_gets_invoked(uow: FakeUnitOfWork):
    spy = Mock()
    def handler(uow: FakeUnitOfWork, event: UserChangedRoom):
        assert event.user_id is "in_room"
        assert event.room_entered is "room2"
        assert event.room_left is "room1"
        assert event.exit_used is "To Kitchen"
        spy()
    handlers = {UserChangedRoom: [handler]}
    message_bus = MessageBus(event_handlers=handlers)
    message_bus.handle(uow, TraverseExit(exit_name="To Kitchen"), client_user_id="in_room")
    assert spy.called


@pytest.mark.skip(reason="TODO")
def test_users_get_notified_if_other_enters_or_leaves_room() -> None:
    uow = FakeUnitOfWork()
    bus = MessageBus()
    bus.handle(uow, CreateInitialData())
    user_a = bus.handle(uow, CreateUser(
        email='test@test.com',
        name='testerA',
        password='asdasd'
    ))
    user_b = bus.handle(uow, CreateUser(
        email='test@test.com',
        name='testerB',
        password='asdasd'
    ))
    room = bus.handle(
        uow=uow, 
        command=CreateConnectedRoom(
            name='rrom',
            description='descripdsdas',
            exit_to_new_room_name='go',
            exit_to_new_room_description='hehe',
            exit_to_old_room_name='return',
            exit_to_old_room_description='hoho'
        ),
        client_user_id=user_a.user_id
    )
    bus.handle(
        uow=uow,
        command=TraverseExit(
            exit_name='go'
        ),
        client_user_id=user_a.user_id
    )
    assert user_b.user_id in uow.notifications.notifications
    userb_notifications = uow.notifications.notifications.get(user_b.user_id, None)
    assert userb_notifications is not None
    assert len(userb_notifications) == 1
    userb_noti = userb_notifications[0]
    assert userb_noti.event == 'other_left_room'
    assert userb_noti.data["user_name"] == 'testerA'
