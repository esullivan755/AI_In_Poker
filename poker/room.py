"""Poker room management system."""
from typing import Dict, List, Optional
from uuid import uuid4
from poker.game import TexasHoldemGame, GameState
from poker.player import Player


class PokerRoom:
    """Manages poker games and players."""
    
    def __init__(self, room_id: Optional[str] = None, name: str = "Main Room"):
        self.room_id = room_id or str(uuid4())
        self.name = name
        self.games: Dict[str, TexasHoldemGame] = {}
        self.players: Dict[str, Player] = {}  # All players in room
        self.player_game_map: Dict[str, str] = {}  # player_id -> game_id
    
    def create_game(self, game_id: Optional[str] = None, small_blind: int = 5, big_blind: int = 10) -> str:
        """Create a new poker game."""
        game_id = game_id or str(uuid4())
        if game_id in self.games:
            raise ValueError(f"Game {game_id} already exists")
        
        game = TexasHoldemGame(game_id, small_blind, big_blind)
        self.games[game_id] = game
        return game_id
    
    def remove_game(self, game_id: str) -> bool:
        """Remove a game from the room."""
        if game_id not in self.games:
            return False
        
        # Remove players from game
        game = self.games[game_id]
        for player in game.players[:]:
            self.remove_player_from_game(player.player_id, game_id)
        
        del self.games[game_id]
        return True
    
    def add_player(self, player: Player) -> bool:
        """Add a player to the room."""
        if player.player_id in self.players:
            return False
        self.players[player.player_id] = player
        return True
    
    def remove_player(self, player_id: str) -> bool:
        """Remove a player from the room."""
        if player_id not in self.players:
            return False
        
        # Remove from any games
        if player_id in self.player_game_map:
            game_id = self.player_game_map[player_id]
            self.remove_player_from_game(player_id, game_id)
        
        del self.players[player_id]
        return True
    
    def add_player_to_game(self, player_id: str, game_id: str) -> bool:
        """Add a player to a specific game."""
        if player_id not in self.players:
            return False
        if game_id not in self.games:
            return False
        
        player = self.players[player_id]
        game = self.games[game_id]
        
        if game.add_player(player):
            self.player_game_map[player_id] = game_id
            return True
        return False
    
    def remove_player_from_game(self, player_id: str, game_id: str) -> bool:
        """Remove a player from a specific game."""
        if game_id not in self.games:
            return False
        
        game = self.games[game_id]
        if game.remove_player(player_id):
            if player_id in self.player_game_map:
                del self.player_game_map[player_id]
            return True
        return False
    
    def get_player_game(self, player_id: str) -> Optional[TexasHoldemGame]:
        """Get the game a player is currently in."""
        if player_id not in self.player_game_map:
            return None
        game_id = self.player_game_map[player_id]
        return self.games.get(game_id)
    
    def get_game(self, game_id: str) -> Optional[TexasHoldemGame]:
        """Get a game by ID."""
        return self.games.get(game_id)
    
    def list_games(self) -> List[Dict]:
        """List all games in the room."""
        return [
            {
                "game_id": game_id,
                "state": game.state.value,
                "num_players": len(game.players),
                "pot": game.pot,
                "betting_round": game.betting_round.value if game.betting_round else None,
            }
            for game_id, game in self.games.items()
        ]
    
    def list_players(self) -> List[Dict]:
        """List all players in the room."""
        return [
            {
                "player_id": player_id,
                "name": player.name,
                "chips": player.chips,
                "game_id": self.player_game_map.get(player_id),
            }
            for player_id, player in self.players.items()
        ]
    
    def start_game_hand(self, game_id: str) -> bool:
        """Start a new hand in a game."""
        if game_id not in self.games:
            return False
        return self.games[game_id].start_hand()
    
    def process_player_action(self, player_id: str, action: str, amount: int = 0) -> tuple:
        """
        Process a player action in their current game.
        Returns: (success, message)
        """
        game = self.get_player_game(player_id)
        if not game:
            return False, "Player is not in a game"
        
        player = self.players.get(player_id)
        if not player:
            return False, "Player not found"
        
        return game.process_action(player, action, amount)
    
    def get_player_game_state(self, player_id: str) -> Optional[Dict]:
        """Get game state for a specific player."""
        game = self.get_player_game(player_id)
        if not game:
            return None
        
        player = self.players.get(player_id)
        if not player:
            return None
        
        return game.get_game_state_for_player(player)

