"""Defines the Session class, used to handle user interaction.
"""
from . import entities
from . import verbs as v
from . import util
import textwrap
from architext.adapters.sender import MessageOptions, Message, AbstractSender

class Session:
    """This class handles interaction with a single user, though it can send messages to other users as well, to inform them of the session's user actions.
    The Session is responsible for:
      - Redirecting messages sent by its client to the right verb to process them.
      - Provide methods to verbs for sending messages from the client's perspective: only to the client, to other users in the client's room, etc.
      - Asking verbs if the interaction is finished so it can keep using the verb to process messages or poll again for a new verb.
      - Handle client disconnection.
    """

    # List of all verbs supported by the session, ordered by priority: if two verbs can handle the same message, the first will have preference.
    verbs = [v.ExportWorld, v.ImportWorld, v.DeleteWorld, v.JoinByInviteCode, v.EnterWorld, v.CreateWorld, v.DeployPublicSnapshot, v.GoToLobby, v.CustomVerb, v.Build, v.Emote, v.Go, v.Help, v.Look, v.Remodel, v.Say, v.Shout, v.Craft, v.EditItem, v.Connect, v.TeleportClient, v.TeleportUser, v.TeleportAllInRoom, v.TeleportAllInWorld, v.DeleteRoom, v.DeleteItem, v.DeleteExit, v.WorldInfo, v.Info, v.Items, v.Exits, v.AddVerb, v.MasterMode, v.TextToOne, v.TextToRoom, v.TextToRoomUnless, v.TextToWorld, v.Take, v.Drop, v.Inventory, v.MasterOpen, v.MasterClose, v.AssignKey, v.Open, v.SaveItem, v.PlaceItem, v.CreateSnapshot, v.DeploySnapshot, v.CheckForItem, v.Give, v.TakeFrom, v.MakeEditor, v.RemoveEditor, v.PubishSnapshot, v.UnpubishSnapshot, v.DeleteSnapshot, v.InspectCustomVerb, v.DeleteCustomVerb, v.EditWorld, v.DeleteKey, v.Who, v.RefreshLobby, v.Recall, v.LobbyHelp, v.RollDice]

    def __init__(self, client_id, sender: AbstractSender):
        self.sender = sender
        self.logger = None  # logger for recording user interaction
        self.client_id = client_id  # direction to send messages to our client
        self.current_verb = v.Login(self)  # verb that is currently handling interaction. It starts with the log-in process.
        self.user = None  # here we'll have an User entity once the log-in is completed.
        self.world_list_cache = None  # when the lobby is shown its values are cached here (see #122).

    def process_message(self, message):
        """This method processes a message sent by the client.
        It polls all verbs, using their can_process method to find a verb that can process the message.
        Then makes that verb the current_verb and lets it handle the message.
        """
        if self.user is not None:
            self.user.reload()
            if self.user.client_id != self.client_id:  # another session has been opened for the same user
                self.send_to_client('Otra sesión ha sido abierta para el mismo usuario. Tu sesión ha sido cerrada.')
                self.disconnect()
                return

        if self.logger:
            self.logger.info('client\n'+message)
        
        if self.current_verb is None:
            for verb in self.verbs:
                if verb.can_process(message, self):
                    self.current_verb = verb(self)
                    break
        
        if self.current_verb is not None:
            try:
                self.current_verb.execute(message)
            except Exception as e:
                self.send_to_client(_("An unexpected error ocurred. It has been notified and it will be soon fixed. You probably can continue playing without further issues."))
                if self.logger:
                    self.logger.exception('ERROR: ' + str(e))
                else:
                    print('ERROR: ' + str(e))
                raise e
            
            if self.current_verb.command_finished():
                self.current_verb = None
        else:
            if self.user.room is None:
                self.send_to_client(_('I don\'t understand that. You can enter "r" to show the lobby menu again.'))
            else: 
                self.send_to_client(_('I don\'t understand that.'))

    def disconnect(self):
        if self.user is not None and self.user.client_id == self.client_id:
            if not self.user.master_mode:
                self.send_to_others_in_room(_("Whoop! {player_name} has gone.").format(player_name=self.user.name))
            self.user.disconnect()
        self.client_id = None

    def send_to_client(self, message, options: MessageOptions = MessageOptions()):
        self.send(self.client_id, "\n\r"+message, options=options)
        if self.logger:
            self.logger.info('server\n'+message)

    def send_to_user(self, user, message, options: MessageOptions = MessageOptions()):
        if user.client_id is not None:
            self.send(user.client_id, "\n\r"+message, options=options)

    def send_to_room_except(self, exception_user, message, options: MessageOptions = MessageOptions(section=False)):
        users_in_this_room = entities.User.objects(room=self.user.room)
        for user in users_in_this_room:
            if user != exception_user:
                self.send(user.client_id, message, options=options)

    def send_to_others_in_room(self, message, options: MessageOptions = MessageOptions(section=False)):
        self.send_to_room_except(self.user, message, options=options)

    def send_to_room(self, message, options: MessageOptions = MessageOptions(section=False)):
        users_in_this_room = entities.User.objects(room=self.user.room)
        for user in users_in_this_room:
            self.send(user.client_id, message, options=options)

    def send_to_all(self, message, options: MessageOptions = MessageOptions(section=False)):
        for user in entities.User.objects:
            self.send(user.client_id, message, options=options)

    def send(self, client_id, message, wrap=False, options: MessageOptions = MessageOptions()):
        if wrap:
            # Wrap the message to 80 characters
            message = '\n'.join(
                # Wrap each line individually 
                ['\n'.join(textwrap.wrap(line, 80, 
                    replace_whitespace=False,
                    expand_tabs=False,
                    drop_whitespace=False,
                    break_on_hyphens=False,
                    break_long_words=False
                    ))
                for line in message.splitlines()]
            )

        self.sender.send(client_id, message=Message(text=message, display=options.display, section=options.section))

    # def send_formatted(self, title, body, cancel=False):
    #     self.send_to_client()
    #     subtitle_bar = '─'*len(title)
    #     cancel = cancel_prompt + '\n\n' if cancel else ''
    #     return f'{title}\n{subtitle_bar}\n{cancel}{body}'


    def set_logger(self, logger):
        self.logger = logger


