"""Card and Deck classes for poker game."""
from enum import Enum
from typing import List, Tuple


class Suit(Enum):
    """Card suits."""
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"
    SPADES = "♠"


class Rank(Enum):
    """Card ranks."""
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14


class Card:
    """Represents a playing card."""
    
    def __init__(self, rank: Rank, suit: Suit):
        self.rank = rank
        self.suit = suit
    
    def __repr__(self):
        rank_str = {
            Rank.ACE: "A",
            Rank.KING: "K",
            Rank.QUEEN: "Q",
            Rank.JACK: "J",
            Rank.TEN: "10",
            Rank.NINE: "9",
            Rank.EIGHT: "8",
            Rank.SEVEN: "7",
            Rank.SIX: "6",
            Rank.FIVE: "5",
            Rank.FOUR: "4",
            Rank.THREE: "3",
            Rank.TWO: "2",
        }[self.rank]
        return f"{rank_str}{self.suit.value}"
    
    def __eq__(self, other):
        return isinstance(other, Card) and self.rank == other.rank and self.suit == other.suit
    
    def __hash__(self):
        return hash((self.rank, self.suit))
    
    def __lt__(self, other):
        if not isinstance(other, Card):
            return NotImplemented
        return self.rank.value < other.rank.value
    
    def __le__(self, other):
        if not isinstance(other, Card):
            return NotImplemented
        return self.rank.value <= other.rank.value


class Deck:
    """Standard 52-card deck."""
    
    def __init__(self):
        self.cards: List[Card] = []
        self.reset()
    
    def reset(self):
        """Reset deck to full 52 cards."""
        self.cards = [Card(rank, suit) for suit in Suit for rank in Rank]
    
    def shuffle(self):
        """Shuffle the deck."""
        import random
        random.shuffle(self.cards)
    
    def deal(self, num_cards: int = 1) -> List[Card]:
        """Deal cards from the deck."""
        if len(self.cards) < num_cards:
            raise ValueError(f"Not enough cards in deck. Requested {num_cards}, have {len(self.cards)}")
        dealt = self.cards[:num_cards]
        self.cards = self.cards[num_cards:]
        return dealt
    
    def __len__(self):
        return len(self.cards)

