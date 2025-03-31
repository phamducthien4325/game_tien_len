import enum

class ServerCommandType(enum.Enum):
    PICKING_ROOM = 'picking_room'
    RENAME_CLIENT = 'rename_client'
    RENAME_ROOM = 'rename_room'
    WAIT_ROOM = 'wait_room'
    ROOM_MESSAGE = 'room_message'
    PROMPT_CARDS = 'prompt_cards'
    END_GAME = 'end_game'
    

class ClientCommandType(enum.Enum):
    CONNECT_TO_SERVER = 'connect_to_server'
    CREATE_ROOM = 'create_room'
    EXIT = 'exit'
    RELOAD_ROOM = 'reload_room'
    JOIN_ROOM = 'join_room'
    START_GAME = 'start_game'
    PLAY_HAND = 'play_hand'