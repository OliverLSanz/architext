from .verb import Verb
from .. import util
from .. import entities

class Look(Verb):
    """Shows room and items info to players"""

    command = 'mirar'

    def process(self, message):
        command_length = len(self.command) + 1
        if message[command_length:]:
            self.show_item_or_exit(message[command_length:])
        else:
            self.show_current_room()
        self.finish_interaction()

    def show_item_or_exit(self, partial_name):
        lookable_items = self.session.user.room.items + self.session.user.get_current_world_inventory().items
        names_of_lookable_items = [item.name for item in lookable_items]
        items_he_may_be_referring_to = util.possible_meanings(partial_name, names_of_lookable_items)

        exits_in_room = self.session.user.room.exits
        names_of_exits_in_room = [exit.name for exit in exits_in_room]
        exits_he_may_be_referring_to = util.possible_meanings(partial_name, names_of_exits_in_room)
        

        if len(items_he_may_be_referring_to) + len(exits_he_may_be_referring_to) == 1:
            if len(items_he_may_be_referring_to) == 1:
                item_name = items_he_may_be_referring_to[0]
                for item in lookable_items:
                    if item.name == item_name:
                        description = item.description if item.description else "No tiene nada de especial"
                        self.session.send_to_client(description)
                        break
            else:
                exit_name = exits_he_may_be_referring_to[0]
                for exit in exits_in_room:
                    if exit.name == exit_name:
                        self.session.send_to_client(exit.description)
                        break
        elif len(items_he_may_be_referring_to) + len(exits_he_may_be_referring_to) == 0:
            self.session.send_to_client("No ves eso por aquí.")
        else:  # it is unclear what the user is referring to
            self.session.send_to_client("¿A cuál te refieres? Sé más específico.")
    
    def show_current_room(self):
        title = self.session.user.room.name + "\n"
        description = self.session.user.room.description + "\n"

        listed_exits = [exit.name for exit in self.session.user.room.exits if exit.is_listed()]
        if len(listed_exits) > 0:
            exits = (', '.join(listed_exits))
            exits = "Salidas: {}.\n".format(exits)
        else:
            exits = ""

        listed_items = [item.name for item in self.session.user.room.items if item.is_listed()]
        if len(listed_items) > 0:
            items = 'Ves '+(', '.join(listed_items))
            items = items + '.\n'
        else:
            items = ''

        players_here = '\n'.join(['{} está aquí.'.format(user.name) for user in entities.User.objects(room=self.session.user.room, client_id__ne=None, master_mode=False) if user != self.session.user])
        players_here = players_here + '\n' if players_here != '' else ''
        message = ("""{title}{description}{items}{players_here}{exits}"""
                    ).format(title=title, description=description, exits=exits, players_here=players_here, items=items)
        self.session.send_to_client(message)