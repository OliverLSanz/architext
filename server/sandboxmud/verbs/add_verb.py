from . import verb
from .. import entities
from .. import util
import functools
import textwrap


class AddVerb(verb.Verb):
    """This verb allows users to create new custom verbs tied to items.
    """

    command = 'verbo'
    item_command = 'verboobjeto '  # command for adding verbs to items
    room_command = 'verbosala'    # command for adding verbs to rooms
    world_command = 'verbomundo'  # command for adding verbs to worlds
    permissions = verb.PRIVILEGED

    @classmethod
    def can_process(cls, message, session):
        if message.startswith(cls.item_command) or message.startswith(cls.room_command) or message.startswith(cls.world_command) and super().can_process(message, session):
            return True
        else:
            return False

    def __init__(self, session):
        super().__init__(session)
        self.world_state = None  # world on which the verb will be added, if it is a world verb
        self.room = None   # room  on which the verb will be added, if it is a room verb
        self.item = None   # item  on which the verb will be added, if it is a item verb
        self.verb_names = None
        self.command_list = []
        self.current_process_function = self.process_first_message

    def process(self, message):
        if message == '/':
            self.session.send_to_client("Creación de verbo cancelada.")
            self.finish_interaction()
        else:
            self.current_process_function(message)

    def process_first_message(self, message):
        # figure out wether it is a world, room or item verb
        if message.startswith(self.item_command):
            self.process_item_name(message)
        elif message.startswith(self.room_command):
            self.process_room_verb_creation(message)
        elif message.startswith(self.world_command):
            self.process_world_verb_creation(message)
        else:
            raise ValueError('invalid message "{}"'.format(message))

    def process_item_name(self, message):
        name = message[len(self.item_command):]
        target_item = util.name_to_entity(self.session, name, loose_match=["saved_items"], substr_match=["room_items", "inventory"])

        if target_item == "many":
            self.session.send_to_client("Hay más de un objeto con un nombre similar a ese. Sé más específico.")
            self.finish_interaction()
        elif target_item is None:
            self.session.send_to_client("No encuentras ningún objeto con ese nombre.")
            self.finish_interaction()
        else:
            self.item = target_item
            self.current_process_function = self.process_verb_names

            if target_item.is_saved():
                self.session.send_to_client(textwrap.dedent(f"""
                    Añadiendo un verbo a "{self.item.item_id}" (objeto guardado)
                    {chr(9472)*(22+len(self.item.item_id))}
                    {chr(10060)} Para cancelar, introduce "/" en cualquier momento.
                    Vas a añadir un verbo que todos los jugadores podrán usar sobre este objeto. Primero introduce el nombre del verbo.
                    Por ejemplo, si escribes "usar", tu verbo se ejecutará cuando un jugador escriba "usar {self.item.name}". Puedes introducir varios nombres separados por un espacio, y todos tendrán el mismo efecto.
                    
                    Nombre(s) del verbo:"""
                ))
            else:
                self.session.send_to_client(textwrap.dedent(f"""
                    Añadiendo un verbo a "{self.item.name}"
                    {chr(9472)*(22+len(self.item.name))}
                    {chr(10060)} Para cancelar, introduce "/" en cualquier momento.
                    Vas a añadir un verbo que todos los jugadores podrán usar sobre este objeto. Primero introduce el nombre del verbo.
                    Por ejemplo, si escribes "usar", tu verbo se ejecutará cuando un jugador escriba "usar {self.item.name}". Puedes introducir varios nombres separados por un espacio, y todos tendrán el mismo efecto.
                    
                    Nombre(s) del verbo:"""
                ))


    def process_room_verb_creation(self, message):
        self.room = self.session.user.room
        out_message  = f'Añadiendo un verbo a la sala\n{chr(9472)*29}\n'
        out_message += f'{chr(10060)} Para cancelar, introduce "/" en cualquier momento.\n\n'
        out_message += f'Vas a añadir un verbo que todos los jugadores podrán usar solo en esta sala. Primero introduce el nombre del verbo.\nPor ejemplo, si escribes "cantar", tu verbo se ejecutará cuando un jugador en esta sala escriba "cantar". Puedes introducir varios nombres separados por un espacio, y todos tendrán el mismo efecto.\n\n'
        out_message += 'Nombre(s) del verbo:'
        self.session.send_to_client(out_message)
        self.current_process_function = self.process_verb_names

    def process_world_verb_creation(self, message):
        self.world_state = self.session.user.room.world_state
        out_message  = f'Añadiendo un verbo al mundo\n{chr(9472)*29}\n'
        out_message += f'{chr(10060)} Para cancelar, introduce "/" en cualquier momento.\n\n'
        out_message += f'Vas a añadir un verbo que los jugadores podrán usar en cualquier momento. Primero introduce el nombre del verbo.\nPor ejemplo, si escribes "cantar", tu verbo se ejecutará cuando cualquier jugador escriba "cantar". Puedes introducir varios nombres separados por un espacio, y todos tendrán el mismo efecto.\n\n'
        out_message += 'Nombre(s) del verbo:'
        self.session.send_to_client(out_message)
        self.current_process_function = self.process_verb_names

    def process_verb_names(self, message):
        verb_names = message.split()
        if len(verb_names) == 0:
            self.session.send_to_client("Debes introducir algún nombre")
            return
        for name in verb_names:
            if not self.is_valid_verb_name(message):                
                self.session.send_to_client("En tu lista hay un nombre de verbo inválido. Vuelve a probar.")
                return
        self.verb_names = verb_names
        out_message  = f'Ahora escribe la primera acción a realizar cuando un jugador use el verbo\n{chr(9472)*74}\n  {chr(9679)} Puedes usar cualquier acción que puedas hacer como jugador y editor.\n  {chr(9679)} Cuando se use, será como si un jugador fantasma apareciese en la habitación donde se usa el verbo e hiciese las acciones por ti.\n  {chr(9679)} Puedes escribir ".usuario" para referirte al jugador que usa el verbo.\n\nPuedes seguir escribiendo acciones después de la primera, uno por línea, como harías mientras juegas (aunque no verás ninguna respuesta). Cuando hayas acabado, introduce "OK".\n\nAcciones del verbo: ("OK" para terminar)'
        self.session.send_to_client(out_message)
        self.current_process_function = self.process_command

    def process_command(self, message):
        if message in ['OK', 'ok'] and len(self.command_list) > 0:
            self.build_verb()
            self.finish_interaction()
        elif self.is_valid_command(message):
            self.command_list.append(message)
        else:
            self.session.send_to_client("Ese comando no es válido y ha sido ignorado.")

    def build_verb(self):
        new_verb = entities.CustomVerb(names=self.verb_names, commands=self.command_list)
        if self.item is not None:
            self.item.add_custom_verb(new_verb)
            self.session.send_to_client('Verbo creado! Escribe "{} {}" para desatar su poder!'.format(self.verb_names[0], self.item.name))
        elif self.room is not None:
            self.room.add_custom_verb(new_verb)
            self.session.send_to_client('Verbo de sala creado! Escribe "{}" para desatar su poder!'.format(self.verb_names[0]))
        elif self.world_state is not None:
            self.world_state.add_custom_verb(new_verb)
            self.session.send_to_client('Verbo de sala creado! Escribe "{}" para desatar su poder!'.format(self.verb_names[0]))
        else:
            raise RuntimeError("Unreachable code reached ¯\_(ツ)_/¯")

    def is_valid_verb_name(self, name):
        # TODO checks if a name is a valid verb name
        return True

    def is_valid_command(self, command):
        if not command:
            return False
        return True

