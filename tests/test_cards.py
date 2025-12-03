"""Tests for card and deck functionality."""
import pytest
from poker.cards import Card, Deck, Suit, Rank


class TestCard:
    """Test Card class."""
    
    def test_card_creation(self):
        """Test creating a card."""
        card = Card(Rank.ACE, Suit.SPADES)
        assert card.rank == Rank.ACE
        assert card.suit == Suit.SPADES
    
    def test_card_equality(self):
        """Test card equality."""
        card1 = Card(Rank.KING, Suit.HEARTS)
        card2 = Card(Rank.KING, Suit.HEARTS)
        card3 = Card(Rank.QUEEN, Suit.HEARTS)
        
        assert card1 == card2
        assert card1 != card3
    
    def test_card_comparison(self):
        """Test card comparison."""
        card1 = Card(Rank.TWO, Suit.HEARTS)
        card2 = Card(Rank.ACE, Suit.HEARTS)
        
        assert card1 < card2
        assert card2 > card1
        assert card1 <= card2
    
    def test_card_repr(self):
        """Test card string representation."""
        card = Card(Rank.ACE, Suit.SPADES)
        assert "A" in str(card)
        assert "♠" in str(card)


class TestDeck:
    """Test Deck class."""
    
    def test_deck_creation(self):
        """Test creating a deck."""
        deck = Deck()
        assert len(deck) == 52
    
    def test_deck_reset(self):
        """Test resetting a deck."""
        deck = Deck()
        deck.deal(5)
        assert len(deck) == 47
        deck.reset()
        assert len(deck) == 52
    
    def test_deck_deal(self):
        """Test dealing cards."""
        deck = Deck()
        cards = deck.deal(5)
        assert len(cards) == 5
        assert len(deck) == 47
    
    def test_deck_deal_all(self):
        """Test dealing all cards."""
        deck = Deck()
        cards = deck.deal(52)
        assert len(cards) == 52
        assert len(deck) == 0
    
    def test_deck_deal_insufficient(self):
        """Test dealing more cards than available."""
        deck = Deck()
        deck.deal(50)
        with pytest.raises(ValueError):
            deck.deal(5)
    
    def test_deck_shuffle(self):
        """Test shuffling deck."""
        deck1 = Deck()
        deck2 = Deck()
        deck2.shuffle()
        
        # After shuffle, order should likely be different
        # (very small chance they're the same, but unlikely)
        cards1 = [str(c) for c in deck1.cards]
        cards2 = [str(c) for c in deck2.cards]
        
        # At least verify all cards are still present
        assert set(cards1) == set(cards2)
    
    def test_deck_no_duplicates(self):
        """Test that deck has no duplicate cards."""
        deck = Deck()
        cards = deck.cards
        assert len(cards) == len(set(cards))

