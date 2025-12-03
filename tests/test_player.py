"""Tests for player functionality."""
import pytest
from poker.player import Player, PlayerAction
from poker.cards import Card, Rank, Suit


class TestPlayer:
    """Test Player class."""
    
    def test_player_creation(self):
        """Test creating a player."""
        player = Player("p1", "Alice", chips=1000)
        assert player.player_id == "p1"
        assert player.name == "Alice"
        assert player.chips == 1000
        assert player.is_active
    
    def test_add_chips(self):
        """Test adding chips."""
        player = Player("p1", "Alice", chips=1000)
        player.add_chips(500)
        assert player.chips == 1500
    
    def test_remove_chips(self):
        """Test removing chips."""
        player = Player("p1", "Alice", chips=1000)
        removed = player.remove_chips(300)
        assert removed == 300
        assert player.chips == 700
    
    def test_remove_chips_insufficient(self):
        """Test removing more chips than available."""
        player = Player("p1", "Alice", chips=1000)
        removed = player.remove_chips(1500)
        assert removed == 1000
        assert player.chips == 0
        assert player.is_all_in
    
    def test_bet(self):
        """Test placing a bet."""
        player = Player("p1", "Alice", chips=1000)
        bet_amount = player.bet(100)
        assert bet_amount == 100
        assert player.chips == 900
        assert player.current_bet == 100
        assert player.total_bet_this_round == 100
    
    def test_bet_all_in(self):
        """Test going all-in."""
        player = Player("p1", "Alice", chips=1000)
        bet_amount = player.bet(1500)
        assert bet_amount == 1000
        assert player.chips == 0
        assert player.is_all_in
    
    def test_fold(self):
        """Test folding."""
        player = Player("p1", "Alice", chips=1000)
        player.fold()
        assert not player.is_active
    
    def test_reset_for_new_hand(self):
        """Test resetting for new hand."""
        player = Player("p1", "Alice", chips=1000)
        player.hand = [Card(Rank.ACE, Suit.SPADES)]
        player.bet(100)
        player.fold()
        
        player.reset_for_new_hand()
        assert player.hand == []
        assert player.current_bet == 0
        assert player.total_bet_this_round == 0
        assert player.is_active
        assert not player.is_all_in
    
    def test_reset_for_new_round(self):
        """Test resetting for new betting round."""
        player = Player("p1", "Alice", chips=1000)
        player.bet(100)
        player.reset_for_new_round()
        assert player.current_bet == 0
        assert player.total_bet_this_round == 0
    
    def test_can_act(self):
        """Test can_act method."""
        player = Player("p1", "Alice", chips=1000)
        assert player.can_act()
        
        player.fold()
        assert not player.can_act()
        
        player = Player("p2", "Bob", chips=1000)
        player.bet(1000)  # All in
        assert not player.can_act()
        
        player = Player("p3", "Charlie", chips=0)
        assert not player.can_act()
    
    def test_get_action_not_implemented(self):
        """Test that base player raises NotImplementedError."""
        player = Player("p1", "Alice", chips=1000)
        with pytest.raises(NotImplementedError):
            player.get_action({})

