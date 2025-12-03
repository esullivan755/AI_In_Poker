"""Interactive CLI poker game for human players."""
import sys
from poker.room import PokerRoom
from poker.player import Player, PlayerAction
from poker.demo_player import DemoPlayer
from poker.game import BettingRound, GameState


class HumanPlayer(Player):
    """Human player that gets input from command line."""
    
    def get_action(self, game_state: dict) -> tuple:
        """Get action from human input."""
        print("\n" + "="*60)
        print(f"Your Turn, {self.name}!")
        print("="*60)
        
        # Display game state
        print(f"\nBetting Round: {game_state['betting_round'].upper().replace('_', ' ')}")
        print(f"Pot: ${game_state['pot']}")
        print(f"Current Bet: ${game_state['current_bet']}")
        print(f"Your Chips: ${game_state['chips']}")
        print(f"Your Current Bet: ${game_state['player_current_bet']}")
        
        amount_to_call = game_state['current_bet_to_call']
        min_raise = game_state['min_raise']
        
        print(f"\nYour Hand: {', '.join(str(c) for c in game_state['hand'])}")
        
        if game_state['community_cards']:
            print(f"Community Cards: {', '.join(str(c) for c in game_state['community_cards'])}")
        
        print("\nOther Players:")
        for p in game_state['players']:
            if p['name'] != self.name:
                status = []
                if not p['is_active']:
                    status.append("FOLDED")
                if p['is_all_in']:
                    status.append("ALL-IN")
                status_str = f" ({', '.join(status)})" if status else ""
                print(f"  {p['name']}: ${p['chips']} chips, bet: ${p['current_bet']}{status_str}")
        
        # Show available actions
        print("\nAvailable Actions:")
        if amount_to_call == 0:
            print("  [c]heck - Check (no bet)")
            if game_state['chips'] >= min_raise:
                print(f"  [b]et <amount> - Bet (minimum ${min_raise})")
        else:
            print(f"  [f]old - Fold (give up hand)")
            print(f"  [c]all - Call ${amount_to_call}")
            if game_state['chips'] >= amount_to_call + min_raise:
                print(f"  [r]aise <amount> - Raise (minimum ${min_raise} more)")
        
        if game_state['chips'] > 0:
            print(f"  [a]ll-in - Go all-in (${game_state['chips']})")
        
        # Get user input
        while True:
            try:
                action_input = input("\nYour action: ").strip().lower()
                
                if not action_input:
                    continue
                
                parts = action_input.split()
                action_char = parts[0]
                
                if action_char == 'f' or action_char == 'fold':
                    return PlayerAction.FOLD, 0
                
                elif action_char == 'c' or action_char == 'check' or action_char == 'call':
                    if amount_to_call == 0:
                        return PlayerAction.CHECK, 0
                    else:
                        return PlayerAction.CALL, 0
                
                elif action_char == 'b' or action_char == 'bet':
                    if amount_to_call > 0:
                        print("Cannot bet when there's a bet to call. Use 'raise' instead.")
                        continue
                    if len(parts) < 2:
                        print("Please specify bet amount: bet <amount>")
                        continue
                    try:
                        amount = int(parts[1])
                        if amount < min_raise:
                            print(f"Bet must be at least ${min_raise}")
                            continue
                        if amount > game_state['chips']:
                            print(f"Insufficient chips. You have ${game_state['chips']}")
                            continue
                        return PlayerAction.BET, amount
                    except ValueError:
                        print("Invalid amount. Please enter a number.")
                        continue
                
                elif action_char == 'r' or action_char == 'raise':
                    if amount_to_call == 0:
                        print("Nothing to raise. Use 'bet' instead.")
                        continue
                    if len(parts) < 2:
                        print("Please specify raise amount: raise <amount>")
                        continue
                    try:
                        amount = int(parts[1])
                        if amount < min_raise:
                            print(f"Raise must be at least ${min_raise} more than current bet")
                            continue
                        if amount > game_state['chips'] - amount_to_call:
                            print(f"Insufficient chips. You need ${amount_to_call} to call plus ${amount} to raise.")
                            continue
                        return PlayerAction.RAISE, amount
                    except ValueError:
                        print("Invalid amount. Please enter a number.")
                        continue
                
                elif action_char == 'a' or action_char == 'all-in' or action_char == 'allin':
                    return PlayerAction.ALL_IN, 0
                
                elif action_char == 'q' or action_char == 'quit':
                    print("Quitting game...")
                    sys.exit(0)
                
                else:
                    print("Invalid action. Please try again.")
                    continue
            
            except KeyboardInterrupt:
                print("\n\nQuitting game...")
                sys.exit(0)
            except EOFError:
                print("\n\nQuitting game...")
                sys.exit(0)