class InspectCustomVerb(verb.Verb):
    command = 'ver verbo de '
    world_command = 'ver verbo de mundo'
    room_command = 'ver verbo de sala'

    def process(self, message):
        out_message = ""
        
        if message == self.world_command:
            self.inspectable_custom_verbs = self.session.user.room.world_state.custom_verbs
        elif message == self.room_command:
            self.inspectable_custom_verbs = self.session.user.room.custom_verbs
        else:
            item_name = message[len(self.command):]
            selected_item = util.name_to_entity(self.session, item_name, loose_match=["saved_items"], substr_match=["room_items", "inventory"])

            if selected_item == "many":
                self.session.send_to_client("Hay más de un objeto con un nombre similar a ese. Sé más específico.")
                self.finish_interaction()
                return
            elif selected_item is None:
                self.session.send_to_client("No encuentras ningún objeto con ese nombre.")
                self.finish_interaction()
                return
            else:
                self.inspectable_custom_verbs = selected_item.custom_verbs
                if selected_item.is_saved():
                    out_message += f"Objeto guardado: {selected_item.item_id}\n"
                else:
                    out_message += f"Objeto: {selected_item.name}\n"
                    
        
        if not self.inspectable_custom_verbs:
            out_message += "No tiene verbos para inspeccionar."
            self.session.send_to_client(out_message)
            self.finish_interaction()
            return

        out_message += 'Qué verbo custom quieres inspeccionar?\n'
        out_message += self.get_custom_verb_list()
        self.session.send_to_client(out_message)
        self.process = self.process_menu_option


    def get_custom_verb_list(self):
        list = ''
        for index, custom_verb in enumerate(self.inspectable_custom_verbs):
            list += '{}. {}\n'.format(index, custom_verb.names)
        list += '\n\n"/" para cancelar'
        return list

    def process_menu_option(self, message):
        if message == '/':
            self.session.send_to_client('Cancelado.')
            self.finish_interaction()
            return

        try:
            index = int(message)
            if index < 0:
                raise ValueError
        except ValueError:
            self.session.send_to_client("Introduce un número")
            return

        try:
            chosen_custom_verb = self.inspectable_custom_verbs[index]
        except IndexError:
            self.session.send_to_client("Introduce el número correspondiente a uno de los verbos")
            return

        message = functools.reduce(lambda a,b: '{} / {}'.format(a,b), chosen_custom_verb.names).upper() + "\n"
        message += functools.reduce(lambda a, b: '{}\n{}'.format(a,b), chosen_custom_verb.commands)
        message += '\nOK'
        self.session.send_to_client(message)
        self.finish_interaction()

