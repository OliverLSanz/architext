"""Defines the Session class, used to handle user interaction.
"""
import entities
import verbs as v

class Session:
    """This class handles interaction with a single user, though it can send messages to other users as well, to inform them of the session's user actions.
    The Session is responsible for:
      - Redirecting messages sent by its client to the right verb to process them.
      - Provide methods to verbs for sending messages from the client's perspective: only to the client, to other users in the client's room, etc.
      - Asking verbs if the interaction is finished so it can keep using the verb to process messages or poll again for a new verb.
      - Handle client disconnection.
    """

    # List of all verbs supported by the session, ordered by priority: if two verbs can handle the same message, the first will have preference.
    verbs = [v.Build, v.Emote, v.Go, v.Help, v.Look, v.Remodel, v.Say, v.Shout, v.Craft, v.EditItem, v.Connect, v.Teleport, v.DeleteRoom, v.DeleteItem, v.DeleteExit, v.Info, v.Items, v.Exits, v.AddVerb, v.MasterMode]

    def __init__(self, session_id, server):
        self.logger = None  # logger for recording user interaction
        self.server = server  # server used to send messages
        self.session_id = session_id  # direction to send messages to our client
        self.current_verb = v.Login(self)  # verb that is currently handling interaction. It starts with the log-in process.
        self.user = None  # here we'll have an User entity once the log-in is completed.
        


    def process_message(self, message):
        """This method processes a message sent by the client.
        It polls all verbs, using their can_process method to find a verb that can process the message.
        Then makes that verb the current_verb and lets it handle the message.
        """
        if self.logger:
            self.logger.info('client\n'+message)
        
        # if there is no current verb, search for a verb in the standard verb list
        if self.current_verb is None:
            for verb in self.verbs:
                if verb.can_process(message):
                    self.current_verb = verb(self)
                    break
        
        if self.current_verb is not None:
            self.current_verb.process(message)
            if self.current_verb.command_finished():
                self.current_verb = None
        else:
            custom_verb = self.search_for_custom_verb(message)
            if custom_verb is not None:
                self.execute_custom_verb(custom_verb)
            else:
                self.send_to_client("No te entiendo.")

    def search_for_custom_verb(self, message):
        if len(message.split(" ", 1)) == 2:  # if the message has the form "verb item"
            target_verb_name, target_item_name = message.split(" ", 1)
            suitable_item_found_in_room = next(filter(lambda i: i.name==target_item_name, self.user.room.items), None)
            if suitable_item_found_in_room is not None:
                suitable_verb_found_in_item = next(filter(lambda v: v.name==target_verb_name, suitable_item_found_in_room.custom_verbs), None)
                if suitable_verb_found_in_item is not None:
                    return suitable_verb_found_in_item
        else:
            suitable_verb_found_in_room = next(filter(lambda v: v.name==message, self.user.room.custom_verbs), None)
            if suitable_verb_found_in_room is not None:
                return suitable_verb_found_in_room
            world = entities.World.objects[0]
            suitable_verb_found_in_world = next(filter(lambda v: v.name==message, world.custom_verbs), None)
            if suitable_verb_found_in_world is not None:
                return suitable_verb_found_in_world
        
        return None
            
    def execute_custom_verb(self, custom_verb):
        import ghost_session
        ghost = ghost_session.GhostSession(self.server, self.user.room)
        for message in custom_verb.commands:
            ghost.process_message(message)
        ghost.disconnect()

    def disconnect(self):
        if self.user is not None:
            if not self.user.master_mode:
                self.send_to_others_in_room("¡Whoop! {} se ha esfumado.".format(self.user.name))
            self.user.disconnect()

    def send_to_client(self, message):
        self.server.send_message(self.session_id, "\n\r"+message)
        if self.logger:
            self.logger.info('server\n'+message)

    def send_to_others_in_room(self, message):
        users_in_this_room = entities.User.objects(room=self.user.room)
        for user in users_in_this_room:
            if user != self.user:
                self.server.send_message(user.client_id, message)

    def send_to_room(self, message):
        users_in_this_room = entities.User.objects(room=self.user.room)
        for user in users_in_this_room:
            self.server.send_message(user.client_id, message)

    def send_to_all(self, message):
        for user in entities.User.objects:
            self.server.send_message(user.client_id, message)

    def set_logger(self, logger):
        self.logger = logger
