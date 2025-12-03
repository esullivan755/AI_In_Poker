"""Tests for hand evaluator."""
import pytest
from poker.cards import Card, Suit, Rank
from poker.hand_evaluator import HandEvaluator, HandRank


class TestHandEvaluator:
    """Test HandEvaluator class."""
    
    def test_royal_flush(self):
        """Test royal flush detection."""
        cards = [
            Card(Rank.ACE, Suit.SPADES),
            Card(Rank.KING, Suit.SPADES),
            Card(Rank.QUEEN, Suit.SPADES),
            Card(Rank.JACK, Suit.SPADES),
            Card(Rank.TEN, Suit.SPADES),
        ]
        rank, tiebreakers = HandEvaluator.evaluate_hand(cards)
        assert rank == HandRank.ROYAL_FLUSH
    
    def test_straight_flush(self):
        """Test straight flush detection."""
        cards = [
            Card(Rank.NINE, Suit.HEARTS),
            Card(Rank.EIGHT, Suit.HEARTS),
            Card(Rank.SEVEN, Suit.HEARTS),
            Card(Rank.SIX, Suit.HEARTS),
            Card(Rank.FIVE, Suit.HEARTS),
        ]
        rank, tiebreakers = HandEvaluator.evaluate_hand(cards)
        assert rank == HandRank.STRAIGHT_FLUSH
        assert tiebreakers[0] == 9
    
    def test_four_of_a_kind(self):
        """Test four of a kind detection."""
        cards = [
            Card(Rank.ACE, Suit.SPADES),
            Card(Rank.ACE, Suit.HEARTS),
            Card(Rank.ACE, Suit.DIAMONDS),
            Card(Rank.ACE, Suit.CLUBS),
            Card(Rank.KING, Suit.SPADES),
        ]
        rank, tiebreakers = HandEvaluator.evaluate_hand(cards)
        assert rank == HandRank.FOUR_OF_A_KIND
        assert tiebreakers[0] == Rank.ACE.value
    
    def test_full_house(self):
        """Test full house detection."""
        cards = [
            Card(Rank.KING, Suit.SPADES),
            Card(Rank.KING, Suit.HEARTS),
            Card(Rank.KING, Suit.DIAMONDS),
            Card(Rank.QUEEN, Suit.CLUBS),
            Card(Rank.QUEEN, Suit.SPADES),
        ]
        rank, tiebreakers = HandEvaluator.evaluate_hand(cards)
        assert rank == HandRank.FULL_HOUSE
        assert tiebreakers[0] == Rank.KING.value
        assert tiebreakers[1] == Rank.QUEEN.value
    
    def test_flush(self):
        """Test flush detection."""
        cards = [
            Card(Rank.ACE, Suit.HEARTS),
            Card(Rank.KING, Suit.HEARTS),
            Card(Rank.QUEEN, Suit.HEARTS),
            Card(Rank.JACK, Suit.HEARTS),
            Card(Rank.NINE, Suit.HEARTS),
        ]
        rank, tiebreakers = HandEvaluator.evaluate_hand(cards)
        assert rank == HandRank.FLUSH
    
    def test_straight(self):
        """Test straight detection."""
        cards = [
            Card(Rank.TEN, Suit.SPADES),
            Card(Rank.NINE, Suit.HEARTS),
            Card(Rank.EIGHT, Suit.DIAMONDS),
            Card(Rank.SEVEN, Suit.CLUBS),
            Card(Rank.SIX, Suit.SPADES),
        ]
        rank, tiebreakers = HandEvaluator.evaluate_hand(cards)
        assert rank == HandRank.STRAIGHT
        assert tiebreakers[0] == 10
    
    def test_straight_wheel(self):
        """Test A-2-3-4-5 straight (wheel)."""
        cards = [
            Card(Rank.ACE, Suit.SPADES),
            Card(Rank.FIVE, Suit.HEARTS),
            Card(Rank.FOUR, Suit.DIAMONDS),
            Card(Rank.THREE, Suit.CLUBS),
            Card(Rank.TWO, Suit.SPADES),
        ]
        rank, tiebreakers = HandEvaluator.evaluate_hand(cards)
        assert rank == HandRank.STRAIGHT
    
    def test_three_of_a_kind(self):
        """Test three of a kind detection."""
        cards = [
            Card(Rank.JACK, Suit.SPADES),
            Card(Rank.JACK, Suit.HEARTS),
            Card(Rank.JACK, Suit.DIAMONDS),
            Card(Rank.KING, Suit.CLUBS),
            Card(Rank.QUEEN, Suit.SPADES),
        ]
        rank, tiebreakers = HandEvaluator.evaluate_hand(cards)
        assert rank == HandRank.THREE_OF_A_KIND
        assert tiebreakers[0] == Rank.JACK.value
    
    def test_two_pair(self):
        """Test two pair detection."""
        cards = [
            Card(Rank.TEN, Suit.SPADES),
            Card(Rank.TEN, Suit.HEARTS),
            Card(Rank.NINE, Suit.DIAMONDS),
            Card(Rank.NINE, Suit.CLUBS),
            Card(Rank.KING, Suit.SPADES),
        ]
        rank, tiebreakers = HandEvaluator.evaluate_hand(cards)
        assert rank == HandRank.TWO_PAIR
        assert tiebreakers[0] == Rank.TEN.value
        assert tiebreakers[1] == Rank.NINE.value
    
    def test_pair(self):
        """Test pair detection."""
        cards = [
            Card(Rank.ACE, Suit.SPADES),
            Card(Rank.ACE, Suit.HEARTS),
            Card(Rank.KING, Suit.DIAMONDS),
            Card(Rank.QUEEN, Suit.CLUBS),
            Card(Rank.JACK, Suit.SPADES),
        ]
        rank, tiebreakers = HandEvaluator.evaluate_hand(cards)
        assert rank == HandRank.PAIR
        assert tiebreakers[0] == Rank.ACE.value
    
    def test_high_card(self):
        """Test high card detection."""
        cards = [
            Card(Rank.ACE, Suit.SPADES),
            Card(Rank.KING, Suit.HEARTS),
            Card(Rank.QUEEN, Suit.DIAMONDS),
            Card(Rank.JACK, Suit.CLUBS),
            Card(Rank.NINE, Suit.SPADES),
        ]
        rank, tiebreakers = HandEvaluator.evaluate_hand(cards)
        assert rank == HandRank.HIGH_CARD
    
    def test_seven_card_evaluation(self):
        """Test evaluating 7 cards (Texas Hold'em)."""
        cards = [
            Card(Rank.ACE, Suit.SPADES),
            Card(Rank.ACE, Suit.HEARTS),
            Card(Rank.KING, Suit.DIAMONDS),
            Card(Rank.QUEEN, Suit.CLUBS),
            Card(Rank.JACK, Suit.SPADES),
            Card(Rank.TEN, Suit.HEARTS),
            Card(Rank.NINE, Suit.DIAMONDS),
        ]
        rank, tiebreakers = HandEvaluator.evaluate_hand(cards)
        # Should pick the best 5-card hand (straight)
        assert rank == HandRank.STRAIGHT
    
    def test_compare_hands(self):
        """Test hand comparison."""
        royal_flush = (HandRank.ROYAL_FLUSH, [14])
        straight_flush = (HandRank.STRAIGHT_FLUSH, [9])
        four_kind = (HandRank.FOUR_OF_A_KIND, [14, 13])
        pair = (HandRank.PAIR, [14, 13, 12, 11])
        
        assert HandEvaluator._compare_hands(royal_flush, straight_flush) > 0
        assert HandEvaluator._compare_hands(straight_flush, four_kind) > 0
        assert HandEvaluator._compare_hands(four_kind, pair) > 0
        assert HandEvaluator._compare_hands(pair, four_kind) < 0
    
    def test_compare_player_hands(self):
        """Test comparing multiple player hands."""
        community = [
            Card(Rank.ACE, Suit.SPADES),
            Card(Rank.KING, Suit.HEARTS),
            Card(Rank.QUEEN, Suit.DIAMONDS),
            Card(Rank.JACK, Suit.CLUBS),
            Card(Rank.TEN, Suit.SPADES),
        ]
        
        # Player 0 has royal flush
        player0_hand = [
            Card(Rank.ACE, Suit.SPADES),
            Card(Rank.KING, Suit.SPADES),
        ]
        
        # Player 1 has straight
        player1_hand = [
            Card(Rank.NINE, Suit.HEARTS),
            Card(Rank.EIGHT, Suit.HEARTS),
        ]
        
        ranked = HandEvaluator.compare_player_hands(
            [player0_hand, player1_hand],
            community
        )
        assert ranked[0] == 0  # Player 0 wins
    
    def test_insufficient_cards(self):
        """Test error with insufficient cards."""
        cards = [Card(Rank.ACE, Suit.SPADES)] * 4
        with pytest.raises(ValueError):
            HandEvaluator.evaluate_hand(cards)

