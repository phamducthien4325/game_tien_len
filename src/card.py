from enum import Enum
from termcolor import colored

class HandType(Enum):
    SINGLE = "single"
    DOUBLE = "double"
    TRIPLE = "triple"
    STRAIGHT = "straight"
    THREE_PAIR_SEQUENCE = "three_pair_sequence"
    FOUR_OF_A_KIND = "four_of_a_kind"
    FOUR_PAIR_SEQUENCE = "four_pair_sequence"
    INVALID = "invalid"
    
    def __str__(self):
        return self.value

class Suit(Enum):
    HEARTS = ("♥", "red")
    DIAMONDS = ("♦", "red")
    CLUBS = ("♣", "blue")
    SPADES = ("♠", "blue")

    def __init__(self, symbol, color):
        self.symbol = symbol
        self.color = color

class Card:
    def __init__(self,
                 suit: Suit,
                 rank: int):
        self.suit = suit
        self.rank = rank

    def get_rank(self):
        if self.rank == 1:
            return "A"
        elif self.rank == 11:
            return "J"
        elif self.rank == 12:
            return "Q"
        elif self.rank == 13:
            return "K"
        else:
            return str(self.rank)

    def __str__(self):
        return colored(f"{self.get_rank()}{self.suit.symbol}", self.suit.color, attrs=["bold"])
    
    def __repr__(self):
        return colored(f"{self.get_rank()}{self.suit.symbol}", self.suit.color, attrs=["bold"])
    
    def __eq__(self, other):
        if isinstance(other, Card):
            return self.rank == other.rank and self.suit == other.suit
        return False
    
    def compareTo(self, other):
        this_rank = self.rank
        other_rank = other.rank
        this_suit = self.suit
        other_suit = other.suit
        this_suit = {Suit.SPADES: 1, Suit.CLUBS: 2, Suit.DIAMONDS: 3, Suit.HEARTS: 4}[this_suit]
        other_suit = {Suit.SPADES: 1, Suit.CLUBS: 2, Suit.DIAMONDS: 3, Suit.HEARTS: 4}[other_suit]
        if this_rank == 1:
            this_rank = 14
        if this_rank == 2:
            this_rank = 15
        if other_rank == 1:
            other_rank = 14
        if other_rank == 2:
            other_rank = 15
        if this_rank == other_rank:
            return this_suit < other_suit
        else:
            return this_rank < other_rank
    
    def __lt__(self, other):
        return self.compareTo(other)

    def __hash__(self):
        return hash((self.suit, self.rank))
    
    def get_value(self):
        if self.rank == 1:
            return 14
        elif self.rank == 2:
            return 15
        return self.rank