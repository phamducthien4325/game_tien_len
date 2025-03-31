from .player import Player
from .helper import (
    generate_cards_for_player,
    clear_screen,
)


class Game:
    def __init__(self, *players: Player):
        player1 = players[0]
        player2 = players[1]
        player3 = players[2] if len(players) > 2 else None
        player4 = players[3] if len(players) > 3 else None
        self.players = [player1, player2]
        self.number_of_players = 2
        if player3:
            self.players.append(player3)
            self.number_of_players += 1
        if player4:
            self.players.append(player4)
            self.number_of_players += 1
        self.previous_cards = None
        decks = generate_cards_for_player(self.number_of_players)
        for i in range(self.number_of_players):
            self.players[i].cards = decks[i]
            self.players[i].cards.sort()

        self.current_player_index = 0

    def start_game(self):
        # current_player_index = self.get_first_player()
        # print(f"Player {current_player_index + 1} starts the game.")
        # last_player_index = current_player_index

        # remaining_plyers_per_turn = [i for i in range(self.number_of_players)]
        # while True:
            # if current_player_index == last_player_index:
            #     self.previous_cards = None
            # current_player = self.players[current_player_index]
            # played_cards = current_player.promt_cards(self.previous_cards)
            # if played_cards != self.previous_cards:
            #     last_player_index = current_player_index
            # else:
            #     remaining_plyers_per_turn.remove(current_player_index)
            # self.previous_cards = played_cards
            # if current_player.is_winner():
            #     print(f"Player {current_player_index + 1} wins!")
            #     break
            # current_player_index = (current_player_index + 1) % self.number_of_players
            # while not current_player_index in remaining_plyers_per_turn:
            #     current_player_index = (current_player_index + 1) % self.number_of_players
            clear_screen()
        

    def get_first_player(self) -> int:
        """"
        "Find the player with the smallest card to start the game."
        Returns:
            int: The index of the player who starts the game.
        """
        first_player_number = 0
        smallest_card = self.players[0].get_minimum_card()
        for i in range(1, self.number_of_players):
            if self.players[i].get_minimum_card() < smallest_card:
                smallest_card = self.players[i].get_minimum_card()
                first_player_number = i
        return first_player_number
    
    def get_previous_cards(self):
        return self.previous_cards