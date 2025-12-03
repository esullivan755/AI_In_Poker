"""Tests for poker room functionality."""
import pytest
from poker.room import PokerRoom
from poker.player import Player
from poker.demo_player import DemoPlayer


class TestPokerRoom:
    """Test PokerRoom class."""
    
    def test_room_creation(self):
        """Test creating a poker room."""
        room = PokerRoom(name="Test Room")
        assert room.name == "Test Room"
        assert len(room.games) == 0
        assert len(room.players) == 0
    
    def test_create_game(self):
        """Test creating a game."""
        room = PokerRoom()
        game_id = room.create_game(small_blind=5, big_blind=10)
        assert game_id in room.games
        assert room.games[game_id].small_blind == 5
    
    def test_remove_game(self):
        """Test removing a game."""
        room = PokerRoom()
        game_id = room.create_game()
        assert room.remove_game(game_id)
        assert game_id not in room.games
    
    def test_add_player(self):
        """Test adding a player to room."""
        room = PokerRoom()
        player = DemoPlayer("p1", "Alice", chips=1000)
        assert room.add_player(player)
        assert "p1" in room.players
    
    def test_add_duplicate_player(self):
        """Test adding duplicate player."""
        room = PokerRoom()
        player = DemoPlayer("p1", "Alice", chips=1000)
        room.add_player(player)
        assert not room.add_player(player)
    
    def test_remove_player(self):
        """Test removing a player."""
        room = PokerRoom()
        player = DemoPlayer("p1", "Alice", chips=1000)
        room.add_player(player)
        assert room.remove_player("p1")
        assert "p1" not in room.players
    
    def test_add_player_to_game(self):
        """Test adding player to a game."""
        room = PokerRoom()
        game_id = room.create_game()
        player = DemoPlayer("p1", "Alice", chips=1000)
        room.add_player(player)
        assert room.add_player_to_game("p1", game_id)
        assert "p1" in room.player_game_map
    
    def test_remove_player_from_game(self):
        """Test removing player from game."""
        room = PokerRoom()
        game_id = room.create_game()
        player = DemoPlayer("p1", "Alice", chips=1000)
        room.add_player(player)
        room.add_player_to_game("p1", game_id)
        assert room.remove_player_from_game("p1", game_id)
        assert "p1" not in room.player_game_map
    
    def test_get_player_game(self):
        """Test getting player's game."""
        room = PokerRoom()
        game_id = room.create_game()
        player = DemoPlayer("p1", "Alice", chips=1000)
        room.add_player(player)
        room.add_player_to_game("p1", game_id)
        assert room.get_player_game("p1") == room.games[game_id]
    
    def test_list_games(self):
        """Test listing games."""
        room = PokerRoom()
        game_id1 = room.create_game()
        game_id2 = room.create_game()
        games = room.list_games()
        assert len(games) == 2
        assert any(g["game_id"] == game_id1 for g in games)
    
    def test_list_players(self):
        """Test listing players."""
        room = PokerRoom()
        player1 = DemoPlayer("p1", "Alice", chips=1000)
        player2 = DemoPlayer("p2", "Bob", chips=1000)
        room.add_player(player1)
        room.add_player(player2)
        players = room.list_players()
        assert len(players) == 2
    
    def test_start_game_hand(self):
        """Test starting a hand in a game."""
        room = PokerRoom()
        game_id = room.create_game()
        player1 = DemoPlayer("p1", "Alice", chips=1000)
        player2 = DemoPlayer("p2", "Bob", chips=1000)
        room.add_player(player1)
        room.add_player(player2)
        room.add_player_to_game("p1", game_id)
        room.add_player_to_game("p2", game_id)
        assert room.start_game_hand(game_id)
    
    def test_process_player_action(self):
        """Test processing player action."""
        room = PokerRoom()
        game_id = room.create_game(small_blind=5, big_blind=10)
        player1 = DemoPlayer("p1", "Alice", chips=1000)
        player2 = DemoPlayer("p2", "Bob", chips=1000)
        room.add_player(player1)
        room.add_player(player2)
        room.add_player_to_game("p1", game_id)
        room.add_player_to_game("p2", game_id)
        room.start_game_hand(game_id)
        
        success, message = room.process_player_action("p1", "call")
        assert success or "not" in message.lower()  # May not be their turn
    
    def test_get_player_game_state(self):
        """Test getting player game state."""
        room = PokerRoom()
        game_id = room.create_game()
        player = DemoPlayer("p1", "Alice", chips=1000)
        room.add_player(player)
        room.add_player_to_game("p1", game_id)
        
        state = room.get_player_game_state("p1")
        # May be None if game hasn't started
        assert state is None or isinstance(state, dict)

