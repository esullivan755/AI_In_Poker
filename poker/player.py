"""Player abstraction for poker game."""
from typing import Optional, List
from poker.cards import Card


class PlayerAction:
    """Represents a player action."""
    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    BET = "bet"
    RAISE = "raise"
    ALL_IN = "all_in"


class Player:
    """Base player class that can be extended for LLM players."""
    
    def __init__(self, player_id: str, name: str, chips: int = 1000):
        self.player_id = player_id
        self.name = name
        self.chips = chips
        self.hand: List[Card] = []
        self.current_bet = 0
        self.total_bet_this_round = 0
        self.is_active = True  # Not folded
        self.is_all_in = False
        self.is_sitting_out = False
    
    def add_chips(self, amount: int):
        """Add chips to player's stack."""
        self.chips += amount
    
    def remove_chips(self, amount: int) -> int:
        """Remove chips from player's stack. Returns actual amount removed."""
        actual_amount = min(amount, self.chips)
        self.chips -= actual_amount
        if self.chips == 0:
            self.is_all_in = True
        return actual_amount
    
    def bet(self, amount: int) -> int:
        """Place a bet. Returns actual amount bet."""
        if amount >= self.chips:
            amount = self.chips
            self.is_all_in = True
        
        bet_amount = self.remove_chips(amount)
        self.current_bet += bet_amount
        self.total_bet_this_round += bet_amount
        return bet_amount
    
    def fold(self):
        """Fold the hand."""
        self.is_active = False
    
    def reset_for_new_hand(self):
        """Reset player state for a new hand."""
        self.hand = []
        self.current_bet = 0
        self.total_bet_this_round = 0
        self.is_active = True
        self.is_all_in = False
    
    def reset_for_new_round(self):
        """Reset player state for a new betting round."""
        self.current_bet = 0
        self.total_bet_this_round = 0
    
    def can_act(self) -> bool:
        """Check if player can act (not folded, not all-in, has chips)."""
        return self.is_active and not self.is_all_in and self.chips > 0
    
    def get_action(self, game_state: dict) -> tuple:
        """
        Get player action. To be overridden by subclasses.
        Returns: (action_type, amount)
        - action_type: PlayerAction.FOLD, CHECK, CALL, BET, RAISE, ALL_IN
        - amount: bet/raise amount (0 for fold/check/call)
        
        game_state contains:
        - current_bet_to_call: int
        - min_raise: int
        - pot: int
        - community_cards: List[Card]
        - players: List[Player]
        - betting_round: str
        """
        raise NotImplementedError("Subclasses must implement get_action")
    
    def __repr__(self):
        return f"Player({self.name}, chips={self.chips}, active={self.is_active})"

