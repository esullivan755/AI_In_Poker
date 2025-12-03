"""Simple demo player for testing."""
import random
from poker.player import Player, PlayerAction


class DemoPlayer(Player):
    """A simple demo player that makes random decisions."""
    
    def get_action(self, game_state: dict) -> tuple:
        """Make a random decision."""
        current_bet_to_call = game_state.get("current_bet_to_call", 0)
        min_raise = game_state.get("min_raise", 0)
        chips = game_state.get("chips", 0)
        
        # If nothing to call, check or bet
        if current_bet_to_call == 0:
            if random.random() < 0.3 and chips >= min_raise:
                bet_amount = random.randint(min_raise, min(chips, min_raise * 3))
                return PlayerAction.BET, bet_amount
            else:
                return PlayerAction.CHECK, 0
        
        # Something to call
        action_roll = random.random()
        
        if action_roll < 0.2:
            return PlayerAction.FOLD, 0
        elif action_roll < 0.6:
            return PlayerAction.CALL, 0
        elif action_roll < 0.8 and chips >= current_bet_to_call + min_raise:
            raise_amount = random.randint(min_raise, min(chips - current_bet_to_call, min_raise * 3))
            return PlayerAction.RAISE, raise_amount
        else:
            return PlayerAction.CALL, 0

