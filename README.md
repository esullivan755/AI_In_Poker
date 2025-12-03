# AI_In_Poker

A poker application that allows LLMs (Large Language Models) to play against each other in Texas Hold'em poker games.

## Features

- **Complete Texas Hold'em Game Engine**: Full implementation of poker rules including:
  - Hand evaluation (all hand rankings from high card to royal flush)
  - Betting rounds (pre-flop, flop, turn, river)
  - Pot management and side pots for all-in scenarios
  - Blinds and dealer rotation
  
- **Poker Room System**: Manage multiple games and players:
  - Create and manage multiple poker games
  - Add/remove players from games
  - Track player chips and game state
  
- **Player Abstraction**: Base `Player` class designed to be extended for LLM integration:
  - Simple interface for player actions (fold, check, call, bet, raise, all-in)
  - Game state provided to players for decision-making
  - Ready for API integration

## Project Structure

```
poker/
  ├── cards.py           # Card, Deck, Suit, Rank classes
  ├── hand_evaluator.py  # Hand evaluation and comparison logic
  ├── player.py          # Base Player class and PlayerAction enum
  ├── game.py            # TexasHoldemGame class with full game logic
  ├── room.py            # PokerRoom class for managing games
  └── demo_player.py     # Simple demo player for testing

example.py               # Example usage of the poker room
interactive_game.py       # Interactive CLI game for human players
tests/                   # Comprehensive test suite
requirements.txt         # Python dependencies
```

## Quick Start

### Basic Usage

```python
from poker.room import PokerRoom
from poker.demo_player import DemoPlayer

# Create a poker room
room = PokerRoom(name="My Room")

# Create a game
game_id = room.create_game(small_blind=5, big_blind=10)

# Create and add players
player1 = DemoPlayer("p1", "Alice", chips=1000)
player2 = DemoPlayer("p2", "Bob", chips=1000)

room.add_player(player1)
room.add_player(player2)
room.add_player_to_game("p1", game_id)
room.add_player_to_game("p2", game_id)

# Start a hand
room.start_game_hand(game_id)

# Process player actions
room.process_player_action("p1", "call", 0)
room.process_player_action("p2", "check", 0)
```

### Running the Example

```bash
python3 example.py
```

### Playing Interactive Game

Play against AI opponents in a command-line interface:

```bash
python3 interactive_game.py
```

The interactive game allows you to:
- Set your name and number of AI opponents
- Configure starting chips and blinds
- Play full hands with real-time decision making
- See your cards, community cards, and other players' status
- Make decisions: fold, check, call, bet, raise, or all-in

**Example gameplay:**
```
Your Turn, Player!

Betting Round: PRE FLOP
Pot: $25
Current Bet: $10
Your Chips: $1000
Your Current Bet: $0

Your Hand: A♠, K♥

Available Actions:
  [f]old - Fold (give up hand)
  [c]all - Call $10
  [r]aise <amount> - Raise (minimum $10 more)
  [a]ll-in - Go all-in ($1000)

Your action: c
```

## Player Interface

To create a custom player (e.g., for LLM integration), extend the `Player` class:

```python
from poker.player import Player, PlayerAction

class MyLLMPlayer(Player):
    def get_action(self, game_state: dict) -> tuple:
        """
        game_state contains:
        - betting_round: str
        - pot: int
        - current_bet: int
        - current_bet_to_call: int
        - min_raise: int
        - community_cards: List[Card]
        - hand: List[Card]
        - chips: int
        - players: List[dict]
        - is_your_turn: bool
        
        Returns: (action_type, amount)
        """
        # Your logic here
        return PlayerAction.CALL, 0
```

## Game Flow

1. **Create Room**: Initialize a `PokerRoom`
2. **Create Game**: Create a game with blinds
3. **Add Players**: Add players to the room and assign them to games
4. **Start Hand**: Begin a new hand (deals cards, posts blinds)
5. **Process Actions**: Players take turns making actions
6. **Betting Rounds**: Game automatically advances through betting rounds
7. **Showdown**: Winners are determined and chips distributed

## Testing

The project includes comprehensive tests covering all major components:

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run specific test file
python3 -m pytest tests/test_cards.py -v

# Run with coverage
python3 -m pytest tests/ --cov=poker --cov-report=html
```

**Test Coverage:**
- ✅ Card and Deck functionality (11 tests)
- ✅ Hand evaluation (all hand types) (14 tests)
- ✅ Player actions and state management (10 tests)
- ✅ Game logic and betting rounds (13 tests)
- ✅ Poker room management (16 tests)

**Total: 64 tests** - All passing ✅

## Future Enhancements

- API server for LLM integration
- WebSocket support for real-time gameplay
- Tournament mode
- Hand history and replay
- Statistics tracking
- Multiple game variants (Omaha, etc.)

## License

MIT License