class DeleteCustomVerb(verb.Verb):
    command = 'eliminarverbo '
    permissions = verb.PRIVILEGED

    def process(self, message):
        if message == 'eliminarverbo mundo':
            self.deletable_custom_verbs = self.session.user.room.world_state.custom_verbs
            target_name = 'este mundo'
        elif message == 'eliminarverbo sala':
            self.deletable_custom_verbs = self.session.user.room.custom_verbs
            target_name = f'"{self.session.user.room.name}" (sala)'
        else:
            item_name = message[len(self.command):]

            selected_item = util.name_to_entity(self.session, item_name, loose_match=["saved_items"], substr_match=["room_items", "inventory"])

            if selected_item == "many":
                self.session.send_to_client('Hay varios objetos con un nombre similar a ese. Sé más específico.')
                self.finish_interaction()
                return
            elif selected_item is None:
                self.session.send_to_client('No sé de dónde quieres eliminar verbos. Escribe el nombre de un objeto, "mundo" o "sala".')
                self.finish_interaction()
                return
            target_name = (
                f'"{selected_item.item_id}" (objeto guardado)'
                if selected_item.is_saved()
                else f'"{selected_item.name}" (objeto)'
            )
            self.deletable_custom_verbs = selected_item.custom_verbs

        if not self.deletable_custom_verbs:
            self.session.send_to_client(f"En {target_name} no hay verbos para eliminar.")
            self.finish_interaction()
            return

        out_message = f"""\
        Eliminando verbo de {target_name}
        {chr(9472)*(21+len(target_name))}
        {chr(10060)} Para cancelar, introduce '/' en cualquier momento.

        ¿Qué verbo quieres eliminar? (introduce el número correspondiente)
        {self.get_custom_verb_list()}""".replace('    ', '')
        self.session.send_to_client(out_message)
        self.process = self.process_menu_option

    def get_custom_verb_list(self):
        list = ''
        for index, custom_verb in enumerate(self.deletable_custom_verbs):
            list += f' {index} - {custom_verb.names}\n'
        return list

    def process_menu_option(self, message):
        if message == '/':
            self.session.send_to_client('Borrado de verbo cancelado.')
            self.finish_interaction()
            return

        try:
            index = int(message)
            if index < 0:
                raise ValueError
        except ValueError:
            self.session.send_to_client("Introduce un número")
            return

        try:
            chosen_custom_verb = self.deletable_custom_verbs[index]
        except IndexError:
            self.session.send_to_client("Introduce el número correspondiente a uno de los verbos")
            return

        chosen_custom_verb.delete()
        self.session.send_to_client('Verbo borrado.')
        self.finish_interaction()
        

