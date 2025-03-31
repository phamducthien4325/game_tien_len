import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from socket import *
import signal
import sys
import threading
import pickle
from functools import partial
from src import Room, RoomStatus, Card, classify_hand, Player, check_cards, get_card_from_str, HandType, is_suitable_for_previous_hand
from command_type import (
    ServerCommandType, 
    ClientCommandType,
)

class Server:
    Players = []
    Rooms = {}

    def __init__(self, HOST, PORT):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) # Allow the server to reuse the same port when the previous connection is not completely closed
        self.socket.bind((HOST, PORT))
        self.socket.listen(12)
        print('The server is ready to receive')

    def listen(self):
        while True:
            connectionSocket, addr = self.socket.accept()
            client = {'client_name': None, 'connectionSocket': connectionSocket, 'addr': addr, 'room': None}
            self.Players.append(client)
            client_thread = threading.Thread(target=self.handle_client, args=(client,), daemon=True)
            client_thread.start() 


    def handle_client(self, client):
        connectionSocket = client['connectionSocket']
        addr = client['addr']
        while True:
            serialized_data = connectionSocket.recv(4096)
            if not serialized_data:
                print(f"Client {addr} disconnected.")
                self.Players.remove(client)
                # TODO: remove client from Rooms
                connectionSocket.close()
                break
            
            client_message = pickle.loads(serialized_data)

            match client_message['type']:
                case ClientCommandType.CONNECT_TO_SERVER:
                    client_name = client_message['name']
                    is_valid_name = True
                    for player in self.Players:
                        if player['client_name'] == client_name:
                            rename_message = {'message': f"Name {client_name} is already taken.", 'type': ServerCommandType.RENAME_CLIENT}
                            connectionSocket.send(pickle.dumps(rename_message))
                            is_valid_name = False
                            break
                    if is_valid_name:
                        print(f"Client {client_name} connected from {addr}")
                        client['client_name'] = client_name
                        self.pick_room(client)

                case ClientCommandType.EXIT:
                    print(f"Clien from {addr} disconnected.")
                    connectionSocket.close()
                    self.Players.remove(player)
                    # TODO: remove client from Players and Rooms
                    break

                case ClientCommandType.CREATE_ROOM:
                    room_name = client_message['room_name']
                    if room_name in Server.Rooms.keys():
                        rename_room_message = {'message': f"Room {room_name} already exists!", 'type': ServerCommandType.RENAME_ROOM}
                        connectionSocket.send(pickle.dumps(rename_room_message))
                    else:
                        new_room = Room(room_name, client_message['client_name'])
                        Server.Rooms[room_name] = new_room
                        print(f"Room {room_name} created successfully!")
                        client['room'] = new_room
                        message = f"Room {room_name} created successfully!"
                        message += f"\nYou are the host of room: {room_name}."
                        message += f"\nRoom status:\n{new_room.status()}"
                        room_status_message = {'message': message, 'is_host': True, 'type': ServerCommandType.WAIT_ROOM}
                        connectionSocket.send(pickle.dumps(room_status_message))

                case ClientCommandType.RELOAD_ROOM:
                    self.pick_room(client)

                case ClientCommandType.JOIN_ROOM:
                    self.handle_join_room(client, client_message['room_name'])

                case ClientCommandType.START_GAME:
                    room = client['room']
                    if room.number_of_players() == 1:
                        message = f"Room {room.room_name} has only one player!"
                        message += "\nPlease wait for other players to join."
                        room_status_message = {'message': message, 'is_host': True, 'type': ServerCommandType.WAIT_ROOM}
                        connectionSocket.send(pickle.dumps(room_status_message))
                    else:
                        message = f"Room {room.room_name} is starting the game!"
                        room_message = {'message': message, 'type': ServerCommandType.ROOM_MESSAGE, 'clear_screen': False}
                        self.room_message(room.room_name, room_message)
                        self.handle_start_game(room)
                        
                case ClientCommandType.PLAY_HAND:
                    player_name = client['client_name']
                    room_name = client_message['room_name']
                    room = Server.Rooms[room_name]
                    player = room.get_player_from_name(player_name)
                    previous_cards = room.get_previous_cards()
                    str_cards = client_message['play_hand']
                    if previous_cards != None:
                        previous_hand_type = classify_hand(previous_cards)
                    is_pass = False
                    if str_cards == "pass":
                        if previous_cards == None:
                            tmp = "You cannot pass in the first turn of a cycle."
                            tmp_message = {'message': tmp, 'type': ServerCommandType.PROMPT_CARDS, 'clear_screen': False, 'room_name': room_name}
                            self.room_message(room.room_name, tmp_message, reciver_name=player_name)
                            continue
                        is_pass = True

                    if not is_pass:
                        if not check_cards(str_cards):
                            tmp = "Invalid card format. Please try again."
                            tmp_message = {'message': tmp, 'type': ServerCommandType.PROMPT_CARDS, 'clear_screen': False, 'room_name': room_name}
                            self.room_message(room.room_name, tmp_message, reciver_name=player_name)
                            continue
                        cards = [get_card_from_str(card) for card in str_cards.split()]
                        is_valid = True
                        for card in cards:
                            if not player.is_card_in_hand(card):
                                tmp = f"You don't have card {card} in your hand. Please try again."
                                tmp_message = {'message': tmp, 'type': ServerCommandType.PROMPT_CARDS, 'clear_screen': False, 'room_name': room_name}
                                self.room_message(room.room_name, tmp_message, reciver_name=player_name)
                                is_valid = False
                                break
                        if not is_valid:
                            continue
                        played_type = classify_hand(cards)
                        if played_type == HandType.INVALID:
                            tmp = "Invalid hand. Please try again."
                            tmp_message = {'message': tmp, 'type': ServerCommandType.PROMPT_CARDS, 'clear_screen': False, 'room_name': room_name}
                            self.room_message(room.room_name, tmp_message, reciver_name=player_name)
                            continue
                        if not is_suitable_for_previous_hand(cards, previous_cards):
                            tmp = f"Invalid hand. You cannot play {played_type} {cards} after {previous_hand_type} {previous_cards}. Please try again."
                            tmp_message = {'message': tmp, 'type': ServerCommandType.PROMPT_CARDS, 'clear_screen': False, 'room_name': room_name}
                            self.room_message(room.room_name, tmp_message, reciver_name=player_name)
                            continue
                    else:
                        cards = previous_cards
                        played_type = classify_hand(cards)

                    if room.game.play_cards(player_name, cards) == f"Player {player_name} wins!":
                        message = f"Player {player_name} wins!"
                        room_message = {'message': message, 'type': ServerCommandType.ROOM_MESSAGE, 'clear_screen': False}
                        self.room_message(room.room_name, room_message)
                        message = f"You are back to the room."
                        message += f"\nRoom status:\n{room.status()}"
                        room_status_message = {'message': message, 'is_host': False, 'type': ServerCommandType.WAIT_ROOM}
                        self.room_message(room.room_name, room_status_message, exclude_player_name=room.host_name)
                        room_status_message = {'message': message, 'is_host': True, 'type': ServerCommandType.WAIT_ROOM}
                        self.room_message(room.room_name, room_status_message, reciver_name=room.host_name)
                    else:
                        if is_pass:
                            message = f"Player {player_name} passed."
                        else:
                            message = f"Player {player_name} played {played_type} {cards}."
                        room_message = {'message': message, 'type': ServerCommandType.ROOM_MESSAGE, 'clear_screen': False}
                        self.room_message(room.room_name, room_message)
                        current_player_name = room.get_current_player_name()
                        message = f"It's your turn to play!"
                        previous_cards = room.get_previous_cards()
                        if previous_cards != None:
                            previous_hand_type = classify_hand(previous_cards)
                            message += f"\nPrevious cards played {previous_hand_type} hand: {previous_cards}"
                        else:
                            message += f"\nA new turn cycle has started, you can play any cards."
                        message += "\nYour cards: "
                        message += room.get_card_of_player(current_player_name)
                        message += "Please enter the card you want to play (e.g., 1h for Ace of Hearts): "
                        send_message = {'message': message, 'room_name': room.room_name, 'type': ServerCommandType.PROMPT_CARDS, 'clear_screen': False}
                        self.room_message(room.room_name, send_message, reciver_name=current_player_name)
                
                case _:
                    print("Unknown command type")

    def handle_start_game(self, room: Room):
        room.start_game()

        deck_dict = room.get_player_decks()
        for player_name in room.get_client_name_list():
            deck = deck_dict[player_name]
            message = f"Your cards: {deck}"
            room_message = {'message': message, 'type': ServerCommandType.ROOM_MESSAGE, 'clear_screen': False}
            self.room_message(room.room_name, room_message, reciver_name=player_name)

        first_player_name = room.get_first_player_name()
        first_player_message = f"Player {first_player_name} starts the game."
        room_message = {'message': first_player_message, 'type': ServerCommandType.ROOM_MESSAGE, 'clear_screen': False}
        self.room_message(room.room_name, room_message)

        current_player_name = room.get_current_player_name()
        message = f"It's your turn to play!"
        previous_cards = room.get_previous_cards()
        if previous_cards != None:
            previous_hand_type = classify_hand(previous_cards)
            message += f"\nPrevious cards played {previous_hand_type} hand: {previous_cards}"
        else:
            message += f"\nA new turn cycle has started, you can play any cards."
        message += "\nYour cards: "
        message += room.get_card_of_player(current_player_name)
        message += "Please enter the card you want to play (e.g., 1h for Ace of Hearts): "
        send_message = {'message': message, 'room_name': room.room_name, 'type': ServerCommandType.PROMPT_CARDS, 'clear_screen': False}
        self.room_message(room.room_name, send_message, reciver_name=current_player_name)

    def handle_join_room(self, client, room_name):
        if room_name not in Server.Rooms.keys():
            message = f"Room {room_name} does not exist!"
            message += "\nPlease choose another room."
            if len(Server.Rooms) == 0:
                message += '\nThere are no rooms available!'
            else:
                message += '\nAvailable rooms:'
            for room_name, room in Server.Rooms.items():
                message += "\n---------"
                message += f"\nRoom Name: {room_name}\nHost: {room.host_name}\nNumber of players: {room.number_of_players()}"
            connectionSocket = client['connectionSocket']
            room_status_message = {'message': message, 'type': ServerCommandType.PICKING_ROOM}
            connectionSocket.send(pickle.dumps(room_status_message))
        else:
            room = Server.Rooms[room_name]
            if room.room_status == RoomStatus.WAITING:
                room.add_player(client['client_name'])
                client['room'] = room
                message = f"You have joined room {room_name} successfully!"
                message += f"\nRoom status:\n{room.status()}"
                room_status_message = {'message': message, 'is_host': False, 'type': ServerCommandType.WAIT_ROOM}
                connectionSocket = client['connectionSocket']
                connectionSocket.send(pickle.dumps(room_status_message))
                message = f"{client['client_name']} has joined the room!"
                message += f"\nRoom status:\n{room.status()}"
                room_message = {'message': message, 'type': ServerCommandType.ROOM_MESSAGE, 'clear_screen': False}
                self.room_message(room_name, room_message, exclude_player_name=client['client_name'])
            else:
                message = f"Room {room_name} is not available for joining!"
                message += "\nPlease choose another room."
                if len(Server.Rooms) == 0:
                    message += '\nThere are no rooms available!'
                else:
                    message += '\nAvailable rooms:'
                for room_name, room in Server.Rooms.items():
                    message += "\n---------"
                    message += f"\nRoom Name: {room_name}\nHost: {room.host_name}\nNumber of players: {room.number_of_players()}"
                connectionSocket = client['connectionSocket']
                room_status_message = {'message': message, 'type': ServerCommandType.PICKING_ROOM}
                connectionSocket.send(pickle.dumps(room_status_message))

    def room_message(self, room_name, message, exclude_player_name=None, reciver_name=None):
        room = Server.Rooms[room_name]
        if reciver_name:
            for player in self.Players:
                if player['client_name'] == reciver_name:
                    client_socket = player['connectionSocket']
                    client_socket.send(pickle.dumps(message))
        else:
            for player_name in room.get_client_name_list():
                if player_name == exclude_player_name:
                    continue
                for player in self.Players:
                    if player['client_name'] == player_name:
                        client_socket = player['connectionSocket']
                        client_socket.send(pickle.dumps(message))
        

    def pick_room(self, client):
        data = {}
        data['message'] = f"Hello {client['client_name']}!"
        data['type'] = ServerCommandType.PICKING_ROOM
        if len(Server.Rooms) == 0:
            data['message'] += '\nThere are no rooms available!'
        else:
            data['message'] += '\nAvailable rooms:'
            for room_name, room in Server.Rooms.items():
                data['message'] += "\n---------"
                data['message'] += f"\nRoom Name: {room_name}\nHost: {room.host_name}\nNumber of players: {room.number_of_players()}"
        client['connectionSocket'].send(pickle.dumps(data))

def signal_handler(sig, frame, server):
    print('\nShutting down server...')
    for player in server.Players:
        try:
            player['connectionSocket'].close()
        except Exception as e:
            print(f"Error closing connection for {player['client_name']}: {e}")
    server.socket.close()
    sys.exit(0)

if __name__ == '__main__':
    HOST = ''
    PORT = 12001
    server = Server(HOST, PORT)
    signal.signal(signal.SIGINT, partial(signal_handler, server=server))  # Handle Ctrl+C
    server.listen()