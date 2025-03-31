from socket import *
from threading import Thread
import os
import pickle
from command_type import ClientCommandType, ServerCommandType

class Client:
    def __init__(self, HOST, PORT):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.connect((HOST, PORT))
        print('Connected to server')
        self.name = None
        self.talk_to_server()

    def talk_to_server(self):
        self.name = input("Enter your name: ")
        connect_message = {'name': self.name, 'type': ClientCommandType.CONNECT_TO_SERVER}
        self.socket.send(pickle.dumps(connect_message))
        while True:
            server_message = pickle.loads(self.socket.recv(4096))
            if not server_message:
                os._exit(0)
            command_type = server_message['type']
            

            match command_type:
                case ServerCommandType.PICKING_ROOM:
                    print("\033[1;31;40m" + server_message['message'] + "\033[0m")
                    self.handle_room_picking()
                    
                case ServerCommandType.RENAME_CLIENT:
                    print("\033[1;31;40m" + server_message['message'] + "\033[0m")
                    self.name = input("Enter your name: ")
                    connect_message = {'name': self.name, 'type': ClientCommandType.CONNECT_TO_SERVER}
                    self.socket.send(pickle.dumps(connect_message))
                
                case ServerCommandType.RENAME_ROOM:
                    print("\033[1;31;40m" + server_message['message'] + "\033[0m")
                    self.handle_rename_room()

                case ServerCommandType.WAIT_ROOM:
                    print("\033[1;31;40m" + server_message['message'] + "\033[0m")
                    if server_message['is_host'] == False:
                        print("Please wait util the host start the game")
                    else:
                        Thread(target=self.handle_wait_room, daemon=True).start()

                case ServerCommandType.ROOM_MESSAGE:
                    if server_message['clear_screen'] == True:
                        clear_screen()
                    print("\033[1;31;40m" + server_message['message'] + "\033[0m")

                case ServerCommandType.PROMPT_CARDS:
                    # if server_message['clear_screen'] == True:
                    #     clear_screen()
                    print(server_message['message'])
                    self.handle_prompt_cards(server_message['room_name'])

                case _:
                    print("Unknown command type")
        # Thread(target=self.receive_messages, daemon=True).start()
        # self.send_messages()

    def handle_prompt_cards(self, room_name: str):
        str_cards = input(f"Player {self.name}, please enter the card you want to play (e.g., 1h for Ace of Hearts): ")
        input_cards_message = {'play_hand': str_cards, 'type': ClientCommandType.PLAY_HAND, 'client_name': self.name, 'room_name': room_name}
        self.socket.send(pickle.dumps(input_cards_message))
        print(input_cards_message)

    def handle_wait_room(self):
        # print("Please choose the command below:\n\nPress "1" to start the game.\nPress "2" to leave the room.")
        # print("Press "0" to exit.")
        while True:
            print('Press "1" to start the game.')
            command = input()
            if command == '1':
                start_game_message = {'type': ClientCommandType.START_GAME}
                self.socket.send(pickle.dumps(start_game_message))
                print("Starting game...")
                break

    def handle_rename_room(self):
        print("Please enter the new room name:")
        room_name = input()
        rename_room_message = {'room_name': room_name, 'client_name': self.name, 'type': ClientCommandType.CREATE_ROOM}
        self.socket.send(pickle.dumps(rename_room_message))

    def handle_room_picking(self):
        print('Please choose the command below:\nPress "0" to exit.\nPress "1" to create a room.\nPress "2" to reload the room list.\nPress "3" to join a room.')
        while True:
            client_input = input()
            if client_input == '0':
                exit_message = {'type': ClientCommandType.EXIT}
                self.socket.send(pickle.dumps(exit_message))
                print("Exiting...")
                self.socket.close()
                os._exit(0)
                break
            elif client_input == '1':
                room_name = input("Enter room name: ")
                create_room_message = {'room_name': room_name, 'client_name': self.name, 'type': ClientCommandType.CREATE_ROOM}
                self.socket.send(pickle.dumps(create_room_message))
                break
            elif client_input == '2':
                reload_message = {'type': ClientCommandType.RELOAD_ROOM}
                self.socket.send(pickle.dumps(reload_message))
                print("Reloading room list...")
                break
            elif client_input == '3':
                room_name = input("Enter room name: ")
                join_room_message = {'room_name': room_name, 'type': ClientCommandType.JOIN_ROOM}
                self.socket.send(pickle.dumps(join_room_message))
                print(f"Joining room {room_name}...")
                break
            else:
                print("Invalid command. Please try again.")

    def send_messages(self):
        while True:
            client_input = input()
            client_message = f"{self.name}: {client_input}"
            self.socket.send(pickle.dumps(client_message))

def clear_screen():
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == '__main__':
    Client('localhost', 12001)