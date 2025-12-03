"""Texas Hold'em poker game logic."""
from typing import List, Optional, Dict, Tuple
from enum import Enum
from poker.cards import Deck, Card
from poker.hand_evaluator import HandEvaluator
from poker.player import Player, PlayerAction


class BettingRound(Enum):
    """Betting rounds in Texas Hold'em."""
    PRE_FLOP = "pre_flop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"
    SHOWDOWN = "showdown"


class GameState(Enum):
    """Game states."""
    WAITING_FOR_PLAYERS = "waiting_for_players"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


class TexasHoldemGame:
    """Texas Hold'em poker game."""
    
    def __init__(self, game_id: str, small_blind: int = 5, big_blind: int = 10):
        self.game_id = game_id
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.players: List[Player] = []
        self.deck = Deck()
        self.community_cards: List[Card] = []
        self.pot = 0
        self.side_pots: List[Tuple[int, List[Player]]] = []  # (amount, eligible_players)
        self.current_bet = 0
        self.betting_round = BettingRound.PRE_FLOP
        self.dealer_position = 0
        self.small_blind_position = 0
        self.big_blind_position = 0
        self.current_player_index = 0
        self.state = GameState.WAITING_FOR_PLAYERS
        self.winners: List[Tuple[Player, int]] = []  # (player, amount_won)
        self.hand_history: List[Dict] = []
        self.acted_this_round: set = set()  # Track players who have acted this betting round
    
    def add_player(self, player: Player) -> bool:
        """Add a player to the game."""
        if len(self.players) >= 10:  # Max 10 players
            return False
        if any(p.player_id == player.player_id for p in self.players):
            return False
        self.players.append(player)
        return True
    
    def remove_player(self, player_id: str) -> bool:
        """Remove a player from the game."""
        self.players = [p for p in self.players if p.player_id != player_id]
        return True
    
    def start_hand(self) -> bool:
        """Start a new hand."""
        active_players = [p for p in self.players if not p.is_sitting_out and p.chips > 0]
        if len(active_players) < 2:
            return False
        
        # Reset game state
        self.deck.reset()
        self.deck.shuffle()
        self.community_cards = []
        self.pot = 0
        self.side_pots = []
        self.current_bet = 0
        self.betting_round = BettingRound.PRE_FLOP
        self.winners = []
        
        # Reset players
        for player in self.players:
            player.reset_for_new_hand()
        
        # Update dealer positions
        self.dealer_position = (self.dealer_position + 1) % len(active_players)
        self.small_blind_position = (self.dealer_position + 1) % len(active_players)
        self.big_blind_position = (self.dealer_position + 2) % len(active_players)
        
        # Post blinds
        sb_player = active_players[self.small_blind_position]
        bb_player = active_players[self.big_blind_position]
        
        sb_amount = min(self.small_blind, sb_player.chips)
        bb_amount = min(self.big_blind, bb_player.chips)
        
        self.pot += sb_player.bet(sb_amount)
        self.pot += bb_player.bet(bb_amount)
        
        self.current_bet = max(sb_player.current_bet, bb_player.current_bet)
        
        # Deal hole cards
        for player in active_players:
            player.hand = self.deck.deal(2)
        
        # Initialize acted players - blinds have already acted
        self.acted_this_round.clear()
        self.acted_this_round.add(sb_player.player_id)
        self.acted_this_round.add(bb_player.player_id)
        
        # Set current player (first to act after big blind)
        self.current_player_index = (self.big_blind_position + 1) % len(active_players)
        self.state = GameState.IN_PROGRESS
        
        return True
    
    def get_active_players(self) -> List[Player]:
        """Get list of active (not folded) players."""
        return [p for p in self.players if p.is_active and not p.is_sitting_out]
    
    def get_eligible_players(self) -> List[Player]:
        """Get players eligible to act (not folded, not all-in)."""
        return [p for p in self.get_active_players() if p.can_act()]
    
    def process_action(self, player: Player, action: str, amount: int = 0) -> Tuple[bool, str]:
        """
        Process a player action.
        Returns: (success, message)
        """
        if self.state != GameState.IN_PROGRESS:
            return False, "Game is not in progress"
        
        if player not in self.get_eligible_players():
            return False, "Player cannot act"
        
        if player != self.get_current_player():
            return False, "Not player's turn"
        
        amount_to_call = self.current_bet - player.current_bet
        min_raise = self.big_blind
        
        if action == PlayerAction.FOLD:
            player.fold()
            self.acted_this_round.add(player.player_id)  # Folding counts as acting
            self._advance_to_next_player()
            return True, f"{player.name} folds"
        
        elif action == PlayerAction.CHECK:
            if amount_to_call > 0:
                return False, "Cannot check, must call or fold"
            self.acted_this_round.add(player.player_id)
            self._advance_to_next_player()
            return True, f"{player.name} checks"
        
        elif action == PlayerAction.CALL:
            if amount_to_call == 0:
                return False, "Nothing to call, check instead"
            call_amount = min(amount_to_call, player.chips)
            bet_amount = player.bet(call_amount)
            self.pot += bet_amount
            self.acted_this_round.add(player.player_id)
            self._advance_to_next_player()
            return True, f"{player.name} calls {bet_amount}"
        
        elif action == PlayerAction.BET:
            if self.current_bet > 0:
                return False, "Cannot bet, must call or raise"
            if amount < min_raise:
                return False, f"Bet must be at least {min_raise}"
            if amount > player.chips:
                return False, "Insufficient chips"
            
            bet_amount = player.bet(amount)
            self.current_bet = player.current_bet
            self.pot += bet_amount
            self.acted_this_round.clear()  # Reset acted players when someone bets
            self.acted_this_round.add(player.player_id)
            self._advance_to_next_player()
            return True, f"{player.name} bets {bet_amount}"
        
        elif action == PlayerAction.RAISE:
            if amount_to_call == 0:
                return False, "Nothing to raise, bet instead"
            total_raise_amount = amount_to_call + amount
            if amount < min_raise:
                return False, f"Raise must be at least {min_raise} more than current bet"
            if total_raise_amount > player.chips:
                return False, "Insufficient chips"
            
            bet_amount = player.bet(total_raise_amount)
            self.current_bet = player.current_bet
            self.pot += bet_amount
            self.acted_this_round.clear()  # Reset acted players when someone raises
            self.acted_this_round.add(player.player_id)
            self._advance_to_next_player()
            return True, f"{player.name} raises to {self.current_bet}"
        
        elif action == PlayerAction.ALL_IN:
            all_in_amount = player.bet(player.chips)
            if all_in_amount > self.current_bet:
                self.current_bet = player.current_bet
                self.acted_this_round.clear()  # Reset if this is a raise
            self.pot += all_in_amount
            self.acted_this_round.add(player.player_id)
            self._advance_to_next_player()
            return True, f"{player.name} goes all-in with {all_in_amount}"
        
        return False, f"Unknown action: {action}"
    
    def get_current_player(self) -> Optional[Player]:
        """Get the current player whose turn it is."""
        eligible = self.get_eligible_players()
        if not eligible:
            return None
        return eligible[self.current_player_index % len(eligible)]
    
    def _advance_to_next_player(self):
        """Advance to the next player."""
        eligible = self.get_eligible_players()
        if not eligible:
            self._check_betting_round_complete()
            return
        
        self.current_player_index = (self.current_player_index + 1) % len(eligible)
        
        # Check if betting round is complete
        current_player = self.get_current_player()
        if current_player is None:
            self._check_betting_round_complete()
            return
        
        # Check if all players have acted and bets are equalized
        all_bets_equal = all(
            p.current_bet == self.current_bet or p.is_all_in or not p.is_active
            for p in self.get_active_players()
        )
        
        if all_bets_equal and self._all_players_have_acted():
            self._check_betting_round_complete()
    
    def _all_players_have_acted(self) -> bool:
        """Check if all eligible players have acted this round."""
        eligible = self.get_eligible_players()
        if len(eligible) == 0:
            return True
        
        # Check if all eligible players have acted
        eligible_ids = {p.player_id for p in eligible}
        return eligible_ids.issubset(self.acted_this_round)
    
    def _check_betting_round_complete(self):
        """Check if betting round is complete and advance if needed."""
        active_players = self.get_active_players()
        
        # If only one active player, they win
        if len(active_players) == 1:
            winner = active_players[0]
            winner.add_chips(self.pot)
            self.winners = [(winner, self.pot)]
            self.state = GameState.FINISHED
            return
        
        # Advance to next betting round
        if self.betting_round == BettingRound.PRE_FLOP:
            self._deal_flop()
        elif self.betting_round == BettingRound.FLOP:
            self._deal_turn()
        elif self.betting_round == BettingRound.TURN:
            self._deal_river()
        elif self.betting_round == BettingRound.RIVER:
            self._showdown()
    
    def _deal_flop(self):
        """Deal the flop."""
        self.betting_round = BettingRound.FLOP
        self.deck.deal(1)  # Burn card
        self.community_cards = self.deck.deal(3)
        self._reset_betting_round()
    
    def _deal_turn(self):
        """Deal the turn."""
        self.betting_round = BettingRound.TURN
        self.deck.deal(1)  # Burn card
        self.community_cards.append(self.deck.deal(1)[0])
        self._reset_betting_round()
    
    def _deal_river(self):
        """Deal the river."""
        self.betting_round = BettingRound.RIVER
        self.deck.deal(1)  # Burn card
        self.community_cards.append(self.deck.deal(1)[0])
        self._reset_betting_round()
    
    def _reset_betting_round(self):
        """Reset betting round state."""
        self.current_bet = 0
        self.acted_this_round.clear()  # Reset acted players for new betting round
        for player in self.players:
            player.reset_for_new_round()
        
        # Set current player to first active player after dealer
        active = self.get_active_players()
        if active:
            # Find dealer position in active players list
            dealer_player = self.players[self.dealer_position]
            try:
                dealer_idx = active.index(dealer_player)
                self.current_player_index = (dealer_idx + 1) % len(active)
            except ValueError:
                self.current_player_index = 0
    
    def _showdown(self):
        """Determine winners and distribute pot."""
        self.betting_round = BettingRound.SHOWDOWN
        active_players = self.get_active_players()
        
        if len(active_players) == 0:
            return
        
        # Calculate side pots if there are all-in players
        self._calculate_side_pots()
        
        # Evaluate hands
        player_hands = [p.hand for p in active_players]
        ranked_players = HandEvaluator.compare_player_hands(player_hands, self.community_cards)
        
        # Distribute pots
        self.winners = []
        if self.side_pots:
            # Distribute side pots
            for pot_amount, eligible_players in self.side_pots:
                eligible_indices = [i for i, p in enumerate(active_players) if p in eligible_players]
                winners = [ranked_players[i] for i in eligible_indices if ranked_players[i] in eligible_indices]
                if winners:
                    winner_idx = winners[0]
                    per_player = pot_amount // len([w for w in winners if w == winners[0]])
                    active_players[winner_idx].add_chips(per_player)
                    self.winners.append((active_players[winner_idx], per_player))
        else:
            # Single pot
            winner_idx = ranked_players[0]
            active_players[winner_idx].add_chips(self.pot)
            self.winners = [(active_players[winner_idx], self.pot)]
        
        self.state = GameState.FINISHED
    
    def _calculate_side_pots(self):
        """Calculate side pots for all-in players."""
        active_players = self.get_active_players()
        if not active_players:
            return
        
        # Get all unique bet amounts
        bet_amounts = sorted(set(p.total_bet_this_round for p in active_players), reverse=True)
        
        self.side_pots = []
        remaining_pot = self.pot
        
        for i, bet_amount in enumerate(bet_amounts):
            if remaining_pot <= 0:
                break
            
            # Players eligible for this side pot
            eligible = [p for p in active_players if p.total_bet_this_round >= bet_amount]
            
            # Calculate pot contribution
            if i == 0:
                pot_contribution = bet_amount * len(eligible)
            else:
                prev_bet = bet_amounts[i-1]
                pot_contribution = (bet_amount - prev_bet) * len(eligible)
            
            if pot_contribution > 0:
                self.side_pots.append((pot_contribution, eligible))
                remaining_pot -= pot_contribution
    
    def get_game_state_for_player(self, player: Player) -> Dict:
        """Get game state information for a specific player."""
        return {
            "game_id": self.game_id,
            "betting_round": self.betting_round.value,
            "pot": self.pot,
            "current_bet": self.current_bet,
            "current_bet_to_call": self.current_bet - player.current_bet,
            "min_raise": self.big_blind,
            "community_cards": self.community_cards,
            "hand": player.hand,
            "chips": player.chips,
            "player_current_bet": player.current_bet,
            "players": [
                {
                    "name": p.name,
                    "chips": p.chips,
                    "current_bet": p.current_bet,
                    "is_active": p.is_active,
                    "is_all_in": p.is_all_in,
                }
                for p in self.players
            ],
            "is_your_turn": self.get_current_player() == player,
        }