def print_hand_result(game, player):
    """Print hand result for a player."""
    if game.community_cards:
        from poker.hand_evaluator import HandEvaluator
        all_cards = player.hand + game.community_cards
        rank, tiebreakers = HandEvaluator.evaluate_hand(all_cards)
        print(f"  {player.name}: {rank.name.replace('_', ' ').title()}")


def main():
    """Main interactive game loop."""
    print("="*60)
    print("Welcome to Texas Hold'em Poker!")
    print("="*60)
    
    # Get player name
    player_name = input("\nEnter your name: ").strip() or "Player"
    
    # Get number of AI opponents
    while True:
        try:
            num_opponents = input("How many AI opponents? (1-5): ").strip()
            num_opponents = int(num_opponents) if num_opponents else 2
            if 1 <= num_opponents <= 5:
                break
            print("Please enter a number between 1 and 5.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Get starting chips
    while True:
        try:
            starting_chips = input("Starting chips per player? (default 1000): ").strip()
            starting_chips = int(starting_chips) if starting_chips else 1000
            if starting_chips > 0:
                break
            print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Get blinds
    while True:
        try:
            small_blind = input("Small blind? (default 5): ").strip()
            small_blind = int(small_blind) if small_blind else 5
            big_blind = input("Big blind? (default 10): ").strip()
            big_blind = int(big_blind) if big_blind else 10
            if small_blind > 0 and big_blind > small_blind:
                break
            print("Big blind must be greater than small blind.")
        except ValueError:
            print("Please enter valid numbers.")
    
    # Create room and game
    room = PokerRoom(name="Interactive Room")
    game_id = room.create_game(small_blind=small_blind, big_blind=big_blind)
    
    # Create human player
    human_player = HumanPlayer("human", player_name, chips=starting_chips)
    room.add_player(human_player)
    room.add_player_to_game("human", game_id)
    
    # Create AI opponents
    ai_names = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
    for i in range(num_opponents):
        ai_player = DemoPlayer(f"ai{i}", ai_names[i], chips=starting_chips)
        room.add_player(ai_player)
        room.add_player_to_game(f"ai{i}", game_id)
    
    print(f"\nGame created with {num_opponents + 1} players!")
    print(f"Blinds: ${small_blind}/${big_blind}")
    print(f"Starting chips: ${starting_chips} per player")
    
    # Game loop
    hand_number = 0
    while True:
        hand_number += 1
        print("\n" + "="*60)
        print(f"HAND #{hand_number}")
        print("="*60)
        
        # Check if human player still has chips
        if human_player.chips == 0:
            print("\nYou're out of chips! Game over.")
            break
        
        # Check if enough players
        active_players = [p for p in room.players.values() if p.chips > 0]
        if len(active_players) < 2:
            print("\nNot enough players with chips. Game over.")
            break
        
        # Start hand
        if not room.start_game_hand(game_id):
            print("Failed to start hand. Not enough players.")
            break
        
        game = room.get_game(game_id)
        
        # Play through the hand
        max_iterations = 200
        iteration = 0
        last_betting_round = None
        last_human_action_round = None
        
        while game.state == GameState.IN_PROGRESS and iteration < max_iterations:
            iteration += 1
            current_player = game.get_current_player()
            
            if current_player is None:
                break
            
            # Skip if only one active player
            if len(game.get_active_players()) <= 1:
                break
            
            # Track betting round for change detection
            # (Actual display happens after actions to show new cards)
            
            # Get game state
            game_state = game.get_game_state_for_player(current_player)
            
            # Get action
            if isinstance(current_player, HumanPlayer):
                # Show summary if this is a new betting round since human's last action
                if last_human_action_round != game.betting_round and last_human_action_round is not None:
                    print("\n" + "-"*60)
                    print("ACTION SUMMARY:")
                    print("-"*60)
                    active_players = game.get_active_players()
                    for p in active_players:
                        if p != current_player:
                            status = []
                            if p.is_all_in:
                                status.append("ALL-IN")
                            if not p.is_active:
                                status.append("FOLDED")
                            status_str = f" ({', '.join(status)})" if status else ""
                            print(f"  {p.name}: ${p.chips} chips, bet: ${p.current_bet}{status_str}")
                    print(f"Pot: ${game.pot}")
                    print("-"*60 + "\n")
                
                action, amount = current_player.get_action(game_state)
                last_human_action_round = game.betting_round
            else:
                # AI player - show their action prominently
                print("\n" + "-"*60)
                print(f"{current_player.name}'s Turn")
                print("-"*60)
                
                # Show what they see
                if game.community_cards:
                    print(f"Community Cards: {', '.join(str(c) for c in game.community_cards)}")
                print(f"Pot: ${game.pot}, Current Bet: ${game.current_bet}")
                if current_player.current_bet < game.current_bet:
                    amount_to_call = game.current_bet - current_player.current_bet
                    print(f"{current_player.name} needs to call ${amount_to_call}")
                else:
                    print(f"{current_player.name} can check or bet")
                
                print(f"{current_player.name} is thinking...")
                action, amount = current_player.get_action(game_state)
            
            # Process action
            betting_round_before = game.betting_round
            success, message = game.process_action(current_player, action, amount)
            
            # Check if betting round advanced (new cards dealt)
            if betting_round_before != game.betting_round:
                print("\n" + "="*60)
                print(f"BETTING ROUND COMPLETE!")
                print(f"NEW ROUND: {game.betting_round.value.upper().replace('_', ' ')}")
                print("="*60)
                if game.community_cards:
                    print(f"Community Cards: {', '.join(str(c) for c in game.community_cards)}")
                print(f"Pot: ${game.pot}")
                print("="*60 + "\n")
                last_betting_round = game.betting_round
            
            if isinstance(current_player, HumanPlayer):
                print(f"\n{message}")
            else:
                # Show AI action prominently
                print(f"\n>>> {message.upper()} <<<")
                print(f"Pot: ${game.pot}, Current Bet: ${game.current_bet}")
                print(f"{current_player.name}'s Chips: ${current_player.chips}")
                if current_player.is_all_in:
                    print(f"{current_player.name} is ALL-IN!")
                print("-"*60)
            
            # Show community cards when they're dealt (after action)
            # This is handled by the betting round change detection above
        
        # Show results
        print("\n" + "="*60)
        print("HAND RESULTS")
        print("="*60)
        
        if game.winners:
            print("\nWinners:")
            for winner, amount in game.winners:
                print(f"  {winner.name} wins ${amount}!")
                print(f"    Hand: {', '.join(str(c) for c in winner.hand)}")
                if game.community_cards:
                    print(f"    Community: {', '.join(str(c) for c in game.community_cards)}")
                print_hand_result(game, winner)
        else:
            print("Hand ended early (all players folded)")
        
        print("\nChip Counts:")
        for player in game.players:
            print(f"  {player.name}: ${player.chips}")
        
        # Ask to continue
        if human_player.chips == 0:
            print("\nYou're out of chips! Game over.")
            break
        
        while True:
            continue_game = input("\nPlay another hand? (y/n): ").strip().lower()
            if continue_game in ['y', 'yes']:
                break
            elif continue_game in ['n', 'no']:
                print("\nThanks for playing!")
                return
            else:
                print("Please enter 'y' or 'n'")
    
    print("\nThanks for playing!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Thanks for playing!")
    except EOFError:
        print("\n\nGame ended. Thanks for playing!")

