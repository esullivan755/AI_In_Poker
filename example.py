"""Example usage of the poker room system."""
from poker.room import PokerRoom
from poker.player import Player
from poker.demo_player import DemoPlayer
from poker.game import BettingRound


def main():
    # Create a poker room
    room = PokerRoom(name="Demo Room")
    
    # Create a game
    game_id = room.create_game(small_blind=5, big_blind=10)
    print(f"Created game: {game_id}")
    
    # Create some players
    players = [
        DemoPlayer("player1", "Alice", chips=1000),
        DemoPlayer("player2", "Bob", chips=1000),
        DemoPlayer("player3", "Charlie", chips=1000),
    ]
    
    # Add players to room and game
    for player in players:
        room.add_player(player)
        room.add_player_to_game(player.player_id, game_id)
        print(f"Added {player.name} to game")
    
    # Start a hand
    print("\n=== Starting New Hand ===")
    if room.start_game_hand(game_id):
        print("Hand started successfully!")
        
        game = room.get_game(game_id)
        
        # Play through the hand
        max_iterations = 100
        iteration = 0
        
        while game.state.value == "in_progress" and iteration < max_iterations:
            iteration += 1
            current_player = game.get_current_player()
            
            if current_player is None:
                break
            
            # Get game state for player
            game_state = game.get_game_state_for_player(current_player)
            
            # Get player action
            action, amount = current_player.get_action(game_state)
            
            # Process action
            success, message = game.process_action(current_player, action, amount)
            print(f"{message}")
            
            # Show game state
            if game.betting_round != BettingRound.PRE_FLOP or len(game.community_cards) > 0:
                print(f"  Community cards: {game.community_cards}")
            print(f"  Pot: {game.pot}, Current bet: {game.current_bet}")
            print(f"  Players: {[f'{p.name}({p.chips})' for p in game.players]}")
            print()
        
        # Show results
        print("=== Hand Results ===")
        if game.winners:
            for winner, amount in game.winners:
                print(f"{winner.name} wins {amount} chips!")
                print(f"  Hand: {winner.hand}")
                if game.community_cards:
                    print(f"  Community: {game.community_cards}")
        else:
            print("No winners (hand ended early)")
        
        print(f"\nFinal chip counts:")
        for player in game.players:
            print(f"  {player.name}: {player.chips} chips")
    else:
        print("Failed to start hand")


if __name__ == "__main__":
    main()

