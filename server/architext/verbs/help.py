from . import verb
from .. import util
import re

class Help(verb.Verb):
    """Shows a help message to the user"""
    regex_command = True
    verbtype = verb.VERSATILE

    general_help = _('help')
    topic_help = _('help (?P<topic>.+)')
    command = [general_help, topic_help]

    def process(self, message):
        match = util.match(self.command, message)
        
        topic = match.get('topic')
        if topic is not None:
            topic = topic.strip()
        
        if topic is None:
            out = _(
                # '┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n'
                # '┃   Architext\'s help hub   ┃\n'
                # '┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n'
                'ARCHITEXT HELP HUB\n'
                '\n'
                'If you are new, just try out writing the following verbs an you\'ll be good to go:\n'
                '  "look"  "look <something>"  "go <somewhere>"  "say <something>"\n'
                'Also note that you can use "exitworld" to travel to other worlds.\n'
                '\n'
                'Now go and have fun! Write "help index" when you want to know more.\n'
            )
        elif re.search(_(r"^index$"), topic):
            out = _(
                # '┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n'
                # '┃   Architext\'s help hub   ┃\n'
                # '┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n'
                'ARCHITEXT HELP INDEX\n'
                '\n'
                'Write "help <topic>" to see information regarding one of these topics:\n'
                '    basics ─ moving around and examining your sorroundings.\n'
                '    interaction ─ take and use what\'s around you.\n'
                '    communication ─ talking with other Architexts\n'
                '    building ─ all you need to know to build incredible worlds\n'
                '    multiverse ─ learn about the multiverse nature of Architext.\n'
                '    master ─ tools for game masters to manually make things happen.\n'
                '    interactive building ─ extra tools to make your creations alive.\n'
            )
        elif re.search(_(r"^basics$"), topic):
            out = _(
                # '┏━━━━━━━━━━━━━━━━━━━━━━┓\n'
                # '┃   Architext basics   ┃\n'
                # '┗━━━━━━━━━━━━━━━━━━━━━━┛\n'
                'HELP: BASICS\n'
                '\n'
                'Moving and looking\n'
                '──────────────────\n'
                'Getting your bearings in Architext\'s worlds is quite easy, just use:\n'
                '  look ─ get a description of your current room.\n'
                '  look <thing> ─ look closely at something in your room\n'
                '  go <exit> ─ travel through an exit in your room.\n'
                '  recall ─ return to the first room of your current world\n'
                '\n'
                'Item\'s visibility\n'
                '─────────────────\n'
                'You\'ll often find items in the room\'s description. You can use:\n'
                '  items ─ lists all obvious items in the room.\n'
                '  exits ─ lists all obvious exits\n'
                '\n'
                'There may be hidden items that are not shown by these verbs nor in the room description. Look out for clues!\n'
                '\n'
                ' ⮕ Next topic: "help interaction".'
            )
        elif re.search(_(r"^interaction$"), topic):
            out = _(
                # '┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n'
                # '┃   Interacting with your surroundings   ┃\n'
                # '┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n'
                'HELP: INTERACT WITH ITEMS AND DOORS\n'
                '\n'
                'Carrying items\n'
                '──────────────\n' 
                'There are certain items you can take with you. These items always appear at the room\'s item list shown when you use "look".\n'
                '\n'
                'Use:\n'
                '  take <item> ─ to put an item in your inventory.\n'
                '  drop <item> ─ to drop an item from your inventory.\n'
                '  inventory ─ to see the items you are carrying.\n'
                '\n'
                'Closed doors\n'
                '────────────\n'
                'You may find closed doors in your way. Use:\n'
                '  open <door> ─ to open a closed door. You\'ll need the right key in your inventory.\n'
                '\n'
                'Custom verbs\n'
                '────────────\n'
                'Architexts can create their own verbs, so keep your eyes open. In some worlds/rooms, you might be able to use verbs like "sing", "hide", "turn lever", "read book" and many more. The possibilities are endless!\n'
                '\n'
                ' ⮕ Next topic: "help communication".'
            )
        elif re.search(_(r"^communication$"), topic):
            out = _(
                # '┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n'
                # '┃       Communication       ┃\n'
                # '┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n'
                'HELP: COMMUNICATION\n'
                '\n'
                'You can use the following verbs:\n'
                '  talk <message> ─ to talk with other players in your room.\n'
                '  emote <action> ─ to dance, gesticulate or whatever you want. Just try it!\n'
                '  shout <message> ─ all players in your world will hear you.\n'
                '  who ─ to see who is online\n'
                '  roll <dice> ─ to roll some dice. Dice can be expressions like 1d6, 2d6+1, etc.\n'
                '\n'
                'Don\'t be shy and say hello :)\n'
                '\n'
                ' ⮕ Next topic: "help building".'
            )
        elif re.search(_(r"^multiverse$"), topic):
            out = _(
                # '┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n'
                # '┃       Travelling the multiverse       ┃\n'
                # '┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n'
                'HELP: MULTIVERSE\n'
                '\n'
                'As an Architext you can visit multiple worlds and create your own. While in a world, use:\n'
                '  exitworld  ─ to go to the lobby\n'
                '\n'
                'The Lobby\n'
                '─────────\n'
                'While in the lobby, you can:\n'
                '  Travel to public worlds.\n'
                '  Create a world.\n'
                '  Enter an invite code to join a private world.\n'
                '  Create your own copy of a public world snapshot.\n'
                '  Import the text representation of a world.\n'
                '\n'
                'Write "?" while in the lobby to see all available actions.\n'
                '\n'
                'Managing your worlds\n'
                '────────────────────\n'
                'A newly created world will be:\n'
                '  PRIVATE: Only you can see it in the lobby. You can share its invite code or make it public by using the editworld verb.\n'
                '  PRIVILEGED: Only you can edit it. You can use the editworld verb to allow everyone to edit, or use:\n'
                '    makeeditor <player> ─ to allow that player to edit this world.\n'
                '    removeeditor <player> ─ to revoke the edition permissions on the player.\n'
                '\n'
                'Note that you have a limit on the number of public worlds you can have.\n'
                'To allow everyone to copy your world, you can use snapshots (see "help snapshots").\n'
                '\n'
                'World exports\n'
                '─────────────\n'
                'You can export you worlds using:\n'
                '  export ─ export the current world as a "short" encoded text.\n'
                '  export pretty ─ same as avobe but with a much longer human readable output.\n'
                '\n'
                'It is advised that you export your master pieces and save them into a local text file. This way the world won\'t be lost in case of a technical problem.\n'
                'You can import your exported worlds from the lobby, even in a different Architext server! Feel free to share your creations online.\n'
                '\n'
                ' ⮕ Next topic: "help master".'
            )
        elif re.search(_(r"^building$|^build$"), topic):
            out = _(
                # '┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n'
                # '┃       World building       ┃\n'
                # '┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n'
                'HELP: BUILDING\n'
                '\n'
                'As an Architext you can easily give life to the worlds from your imagination.\n'
                'To use the building verbs you\'ll need to:\n' 
                '  Be in a world you own, or\n'
                '  be in a world that allows all users to edit, or\n'
                '  get a world\'s creator to make you an editor there (see next topic).\n'
                '\n'
                'All you need to know\n'
                '────────────────────\n'
                'You can build anything using just these verbs:\n'
                '  build  ─ to start creating a room adjacent to your current location.\n'
                '  craft  ─ to add a new item to the room.\n'
                '  reform ─ to edit your current room\n'
                '  edit <item or exit> ─ to edit things at the curent room.\n'
                '\n'
                'Some extra verbs\n'
                '────────────────\n'
                'If you want to expand yor toolkit, use:\n'
                '  info ─ to see all the details of your current room, like its unique number.\n'
                '  info <item or exit> ─ as avobe, but for a particular item or exit.\n'
                '\n'
                '  tp <room number> ─ to teleport to any room.\n'
                '  link ─ create exits between any two existing rooms.\n'
                '\n'
                '  deleteroom ─ to delete your current room and all its contents.\n'
                '  deleteexit <exact exit name> ─ to delete an exit.\n'
                '  deleteitem <exact item name> ─ to delete an item.\n'
                '\n'
                'Please note that delete verbs are irreversible and do not ask for confirmation.\n'
                '\n'
                ' ⮕ Next topic: "help multiverse".'

            )
        elif re.search(_(r"^interactive building$"), topic):
            out = _(
                # '┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n'
                # '┃       Interactive Building       ┃\n'
                # '┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n'
                'HELP: INTERACTIVE BUILDING\n'
                '\n'
                'Keys\n'
                '────\n'
                'You can close an exit and assign it a key using:\n'
                '  masterclose <exit> ─ to close an exit.\n'
                '  assignkey <exit> ─ to assign a key to the exit.\n'
                '  masteropen <exit> ─ to open an exit without the need of a key.\n'
                '  deletekey <exit> ─ to delete a previously assigned key.\n'
                '\n'
                'Custom verbs\n'
                '────────────\n'
                'You can easily create your own verbs. Just try it using:\n'
                '  verb <item> ─ add a verb that can be used over that item.\n'
                '  verb room ─ add a verb that can only be used in the room.\n'
                '  verb world ─ add a verb that can be used anywhere.\n'
                '\n'
                'To see and delete existing verbs, use:\n'
                '  seeverb <item/room/world> ─ to show existing verbs\n'
                '  deleteverb <item/room/world> ─ to delete one of its verbs\n'
                '\n'
                'In "help master" you\'ll find the best commands to use in your custom verbs\n'
                '\n'
                'Other resources\n'
                '───────────────\n'
                'Read "help saving" to learn how to spawn previously created items from your custom verbs.\n'
                'Read "help snapshots" to learn how to test and replay puzzles made with custom verbs.\n'
                '\n'
                ' ⮕ Next topic: "help saving".'
                
            )
        elif re.search(_(r"^saving$"), topic):
            out = _(
                # '┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n'
                # '┃       Saving Items       ┃\n'
                # '┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n'
                'HELP: SAVING ITEMS\n'
                '\n'
                'As a creator, you can save and spawn items with:\n'
                '  save <item> ─ save the item.\n'
                '  spawn ─ show the list of saved items.\n'
                '  spawn <item id> ─ spawns a copy of the item in your current room.\n'
                '\n'
                'You can directly craft a saved item instead of manually crafting, saving and deleting it:\n'
                '  craftsaved ─ create a saved item (without placing it in the room)\n'
                '\n'
                'Saved items are key if you want a custom verb that creates an item. Manually craft the item, save and delete it. Now you can spawn the item with a single command!\n'
                '\n'
                'You can also use this to create verbs that modify items. You can save a turned on "lever" and a turned off one. When a player turns the lever, you can delete the existing item and spawn the other one. Easy peasy!\n' 
                '\n'
                ' ⮕ Next topic: "help snapshots".'
            )
        elif re.search(_(r"^snapshots$"), topic):
            out = _(
                # '┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n'
                # '┃       World Snapshots       ┃\n'
                # '┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n'
                'HELP: WORLD SNAPSHOTS\n'
                '\n'
                'In interactive worlds items are carried around, doors are opened and mechanisms are actioned. This may make things like puzzles hard to test and impossible to replay. Unless you use snapshots.\n'
                '\n'
                'Snapshots are frozen saves of the world that you can later deploy, restoring everything to how it was when you made the snapshot.\n'
                '\n'
                'Snapshot verbs:\n'
                '  snapshot ─ create a snapshot of the current state of the world.\n'
                '  deploy ─ see and restore existing snapshots.\n'
                '  deletesnapshot ─ delete a snapshot\n'
                '\n'
                'Using them you can create a puzzle and then snapshot the world. After that you can test the puzzle knowing you can deploy the snapshot to restore it to its initial state.\n'
                '\n'
                'If you build an interactive scape room world, you can use a snapshot to restore everything to its starting position after each playthrough.\n'
                '\n'
                'Snapshots can also be published, so that anyone can make a copy of your world:\n'
                '  publish ─ make public an existing snapshot.\n'
                '  unpublish ─ make private an existing snapshot.\n'
            )
        elif re.search(_(r"^master$"), topic):
            out = _(
                # '┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n'
                # '┃       Game master tools       ┃\n'
                # '┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n'
                'HELP: GAME MASTER TOOLS\n'
                '\n'
                'It\'s a great idea to run role playing and scape room games in Architext worlds.\n'
                'Here are some tools that will let you spice things up as a game master.\n'
                '\n'
                'Master mode\n'
                '───────────\n'
                'Master Mode is a state in which other players won\'t see you and you\'ll be able to cross closed exits.\n'
                '\n'
                'Use:\n'
                '  mastermode ─ enter or leave the master mode\n'
                '\n'
                'Direct text\n'
                '───────────\n'
                'You may want to send text to your players telling them what has just happened, what noise is heard, etc. To send any text, use:\n'
                '  textroom <text> ─ sends the text to all users in the room.\n'
                '  textworld <text> ─ sends the text to all users in the world.\n'
                '  textto \'<user>\' <text> ─ sends the text to the selected user.\n'
                '\n'
                'Other verbs\n'
                '───────────\n'
                '  takefrom \'<user>\' <item> ─ moves the item from the user\'s inventory to the room.\n'
                '  give \'<user\' <item> ─ moves the item from the room to the user\'s inventory\n'
                '  tproom <room number> ─ teleports all users in your room to the selected one.\n'
                '  tpall <room number> ─ teleports all users in the world to the selected room.\n'
                '  tpuser \'<user>\' <room number> ─ teleports the user to the selected room.\n'
                '\n'
                'NPCs\n'
                '────\n'
                'If you want to play out multiple characters in you game, keep in mind that you can connect from multiple accounts at once.\n'
                '\n'
                'Automation\n'
                '──────────\n'
                'You can create custom verbs that automatically trigger any of the commands explained avobe. This way you can create interesting items like a teleporting scroll or a fart machine. Check out "help interactive building" to find out more.\n'
                '\n'
                ' ⮕ Next topic: "help interactive building".'
            )
        else:
            out = _(
                'Topic "{topic}" not found in help.\n'
                'Write just "help" to see the general help page.'
            ).format(topic=topic)
        
        self.session.send_to_client(out)
        self.finish_interaction()

        