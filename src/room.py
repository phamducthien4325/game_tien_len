import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from enum import Enum
from src import Player, Game

class RoomStatus(Enum):
    WAITING = 'waiting'
    FULL_WAITING = 'full_waiting'
    PLAYING = 'playing'

class Room:
    def __init__(self, room_name: str, client_name: str):
        self.room_name = room_name
        self.host_name = client_name
        self.players_name = [client_name]
        self.room_status = RoomStatus.WAITING
        self.game = None
        self.Players = []
    
    def add_player(self, client_name: str):
        self.players_name.append(client_name)
        if len(self.players_name) == 4:
            self.room_status = RoomStatus.FULL_WAITING

    def status(self) -> str:
        result = f"Room Name: {self.room_name}\n"
        result += f"Host: {self.host_name}\n"
        result += f"Players: {[player for player in self.players_name]}\n"
        result += f"Status: {self.room_status.value}"
        return result
    
    def number_of_players(self) -> int:
        return len(self.players_name)
    
    def remove_player(self, client_name: str):
        if client_name in self.players_name:
            self.players_name.remove(client_name)
            if len(self.players_name) == 0:
                return True
        return False
    
    def start_game(self):
        self.room_status = RoomStatus.PLAYING
        for i in range(len(self.players_name)):
            new_player = Player(self.players_name[i])
            self.Players.append(new_player)
        self.game = Game(*self.Players)

    def get_previous_cards(self):
        if self.game == None:
            return None
        return self.game.get_previous_cards()