from typing import (
    List,
)
from .card import (Card, HandType)
from .helper import (
    classify_hand,
    get_card_from_str,
    is_suitable_for_previous_hand,
)

class Player:
    def __init__(self, name, cards: List[Card] = None):
        self.name = name
        self.cards = cards
        if self.cards:
            self.cards = cards
            self.cards.sort()


    def print_cards(self):
        for card in self.cards:
            print(card, end=" ")
        print()
    
    def get_str_cards(self) -> str:
        str_cards = ""
        for card in self.cards:
            str_cards += f"{card} "
        str_cards += "\n"
        return str_cards

    def promt_cards(self, previous_cards: list[Card] = None) -> list[Card]:
        print(f"{self.name}, it's your turn to play.")
        if previous_cards != None:
            previous_hand_type = classify_hand(previous_cards)
            print(f"Previous cards played {previous_hand_type} hand: {previous_cards}")
        else:
            print(f"A new turn cycle has started, {self.name} can play any cards.")
        print("Your cards: ", end="")
        self.print_cards()
        while True:
            str_cards = input(f"{self.name}, please enter the card you want to play (e.g., 1h for Ace of Hearts): ")
            if str_cards == "pass":
                if previous_cards == None:
                    print("You cannot pass in the first turn of a cycle.")
                    continue
                return previous_cards
            if not self.check_cards(str_cards):
                print("Invalid card format. Please try again.")
                continue
            cards = [get_card_from_str(card) for card in str_cards.split()]
            is_valid = True
            for card in cards:
                if not self.is_card_in_hand(card):
                    print(f"You don't have card {card} in your hand. Please try again.")
                    is_valid = False
                    break
            if not is_valid:
                continue
            played_type = classify_hand(cards)
            if played_type == HandType.INVALID:
                print("Invalid hand. Please try again.")
                continue
            if not is_suitable_for_previous_hand(cards, previous_cards):
                print(f"Invalid hand. You cannot play {played_type} {cards} after {previous_hand_type} {previous_cards}. Please try again.")
                continue
            break
            # check if hand is sutiable for the previous hand
        for card in cards:
            self.remove_card(card)
        return cards

    def check_cards(self, card: str) -> bool:
        cards = card.split()
        if len(cards) != len(set(cards)):
            return False
        for card in cards:
            if not self.check_card_format(card):
                return False
        return True
            
    def check_card_format(self, card: str) -> bool:
        card = [card[:-1], card[-1]]
        if len(card[0]) < 1 or len(card[1]) > 2:
            return False
        if not card[0].isdigit() or not card[1].isalpha():
            return False
        card[0] = int(card[0])
        if card[0] < 1 or card[0] > 13:
            return False
        for suit in ["h", "d", "c", "s"]:
            if card[1] == suit:
                break
        else:
            return False
        return True
    
    def remove_card(self, card: Card):
        for c in self.cards:
            if c == card:
                self.cards.remove(c)
                return
        print("Card not found in player's hand.")

    def get_minimum_card(self) -> Card:
        return self.cards[0]
    
    def is_winner(self) -> bool:
        return len(self.cards) == 0
    
    def is_card_in_hand(self, card: Card) -> bool:
        for c in self.cards:
            if c == card:
                return True
        return False
    
