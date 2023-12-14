from architext.adapters.sender import MessageOptions
from .verb import Verb
from .. import util
from .. import entities
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
            self.session.send_to_client(strings.many_found)
        elif selected_entity is None:
            self.session.send_to_client(strings.not_found)
        else:
            self.session.send_to_client(f"👁 {selected_entity.name}\n{selected_entity.description if selected_entity.description else strings.default_description}")
    
    def show_current_room(self, show_world_name=False):
        title = self.session.user.room.name
        description = (self.session.user.room.description if self.session.user.room.description else strings.default_description) + '\n'

        listed_exits = [exit.name for exit in self.session.user.room.exits if exit.is_listed()]
        if len(listed_exits) > 0:
            exits = (', '.join(listed_exits))
            exits = _("⮕ Exits: {exits}.\n").format(exits=exits)
        else:
            exits = ""

        listed_items = [item.name for item in self.session.user.room.items if item.is_listed()]
        if len(listed_items) > 0:
            items = _('👁 You see ')+(', '.join(listed_items))
            items = items + '.\n'
        else:
            items = ''

        players_here = entities.User.objects(room=self.session.user.room, client_id__ne=None, master_mode=False)
        players_here = [user for user in players_here if user != self.session.user]
        if len(players_here) < 1:
            players_here = ""
        elif len(players_here) == 1:
            players_here = _("{player_name} is here").format(player_name=players_here[0].name)
        else:
            players_list = ', '.join([f'{user.name}' for user in players_here])
            players_here = _("Players here: {players_list}").format(players_list=players_list)
        players_here = f'👤 {players_here}.' + '\n' if players_here != '' else ''
        line_break = '\n' if (items or players_here or exits) else ''
        message = (f"{description}{line_break}{items}{players_here}{exits}")
        
        if show_world_name:
            world_name = _('You are in ') + self.session.user.room.world_state.get_world().name
            self.session.send_to_client(world_name, MessageOptions(display='box'))
            self.session.send_to_client(title, MessageOptions(section=False, display='underline'))
            self.session.send_to_client(message, MessageOptions(section=False))
        else:
            self.session.send_to_client(title, MessageOptions(display='underline'))
            self.session.send_to_client(message, MessageOptions(section=False))
