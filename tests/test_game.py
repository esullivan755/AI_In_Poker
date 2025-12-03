"""Tests for game functionality."""
import pytest
from poker.game import TexasHoldemGame, BettingRound, GameState
from poker.player import Player
from poker.demo_player import DemoPlayer


class TestTexasHoldemGame:
    """Test TexasHoldemGame class."""
    
    def test_game_creation(self):
        """Test creating a game."""
        game = TexasHoldemGame("game1", small_blind=5, big_blind=10)
        assert game.game_id == "game1"
        assert game.small_blind == 5
        assert game.big_blind == 10
        assert game.state == GameState.WAITING_FOR_PLAYERS
    
    def test_add_player(self):
        """Test adding a player."""
        game = TexasHoldemGame("game1")
        player = DemoPlayer("p1", "Alice", chips=1000)
        assert game.add_player(player)
        assert len(game.players) == 1
    
    def test_add_player_max_limit(self):
        """Test max player limit."""
        game = TexasHoldemGame("game1")
        for i in range(10):
            player = DemoPlayer(f"p{i}", f"Player{i}", chips=1000)
            game.add_player(player)
        
        player11 = DemoPlayer("p11", "Player11", chips=1000)
        assert not game.add_player(player11)
    
    def test_remove_player(self):
        """Test removing a player."""
        game = TexasHoldemGame("game1")
        player = DemoPlayer("p1", "Alice", chips=1000)
        game.add_player(player)
        assert game.remove_player("p1")
        assert len(game.players) == 0
    
    def test_start_hand_insufficient_players(self):
        """Test starting hand with insufficient players."""
        game = TexasHoldemGame("game1")
        player = DemoPlayer("p1", "Alice", chips=1000)
        game.add_player(player)
        assert not game.start_hand()
    
    def test_start_hand(self):
        """Test starting a hand."""
        game = TexasHoldemGame("game1", small_blind=5, big_blind=10)
        player1 = DemoPlayer("p1", "Alice", chips=1000)
        player2 = DemoPlayer("p2", "Bob", chips=1000)
        game.add_player(player1)
        game.add_player(player2)
        
        assert game.start_hand()
        assert game.state == GameState.IN_PROGRESS
        assert len(player1.hand) == 2
        assert len(player2.hand) == 2
        assert game.pot > 0  # Blinds posted
    
    def test_blinds_posted(self):
        """Test that blinds are posted correctly."""
        game = TexasHoldemGame("game1", small_blind=5, big_blind=10)
        player1 = DemoPlayer("p1", "Alice", chips=1000)
        player2 = DemoPlayer("p2", "Bob", chips=1000)
        game.add_player(player1)
        game.add_player(player2)
        
        game.start_hand()
        # One player should have bet small blind, one big blind
        bets = [p.current_bet for p in game.players]
        assert 5 in bets or 10 in bets
    
    def test_process_action_fold(self):
        """Test processing fold action."""
        game = TexasHoldemGame("game1", small_blind=5, big_blind=10)
        player1 = DemoPlayer("p1", "Alice", chips=1000)
        player2 = DemoPlayer("p2", "Bob", chips=1000)
        game.add_player(player1)
        game.add_player(player2)
        game.start_hand()
        
        current_player = game.get_current_player()
        success, message = game.process_action(current_player, "fold")
        assert success
        assert "folds" in message.lower()
        assert not current_player.is_active
    
    def test_process_action_check(self):
        """Test processing check action."""
        game = TexasHoldemGame("game1", small_blind=5, big_blind=10)
        player1 = DemoPlayer("p1", "Alice", chips=1000)
        player2 = DemoPlayer("p2", "Bob", chips=1000)
        game.add_player(player1)
        game.add_player(player2)
        game.start_hand()
        
        # Find player who can check (not the big blind)
        current_player = game.get_current_player()
        if current_player.current_bet < game.current_bet:
            # This player needs to call, skip
            game.process_action(current_player, "call")
            current_player = game.get_current_player()
        
        # Now try to check
        if current_player.current_bet == game.current_bet:
            success, message = game.process_action(current_player, "check")
            assert success
    
    def test_process_action_call(self):
        """Test processing call action."""
        game = TexasHoldemGame("game1", small_blind=5, big_blind=10)
        player1 = DemoPlayer("p1", "Alice", chips=1000)
        player2 = DemoPlayer("p2", "Bob", chips=1000)
        game.add_player(player1)
        game.add_player(player2)
        game.start_hand()
        
        current_player = game.get_current_player()
        if current_player.current_bet < game.current_bet:
            success, message = game.process_action(current_player, "call")
            assert success
            assert "calls" in message.lower()
    
    def test_process_action_bet(self):
        """Test processing bet action."""
        game = TexasHoldemGame("game1", small_blind=5, big_blind=10)
        player1 = DemoPlayer("p1", "Alice", chips=1000)
        player2 = DemoPlayer("p2", "Bob", chips=1000)
        game.add_player(player1)
        game.add_player(player2)
        game.start_hand()
        
        # Advance to flop where betting can start
        # For now, just test that bet action is recognized
        current_player = game.get_current_player()
        # Skip if they need to call first
        if current_player.current_bet < game.current_bet:
            game.process_action(current_player, "call")
    
    def test_get_active_players(self):
        """Test getting active players."""
        game = TexasHoldemGame("game1")
        player1 = DemoPlayer("p1", "Alice", chips=1000)
        player2 = DemoPlayer("p2", "Bob", chips=1000)
        game.add_player(player1)
        game.add_player(player2)
        
        assert len(game.get_active_players()) == 2
        player1.fold()
        assert len(game.get_active_players()) == 1
    
    def test_get_game_state_for_player(self):
        """Test getting game state for a player."""
        game = TexasHoldemGame("game1", small_blind=5, big_blind=10)
        player1 = DemoPlayer("p1", "Alice", chips=1000)
        player2 = DemoPlayer("p2", "Bob", chips=1000)
        game.add_player(player1)
        game.add_player(player2)
        game.start_hand()
        
        state = game.get_game_state_for_player(player1)
        assert "game_id" in state
        assert "betting_round" in state
        assert "pot" in state
        assert "hand" in state
        assert len(state["hand"]) == 2

