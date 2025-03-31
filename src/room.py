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
        self.client_name_list = [client_name]
        self.room_status = RoomStatus.WAITING
        self.game = None
        self.Players = []
    
    def add_player(self, client_name: str):
        self.client_name_list.append(client_name)
        if len(self.client_name_list) == 4:
            self.room_status = RoomStatus.FULL_WAITING

    def status(self) -> str:
        result = f"Room Name: {self.room_name}\n"
        result += f"Host: {self.host_name}\n"
        result += f"Players: {[player for player in self.client_name_list]}\n"
        result += f"Status: {self.room_status.value}"
        return result
    
    def number_of_players(self) -> int:
        return len(self.client_name_list)
    
    def remove_player(self, client_name: str):
        if client_name in self.client_name_list:
            self.client_name_list.remove(client_name)
            if len(self.client_name_list) == 0:
                return True
        return False
    
    def start_game(self):
        self.room_status = RoomStatus.PLAYING
        for i in range(len(self.client_name_list)):
            new_player = Player(self.client_name_list[i])
            self.Players.append(new_player)
        self.game = Game(*self.Players)

    def get_previous_cards(self):
        if self.game == None:
            return None
        return self.game.get_previous_cards()
    
    def get_player_decks(self):
        if self.game == None:
            return None
        return self.game.get_player_decks()
    
    def get_client_name_list(self):
        return self.client_name_list
    
    def get_first_player_name(self):
        if self.game == None:
            return None
        return self.game.get_first_player_name()
    
    def get_current_player_name(self):
        if self.game == None:
            return None
        return self.game.get_current_player_name()
    
    def get_card_of_player(self, client_name: str):
        if self.game == None:
            return None
        for player in self.Players:
            if player.name == client_name:
                return player.get_str_cards()
        return None
    
    def get_player_from_name(self, client_name: str) -> Player:
        for player in self.Players:
            if player.name == client_name:
                return player
        return None
    
    def reset_game(self):
        self.Players = []
        self.game = None
        self.room_status = RoomStatus.WAITING