class GhostSession(Session):
    """This is a ghost session that the system uses to perform automated tasks
    like player defined verbs. The tasks are executed as normal messages that
    a ghost session processes as if it were a normal session. 

    The differences whith a normal session are:
     - A ghost session doesn't respond to the client that is issuing it
       messages, because there is none.
     - A ghost session belongs to the user specified in the field GHOST_USER_NAME.
       This user cannot be used by normal sessions.
     - A ghost session ends as soon as the automated task does.
    """

    MAX_DEPTH = 10  # max number of recursive GhostSessions

    def __init__(self, server, start_room, creator_session, depth=0):
        GHOST_USER_NAME = util.GHOST_USER_NAME  # name of the ghost user
        PLACEHOLDER_SESSION_ID = -1  # with this invalid id, the server won't send messages meant to the session's client 
        super().__init__(PLACEHOLDER_SESSION_ID, server)  # normal session __init__. Assigns session id and server.
        self.current_verb = None  # we want to not have an assigned verb at session creation.
        self.depth = depth
        self.creator_session = creator_session
        if self.depth > self.MAX_DEPTH:
            raise GhostSessionMaxDepthExceeded()

        # retrieve or create ghost user and put in in the right room.
        if entities.User.objects(name=GHOST_USER_NAME):
            self.user = entities.User.objects(name=GHOST_USER_NAME).first()
            self.user.connect(self.client_id)
            self.user.teleport(start_room)
        else:
            self.user = entities.User(name=GHOST_USER_NAME, room=start_room, master_mode=True, password='patata frita')
            self.user.connect(self.client_id)

    def disconnect(self):
        if self.user is not None:
            self.user.disconnect()


class GhostSessionMaxDepthExceeded(Exception):
    """
    Raised when there are too many nested custom verbs in execution.
    i.e. when a custom verb is used that uses another custom verb, and so on.
    """