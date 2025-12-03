"""Hand evaluation logic for poker."""
from enum import Enum
from typing import List, Tuple, Optional
from collections import Counter
from poker.cards import Card, Rank


class HandRank(Enum):
    """Poker hand rankings."""
    HIGH_CARD = 1
    PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10


class HandEvaluator:
    """Evaluates poker hands."""
    
    @staticmethod
    def evaluate_hand(cards: List[Card]) -> Tuple[HandRank, List[int]]:
        """
        Evaluate a poker hand (5-7 cards).
        Returns (hand_rank, tiebreaker_values).
        """
        if len(cards) < 5:
            raise ValueError("Need at least 5 cards to evaluate a hand")
        
        # Get all possible 5-card combinations
        best_hand = None
        best_rank = None
        best_tiebreakers = None
        
        from itertools import combinations
        for combo in combinations(cards, 5):
            rank, tiebreakers = HandEvaluator._evaluate_five_cards(list(combo))
            if best_hand is None or HandEvaluator._compare_hands(
                (rank, tiebreakers), (best_rank, best_tiebreakers)
            ) > 0:
                best_hand = combo
                best_rank = rank
                best_tiebreakers = tiebreakers
        
        return best_rank, best_tiebreakers
    
    @staticmethod
    def _evaluate_five_cards(cards: List[Card]) -> Tuple[HandRank, List[int]]:
        """Evaluate exactly 5 cards."""
        ranks = [card.rank.value for card in cards]
        suits = [card.suit for card in cards]
        rank_counts = Counter(ranks)
        suit_counts = Counter(suits)
        
        # Check for flush
        is_flush = len(suit_counts) == 1
        
        # Check for straight
        sorted_ranks = sorted(set(ranks))
        is_straight = False
        if len(sorted_ranks) == 5:
            if sorted_ranks[-1] - sorted_ranks[0] == 4:
                is_straight = True
            # Check for A-2-3-4-5 straight (wheel)
            elif sorted_ranks == [2, 3, 4, 5, 14]:
                is_straight = True
                sorted_ranks = [1, 2, 3, 4, 5]  # Ace low
        
        # Royal flush
        if is_flush and is_straight and sorted_ranks[-1] == 14 and sorted_ranks[0] == 10:
            return HandRank.ROYAL_FLUSH, [14]
        
        # Straight flush
        if is_flush and is_straight:
            return HandRank.STRAIGHT_FLUSH, [sorted_ranks[-1]]
        
        # Four of a kind
        if 4 in rank_counts.values():
            four_kind = [r for r, count in rank_counts.items() if count == 4][0]
            kicker = [r for r, count in rank_counts.items() if count == 1][0]
            return HandRank.FOUR_OF_A_KIND, [four_kind, kicker]
        
        # Full house
        if 3 in rank_counts.values() and 2 in rank_counts.values():
            three_kind = [r for r, count in rank_counts.items() if count == 3][0]
            pair = [r for r, count in rank_counts.items() if count == 2][0]
            return HandRank.FULL_HOUSE, [three_kind, pair]
        
        # Flush
        if is_flush:
            return HandRank.FLUSH, sorted(ranks, reverse=True)
        
        # Straight
        if is_straight:
            return HandRank.STRAIGHT, [sorted_ranks[-1]]
        
        # Three of a kind
        if 3 in rank_counts.values():
            three_kind = [r for r, count in rank_counts.items() if count == 3][0]
            kickers = sorted([r for r, count in rank_counts.items() if count == 1], reverse=True)
            return HandRank.THREE_OF_A_KIND, [three_kind] + kickers
        
        # Two pair
        pairs = [r for r, count in rank_counts.items() if count == 2]
        if len(pairs) == 2:
            pairs.sort(reverse=True)
            kicker = [r for r, count in rank_counts.items() if count == 1][0]
            return HandRank.TWO_PAIR, pairs + [kicker]
        
        # Pair
        if len(pairs) == 1:
            pair = pairs[0]
            kickers = sorted([r for r, count in rank_counts.items() if count == 1], reverse=True)
            return HandRank.PAIR, [pair] + kickers
        
        # High card
        return HandRank.HIGH_CARD, sorted(ranks, reverse=True)
    
    @staticmethod
    def _compare_hands(hand1: Tuple[HandRank, List[int]], hand2: Tuple[HandRank, List[int]]) -> int:
        """
        Compare two hands.
        Returns: 1 if hand1 > hand2, -1 if hand1 < hand2, 0 if equal.
        """
        rank1, tiebreakers1 = hand1
        rank2, tiebreakers2 = hand2
        
        if rank1.value > rank2.value:
            return 1
        if rank1.value < rank2.value:
            return -1
        
        # Same rank, compare tiebreakers
        for t1, t2 in zip(tiebreakers1, tiebreakers2):
            if t1 > t2:
                return 1
            if t1 < t2:
                return -1
        
        return 0
    
    @staticmethod
    def compare_player_hands(players_cards: List[List[Card]], community_cards: List[Card]) -> List[int]:
        """
        Compare hands of multiple players.
        Returns list of player indices sorted by hand strength (best first).
        """
        evaluations = []
        for i, player_cards in enumerate(players_cards):
            all_cards = player_cards + community_cards
            rank, tiebreakers = HandEvaluator.evaluate_hand(all_cards)
            evaluations.append((i, rank, tiebreakers))
        
        # Sort by hand strength (best first)
        evaluations.sort(key=lambda x: (x[1].value, x[2]), reverse=True)
        
        # Handle ties - group players with identical hands
        result = []
        i = 0
        while i < len(evaluations):
            current_rank = evaluations[i][1]
            current_tiebreakers = evaluations[i][2]
            tied_players = [evaluations[i][0]]
            
            # Check for ties
            j = i + 1
            while j < len(evaluations):
                if (evaluations[j][1] == current_rank and 
                    evaluations[j][2] == current_tiebreakers):
                    tied_players.append(evaluations[j][0])
                    j += 1
                else:
                    break
            
            result.extend(tied_players)
            i = j
        
        return result

