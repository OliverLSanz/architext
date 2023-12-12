from .verb import Verb
from .. import util
from .. import strings

class Look(Verb):
    """Shows room and items info to players"""

    command = _('look')

    def process(self, message):
        command_length = len(self.command) + 1
        if message[command_length:]:
            self.show_item_or_exit(message[command_length:])
        else:
            self.show_current_room()
        self.finish_interaction()

    def show_item_or_exit(self, partial_name):
        selected_entity = util.name_to_entity(self.session, partial_name, substr_match=['room_items', 'room_exits', 'inventory'])

        if selected_entity == 'many':
            self.session.sender.send_to_client(strings.many_found)
        elif selected_entity is None:
            self.session.sender.send_to_client(strings.not_found)
        else:
            self.session.sender.send_to_client(f"👁 {selected_entity.name}\n{selected_entity.description if selected_entity.description else strings.default_description}")

    def show_current_room(self, show_world_name=False):
        here = self.session.repository.get_user_room_and_contents(self.session.user_id)
        title = here.room.name + "\n"
        description = (here.room.description if here.room.description else strings.default_description) + "\n"

        listed_exits = [exit.name for exit in here.exits if exit.is_listed()]
        if len(listed_exits) > 0:
            exits = (', '.join(listed_exits))
            exits = _("⮕ Exits: {exits}.\n").format(exits=exits)
        else:
            exits = ""

        listed_items = [item.name for item in here.items if item.is_listed()]
        if len(listed_items) > 0:
            items = _('👁 You see ')+(', '.join(listed_items))
            items = items + '.\n'
        else:
            items = ''

        players_here = self.session.repository.get_visible_users_in_room(here.room.id)
        players_here = [user for user in players_here if user.id != self.session.user_id]
        if len(players_here) < 1:
            players_here = ""
        elif len(players_here) == 1:
            players_here = _("{player_name} is here").format(player_name=players_here[0].name)
        else:
            players_list = ', '.join([f'{user.name}' for user in players_here])
            players_here = _("Players here: {players_list}").format(players_list=players_list)
        players_here = f'👤 {players_here}.' + '\n' if players_here != '' else ''
        underline = '─'*len(title)
        line_break = '\n' if (items or players_here or exits) else ''
        message = (f"""{title}{underline}\n{description}{line_break}{items}{players_here}{exits}""")
        
        if show_world_name:
            world_name = strings.box(_('You are in ') + self.session.repository.get_world_by_state_id(here.room.world_state_id).name)
            message = world_name + '\n' + message

        self.session.sender.send_to_client(message)
