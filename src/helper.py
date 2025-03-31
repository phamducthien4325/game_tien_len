from .card import *
import random
import os

def create_deck() -> list[Card]:
    deck = []
    for suit in Suit:
        for number in range(1, 14):
            deck.append(Card(suit, number))
    return deck

def generate_cards_for_player(num_players: int = 4) -> tuple[list[Card]]:
    cards = create_deck()
    random.shuffle(cards)
    decks = []
    for i in range(num_players):
        decks.append(cards[i * 13:(i + 1) * 13])
    return tuple(decks)

def get_card_from_str(card: str) -> Card:
        card = [card[:-1], card[-1]]
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
        card[1] = {'h': Suit.HEARTS, 'd': Suit.DIAMONDS, 'c': Suit.CLUBS, 's': Suit.SPADES}[card[1]]
        input_card = Card(Suit(card[1]), card[0])
        return input_card

def clear_screen():
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def classify_hand(hand: list[Card]):
    cards = sorted(hand)
    counter = {}
    for card in cards:
        rank = card.get_value()
        if rank in counter:
            counter[rank] += 1
        else:
            counter[rank] = 1
    values = list(counter.keys()) 
    counts = list(counter.values()) 
    if len(cards) == 1:
        return HandType.SINGLE

    if len(cards) == 2 and counts == [2]:
        return HandType.DOUBLE
    
    if len(cards) == 3 and counts == [3]:
        return HandType.TRIPLE
    
    if len(cards) >= 3 and all(values[i] + 1 == values[i + 1] for i in range(len(values) - 1)) and 15 not in values and len(cards) == len(values):
        return HandType.STRAIGHT
    
    if len(cards) == 6 and counts == [2, 2, 2] and all(values[i] + 1 == values[i + 1] for i in range(len(values) - 1)):
        return HandType.THREE_PAIR_SEQUENCE

    if len(cards) == 4 and counts == [4]:
        return HandType.FOUR_OF_A_KIND
    
    if len(cards) == 8 and counts == [2, 2, 2, 2] and all(values[i] + 1 == values[i + 1] for i in range(len(values) - 1)):
        return HandType.FOUR_PAIR_SEQUENCE

    return HandType.INVALID

def is_suitable_for_previous_hand(played_cards: list[Card], previous_cards: list[Card]) -> bool:
    played_cards = sorted(played_cards)
    played_type = classify_hand(played_cards)
    if played_type == HandType.INVALID:
        return False
    if previous_cards is None:
        return True
    previous_cards = sorted(previous_cards)
    previous_type = classify_hand(previous_cards)
    
    match previous_type:
        case HandType.SINGLE:
            if previous_cards[0].rank == 2 and (played_type == HandType.FOUR_OF_A_KIND or played_type == HandType.THREE_PAIR_SEQUENCE or played_type == HandType.FOUR_PAIR_SEQUENCE):
                return True
            return played_type == HandType.SINGLE and (previous_cards[0] < played_cards[0])
        case HandType.DOUBLE:
            if previous_type == HandType.FOUR_PAIR_SEQUENCE:
                return True
            return played_type == HandType.DOUBLE and previous_cards[-1] < played_cards[-1]
        case HandType.TRIPLE:
            return played_type == HandType.TRIPLE and previous_cards[-1] < played_cards[-1]
        case HandType.STRAIGHT:
            return played_type == HandType.STRAIGHT and len(played_cards) == len(previous_cards) and previous_cards[-1] < played_cards[-1]
        case HandType.THREE_PAIR_SEQUENCE:
            if previous_type == HandType.FOUR_PAIR_SEQUENCE:
                return True
            return played_type == HandType.THREE_PAIR_SEQUENCE and previous_cards[-1] < played_cards[-1]
        case HandType.FOUR_OF_A_KIND:
            if previous_type == HandType.FOUR_PAIR_SEQUENCE:
                return True
            return played_type == HandType.FOUR_OF_A_KIND and previous_cards[-1] < played_cards[-1]
        case HandType.FOUR_PAIR_SEQUENCE:
            return played_type == HandType.FOUR_PAIR_SEQUENCE and previous_cards[-1] < played_cards[-1]
        case HandType.INVALID:
            print("how is previous hand invalid???")
            return False
    return False

def check_cards(card: str) -> bool:
    cards = card.split()
    if len(cards) != len(set(cards)):
        return False
    for card in cards:
        if not check_card_format(card):
            return False
    return True
        
def check_card_format(card: str) -> bool:
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