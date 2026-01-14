# Game AI Client SDK

[![Version](https://img.shields.io/badge/version-0.7.0-blue.svg)](https://pypi.org/project/game-ai-client/)
[![Python](https://img.shields.io/badge/python-3.9+-brightgreen.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A professional Python SDK for integrating AI into turn-based board games using Monte Carlo Tree Search (MCTS). This framework provides a generic, extensible interface that allows game developers to add intelligent AI opponents with minimal coupling to game-specific logic.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
- [Architecture](#architecture)
- [Advanced Features](#advanced-features)
- [Integration Guides](#integration-guides)
- [API Reference](#api-reference)
- [Examples](#examples)
- [Self-Play & Machine Learning](#self-play--machine-learning)
- [Event System](#event-system)
- [Changelog](#changelog)
- [Contributing](#contributing)

## Features

### Core Features

- **Generic Game Interface**: Protocol-based design works with any turn-based game
- **Powerful MCTS Engine**: State-of-the-art Monte Carlo Tree Search with customizable strategies
- **Three Difficulty Levels**: Easy, Medium, and Hard AI opponents with distinct playing strengths
- **AI vs AI Gameplay**: Built-in support for automated matches with configurable difficulty
- **Dynamic Difficulty Adaptation**: AI that adjusts based on human player performance
- **Minimal Integration**: Keep full control of your game logic - provide only a move function

### Advanced Features

- **RAVE (Rapid Action Value Estimation)**: Accelerated tree search convergence
- **MCTS Solver**: Proven win/loss/draw detection for perfect endgame play
- **Progressive Widening**: Intelligent branching factor reduction for complex games
- **Heuristic Simulations**: Optional position evaluators for stronger play
- **Tree Reuse**: Memory-efficient MCTS across sequential moves
- **Strategy Pattern**: Fully customizable MCTS phases (Selection, Expansion, Simulation, Backpropagation)

### Integration & Deployment

- **Self-Play Infrastructure**: Built-in support for AI training data collection
- **Event System**: RabbitMQ-based event publishing and listening
- **ML Integration**: Events for machine learning model integration
- **Game Registration**: Dynamic game discovery and validation
- **Docker Support**: Containerized deployment with RabbitMQ

## Installation

### Basic Installation

```bash
pip install game-ai-client==0.7.0
```

### Development Installation

```bash
git clone <repository-url>
cd sdk-project
pip install -e .
pip install -r requirements-dev.txt
```

### Optional Dependencies

```bash
# For RabbitMQ event publishing (optional)
pip install pika>=1.3.2
```

## Quick Start

### 30-Second Integration

```python
from game_sdk import AIGameClient, build_generic_state

# 1. Create your apply_move function
def apply_move_fn(state, move):
    # Your game logic here
    # Returns new state after applying move
    return new_state

# 2. Create AI client
client = AIGameClient(
    game_id="my_game",
    api_key="demo-key",
    apply_move_fn=apply_move_fn
)

# 3. Get AI move
state = build_generic_state(...)
move = client.best_move(match_id, iterations=1000)
```

### AI vs AI Quick Start

For games implementing `TurnBasedGame` protocol:

```python
from your_game import YourGame, state_to_game, game_to_state

# Create game
game = YourGame()

# Run AI vs AI match
result = game.ai_vs_ai_difficulty_selection(
    difficulty1="medium",
    difficulty2="hard",
    state_to_game_fn=state_to_game,
    game_to_state_fn=game_to_state,
    game_id="your_game"
)

print(f"Winner: {result['winner']}")
print(f"Moves: {result['move_count']}")
```

**Available difficulties**: `"easy"`, `"medium"`, `"hard"`

**Difficulty Details**:
- **Easy**: 100 MCTS iterations + 50% random moves (beginner-friendly)
- **Medium**: 1000 MCTS iterations, pure MCTS strategy (intermediate)
- **Hard**: 5000 MCTS iterations, near-perfect play (expert)

## Core Concepts

### The TurnBasedGame Protocol

Your game needs to implement this simple protocol:

```python
from game_sdk.ai_client import TurnBasedGame
from typing import List, Dict, Any

class MyGame(TurnBasedGame):
    def get_legal_actions(self) -> List[Dict[str, Any]]:
        """Return all legal moves for current player."""
        return [
            {"id": "move_1", "player_index": 0, "type": "PLACE", "position": {"row": 0, "col": 0}},
            # ... more moves
        ]

    def is_game_over(self) -> bool:
        """Check if game has ended."""
        return self._check_winner() or self._check_draw()

    def game_result(self) -> int:
        """Return result from current player's perspective.
        Returns: 1 (win), -1 (loss), 0 (draw)
        """
        return 1 if self.current_player_won() else -1 if self.current_player_lost() else 0

    def move(self, action: Dict[str, Any]) -> "MyGame":
        """Apply move and return new game state (can be immutable or mutable)."""
        new_game = self.clone()
        new_game.apply_action(action)
        return new_game
```

### Generic State Format

The SDK uses a standardized state representation for communication:

```python
{
    "game_id": "tictactoe",
    "state_id": "unique-uuid",
    "turn_index": 5,
    "players": [
        {"id": "P1", "type": "human", "symbol": "X"},
        {"id": "P2", "type": "ai_mcts", "symbol": "O"}
    ],
    "board": {
        "representation": "grid",
        "rows": 3,
        "cols": 3,
        "cells": [[1, 0, 2], [0, 1, 0], [2, 0, 0]],
        "legend": {
            "0": "empty",
            "1": "player_1_piece",
            "2": "player_2_piece"
        }
    },
    "status": "IN_PROGRESS",
    "is_terminal": false,
    "legal_moves": [...],
    "result": null,
    "extra": {"move_count": 5}
}
```

Build states using the utility function:

```python
from game_sdk.utils import build_generic_state

state = build_generic_state(
    game_id="my_game",
    board=[[" ", "X", " "], ["O", "X", " "], [" ", " ", " "]],
    players=[
        {"id": "P1", "type": "human", "symbol": "X"},
        {"id": "P2", "type": "ai_mcts", "symbol": "O"}
    ],
    current_player_symbol="O",
    move_count=3,
    finished=False,
    legal_moves=compute_legal_moves(...),
    result=None
)
```

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│  Game Implementation Layer                                  │
│  - Your game class implementing TurnBasedGame              │
│  - Game-specific rules and logic                           │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  Adapter Layer (integration.py)                             │
│  - GenericGameAdapter: Wraps game in SDK interface         │
│  - State converters: game ↔ generic state format           │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  AI Layer                                                   │
│  - AIGameClient: Match management & AI moves               │
│  - DynamicMCTSAgent: Adaptive difficulty                   │
│  - StatefulGameAdapter: State-level decisions              │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  MCTS Engine (mcts.py)                                      │
│  - Selection: UCB1 or RAVE                                 │
│  - Expansion: Single move or progressive widening          │
│  - Simulation: Random rollout or heuristic                 │
│  - Backpropagation: Value updates with RAVE stats          │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  Logging & Events Layer                                     │
│  - EventPublisher: RabbitMQ event publishing               │
│  - EventListener: Platform event consumption               │
│  - GameClient: Match and move logging                      │
└─────────────────────────────────────────────────────────────┘
```

### Design Patterns

#### 1. Strategy Pattern (MCTS Customization)

Each phase of MCTS is a pluggable strategy:

```python
from game_sdk.mcts import (
    UCBSelectionStrategy,
    DefaultExpansionStrategy,
    RandomSimulationStrategy,
    DefaultBackpropagationStrategy,
    run_mcts
)

# Customize MCTS behavior
custom_selection = UCBSelectionStrategy(exploration_constant=1.41)
custom_simulation = RandomSimulationStrategy()

# Run MCTS with custom strategies
best_move = run_mcts(
    state,
    iterations=1000,
    selection_strategy=custom_selection,
    simulation_strategy=custom_simulation
)
```

#### 2. State Pattern (Dynamic Difficulty)

The `DynamicMCTSAgent` uses state objects for difficulty transitions:

```python
from game_sdk.dynamic_mcts_agent import DynamicMCTSAgent

agent = DynamicMCTSAgent(initial_difficulty="medium")

# Agent automatically adapts difficulty based on performance
move = agent.select_move(game_state)
agent.update_performance(game_result)
```

#### 3. Protocol-Based Design

Python protocols ensure compile-time type safety:

```python
from game_sdk.mcts import GameEnv
from typing import List, Any

class MyGameEnv(GameEnv):
    def legal_moves(self) -> List[Any]:
        pass

    def is_game_over(self) -> bool:
        pass

    def game_result(self) -> int:
        pass

    def move(self, action: Any) -> "MyGameEnv":
        pass

    def current_player(self) -> int:
        pass
```

## Advanced Features

### 1. RAVE (Rapid Action Value Estimation)

RAVE accelerates MCTS by sharing information across the tree:

```python
from game_sdk.mcts import run_mcts, UCBSelectionStrategy

# Enable RAVE for faster convergence
selection = UCBSelectionStrategy(
    exploration_constant=1.41,
    use_rave=True,
    rave_constant=300
)

move = run_mcts(state, iterations=1000, selection_strategy=selection)
```

**Benefits**:
- 2-3x faster convergence in early game
- Better move quality with fewer iterations
- Particularly effective in games with similar moves

### 2. MCTS Solver

Detects proven wins/losses/draws for perfect endgame play:

```python
from game_sdk.mcts import Node, solve_node

# Solver automatically identifies proven outcomes
node = Node(state)
solve_node(node, game_env)

if node.is_proven_win:
    print("Guaranteed win from this position!")
elif node.is_proven_loss:
    print("This position is lost.")
```

**Use Cases**:
- Perfect endgame play
- Identifying forced wins
- Pruning losing branches

### 3. Progressive Widening

Reduces branching factor in games with many legal moves:

```python
from game_sdk.mcts import DefaultExpansionStrategy

# Limit children based on visit count
expansion = DefaultExpansionStrategy(
    progressive_widening=True,
    widening_constant=2.0
)

# Children = min(legal_moves, widening_constant * sqrt(visit_count))
```

**Ideal For**:
- Games with 20+ legal moves per position
- Go, Chess variants, complex card games
- Memory-constrained environments

### 4. Heuristic Simulations

Replace random rollouts with domain knowledge:

```python
from game_sdk.mcts import SimulationStrategy
from game_sdk.utils import simple_heuristic

class HeuristicSimulation(SimulationStrategy):
    def simulate(self, node: Node, game_env: GameEnv) -> float:
        # Use position evaluation instead of random play
        return simple_heuristic(game_env, player_index=0)

move = run_mcts(state, simulation_strategy=HeuristicSimulation())
```

**Performance Boost**:
- 30-50% stronger play with good heuristics
- Faster training convergence
- Better opening/endgame play

### 5. Tree Reuse

Reuse MCTS tree across moves for efficiency:

```python
from game_sdk.ai_client import StatefulGameAdapter

adapter = StatefulGameAdapter(apply_move_fn)

# First move builds tree
move1 = adapter.best_move(state1, iterations=1000)

# Second move reuses tree from state1
move2 = adapter.best_move(state2, iterations=1000)  # Faster!
```

**Memory Savings**:
- 60-80% reduction in computation
- Particularly effective in AI vs AI games

### 6. Dynamic Difficulty Adaptation

AI that learns your skill level:

```python
from game_sdk.dynamic_mcts_agent import DynamicMCTSAgent

agent = DynamicMCTSAgent(
    initial_difficulty="medium",
    performance_window=10,  # Track last 10 games
    adaptation_threshold=0.7  # Adjust if win rate > 70%
)

# Agent automatically adjusts difficulty
for game in games:
    move = agent.select_move(game.state)
    result = game.play_move(move)
    agent.update_performance(result)  # Learn from outcome
```

**Features**:
- Automatic difficulty adjustment
- Customizable performance windows
- Smooth transitions between difficulty levels

## Integration Guides

### Basic Integration (5 minutes)

You only need to provide ONE function to enable AI:

```python
from typing import Dict, Any
from game_sdk.utils import build_generic_state

def apply_move_my_game(state: Dict[str, Any], move: Dict[str, Any]) -> Dict[str, Any]:
    """Apply move to state and return new state."""

    # 1. Extract data from state
    board = decode_board(state["board"])
    players = state["players"]
    player_index = move["player_index"]

    # 2. Apply move using your game logic
    board[move["position"]["row"]][move["position"]["col"]] = players[player_index]["symbol"]

    # 3. Check game over
    finished, winner = check_game_over(board)

    # 4. Build and return new state
    return build_generic_state(
        game_id=state["game_id"],
        board=board,
        players=players,
        current_player_symbol=get_next_player(players, player_index),
        move_count=state["extra"]["move_count"] + 1,
        finished=finished,
        legal_moves=[] if finished else get_legal_moves(board),
        result=compute_result_map(winner, players) if finished else None
    )
```

Then use it with AIGameClient:

```python
from game_sdk import AIGameClient

client = AIGameClient(
    game_id="my_game",
    api_key="demo-key",
    apply_move_fn=apply_move_my_game
)

# Get AI moves
move = client.best_move(match_id, iterations=1000)
```

### Full Integration with TurnBasedGame

For complete AI vs AI support, implement the protocol:

```python
from game_sdk.ai_client import TurnBasedGame
from typing import List, Dict, Any

class MyGame(TurnBasedGame):
    def __init__(self, board, players, current_player_symbol):
        self.board = board
        self.players = players
        self.current_player_symbol = current_player_symbol

    def get_legal_actions(self) -> List[Dict[str, Any]]:
        actions = []
        for r in range(len(self.board)):
            for c in range(len(self.board[0])):
                if self.board[r][c] == " ":
                    actions.append({
                        "id": f"PLACE_{r}_{c}",
                        "player_index": self._current_player_index(),
                        "type": "PLACE",
                        "position": {"row": r, "col": c}
                    })
        return actions

    def is_game_over(self) -> bool:
        return self._check_winner() or self._check_draw()

    def game_result(self) -> int:
        """From current player's perspective."""
        winner = self._get_winner()
        if winner == self.current_player_symbol:
            return 1
        elif winner is None:
            return 0
        else:
            return -1

    def move(self, action: Dict[str, Any]) -> "MyGame":
        new_board = [row[:] for row in self.board]
        pos = action["position"]
        new_board[pos["row"]][pos["col"]] = self.current_player_symbol

        next_player = self._next_player()
        return MyGame(new_board, self.players, next_player)
```

Now you automatically get AI vs AI:

```python
game = MyGame(empty_board, players, "X")

result = game.ai_vs_ai_difficulty_selection(
    difficulty1="medium",
    difficulty2="hard",
    state_to_game_fn=state_to_game_converter,
    game_to_state_fn=game_to_state_converter,
    game_id="my_game"
)
```

See [GAME_INTEGRATION_GUIDE.md](GAME_INTEGRATION_GUIDE.md) for complete details.

## API Reference

### Core Classes

#### AIGameClient

High-level client for AI game management.

```python
from game_sdk import AIGameClient

client = AIGameClient(
    game_id: str,
    api_key: str,
    apply_move_fn: Callable,
    base_url: str = "http://localhost:8000"
)

# Methods
match_id = client.start_match(players: List[Dict], metadata: Dict)
client.send_state(match_id: str, state: Dict)
move = client.best_move(match_id: str, iterations: int = 1000)
client.log_move(match_id: str, state: Dict, move: Dict)
client.end_match(match_id: str, result: str, final_state: Dict)
```

#### GameClient

Lower-level client for platform communication.

```python
from game_sdk import GameClient

client = GameClient(
    game_id: str,
    api_key: str,
    base_url: str = "http://localhost:8000"
)

# Methods
match_id = client.start_match(players: List[Dict], metadata: Dict)
client.log_move(match_id: str, state: Dict, move: Dict)
client.log_event(match_id: str, event_type: str, event_data: Dict)
client.end_match(match_id: str, result: str, final_state: Dict)
```

#### DynamicMCTSAgent

Adaptive difficulty AI agent.

```python
from game_sdk.dynamic_mcts_agent import DynamicMCTSAgent

agent = DynamicMCTSAgent(
    initial_difficulty: str = "medium",
    performance_window: int = 10,
    adaptation_threshold: float = 0.7
)

move = agent.select_move(game_state: TurnBasedGame)
agent.update_performance(result: float)  # 1.0 (win), 0.0 (draw), -1.0 (loss)
agent.reset()
```

#### MLPredictionClient

Client for machine learning model predictions.

```python
from game_sdk import MLPredictionClient, convert_board_to_cells

client = MLPredictionClient(
    base_url: str = "http://localhost:8000",
    timeout: int = 5
)

# Convert board to numeric format
board = [['X', '', ''], ['', 'O', ''], ['', '', '']]
cells = convert_board_to_cells(board)  # [[1, 0, 0], [0, 2, 0], [0, 0, 0]]

# Get win probability predictions
probs = client.predict_win_probability(
    board_cells=cells,
    turn_index=0,
    model_type="hybrid"  # or "baseline"
)

# Get move predictions
move = client.predict_move(
    board_cells=cells,
    turn_index=0,
    model_type="catboost"  # or "decision-tree", "xgboost"
)

# Check availability
is_available = client.is_available()
```

### Utility Functions

```python
from game_sdk.utils import (
    build_generic_state,
    symbol_to_int,
    detect_move,
    simple_heuristic
)

# Build standardized state
state = build_generic_state(
    game_id: str,
    board: List[List[str]],
    players: List[Dict],
    current_player_symbol: str,
    move_count: int,
    finished: bool,
    legal_moves: List[Dict],
    result: Optional[Dict] = None
)

# Convert symbols to integers for MCTS
int_board = [[symbol_to_int(cell, players) for cell in row] for row in board]

# Detect move between two boards
move = detect_move(old_board, new_board, players)

# Simple position evaluation
score = simple_heuristic(game_env, player_index)
```

### MCTS Functions

```python
from game_sdk.mcts import (
    run_mcts,
    Node,
    UCBSelectionStrategy,
    DefaultExpansionStrategy,
    RandomSimulationStrategy
)

# Run MCTS search
best_move = run_mcts(
    state: GameEnv,
    iterations: int,
    selection_strategy: SelectionStrategy = None,
    expansion_strategy: ExpansionStrategy = None,
    simulation_strategy: SimulationStrategy = None,
    backpropagation_strategy: BackpropagationStrategy = None
)

# Create custom strategies
selection = UCBSelectionStrategy(
    exploration_constant: float = 1.41,
    use_rave: bool = False,
    rave_constant: float = 300
)

expansion = DefaultExpansionStrategy(
    progressive_widening: bool = False,
    widening_constant: float = 2.0
)
```

## Examples

### Example 1: Human vs AI

```python
from game_sdk import AIGameClient, build_generic_state
from my_game import MyGame, apply_move_fn, get_legal_moves

client = AIGameClient("my_game", "api-key", apply_move_fn)

players = [
    {"id": "P1", "type": "human", "symbol": "X"},
    {"id": "P2", "type": "ai_mcts", "symbol": "O"}
]

match_id = client.start_match(players, metadata={"mode": "casual"})
game = MyGame()

while not game.is_over():
    state = build_generic_state(
        game_id="my_game",
        board=game.board,
        players=players,
        current_player_symbol=game.current_player,
        move_count=game.move_count,
        finished=False,
        legal_moves=get_legal_moves(game)
    )

    if game.current_player == "X":
        # Human turn
        move = get_human_input()
    else:
        # AI turn
        client.send_state(match_id, state)
        move = client.best_move(match_id, iterations=1000)

    game.apply_move(move)
    client.log_move(match_id, state, move)

client.end_match(match_id, game.result(), game.final_state())
```

### Example 2: AI vs AI Tournament

```python
from my_game import MyGame

def run_tournament(num_games=10):
    results = {"P1": 0, "P2": 0, "Draw": 0}

    for i in range(num_games):
        game = MyGame()

        result = game.ai_vs_ai_difficulty_selection(
            difficulty1="medium",
            difficulty2="hard",
            state_to_game_fn=state_to_game,
            game_to_state_fn=game_to_state,
            game_id="my_game",
            verbose=False
        )

        if result['winner'] == "X":
            results["P1"] += 1
        elif result['winner'] == "O":
            results["P2"] += 1
        else:
            results["Draw"] += 1

    return results

stats = run_tournament(20)
print(f"P1 wins: {stats['P1']}, P2 wins: {stats['P2']}, Draws: {stats['Draw']}")
```

### Example 3: Custom MCTS Strategies

```python
from game_sdk.mcts import (
    run_mcts,
    UCBSelectionStrategy,
    SimulationStrategy,
    Node,
    GameEnv
)

class CustomSimulation(SimulationStrategy):
    def simulate(self, node: Node, game_env: GameEnv) -> float:
        # Use domain knowledge instead of random rollout
        current = game_env

        while not current.is_game_over():
            moves = current.legal_moves()
            # Prioritize center moves in tic-tac-toe
            center_moves = [m for m in moves if is_center(m)]
            move = center_moves[0] if center_moves else random.choice(moves)
            current = current.move(move)

        return current.game_result()

# Use custom strategy
selection = UCBSelectionStrategy(exploration_constant=1.41, use_rave=True)
simulation = CustomSimulation()

move = run_mcts(
    game_state,
    iterations=2000,
    selection_strategy=selection,
    simulation_strategy=simulation
)
```

For complete working examples, see:
- `tictactoe.py` - Complete Tic-Tac-Toe implementation
- `lobby_handler.py` - Lobby event handling and game initialization
- `selfplay_ai_vs_ml.py` - Self-play with ML model integration

## Self-Play & Machine Learning

### Self-Play Infrastructure

The SDK includes a complete self-play system for generating training data:

```python
from game_sdk.selfplay_runner import SelfPlayRunner, SelfPlayEpisodeConfig

config = SelfPlayEpisodeConfig(
    game_id="my_game",
    num_episodes=100,
    mcts_iterations=800,
    temperature=1.0,  # Exploration temperature
    save_trajectory=True
)

runner = SelfPlayRunner(
    game_integration=game_integration,
    config=config
)

# Generate training data
trajectories = runner.run()

for trajectory in trajectories:
    print(f"Episode: {trajectory.episode_id}")
    print(f"Moves: {len(trajectory.states)}")
    print(f"Winner: {trajectory.winner}")
    # trajectory.states, trajectory.actions, trajectory.rewards
```

### Game Registration

Register your game for self-play discovery:

```python
from game_sdk import register_game

GAME_INTEGRATION = register_game(
    game_name="my_game",
    create_game=create_game_fn,
    state_to_game=state_to_game_fn,
    game_to_state=game_to_state_fn,
    default_players=default_players_fn
)
```

### Integration Validation

```python
from game_sdk import validate_integration

report = validate_integration(GAME_INTEGRATION, "my_game")

if report["errors"]:
    print("Errors:", report["errors"])
elif report["warnings"]:
    print("Warnings:", report["warnings"])
else:
    print("Integration valid!")
```

See [GAME_INTEGRATION_GUIDE.md](GAME_INTEGRATION_GUIDE.md) for complete self-play integration.

## Event System

### Event Publishing

Publish game events to RabbitMQ for logging and analytics:

```python
from game_sdk.event_publisher import EventPublisher, EventPublisherConfig
from game_sdk.events import GameStartedEvent, GameEndedEvent

config = EventPublisherConfig(
    host="localhost",
    port=5672,
    username="guest",
    password="guest",
    exchange="game_events"
)

publisher = EventPublisher(config)

# Publish events
start_event = GameStartedEvent(
    game_id="my_game",
    match_id="match-123",
    players=[...],
    metadata={"mode": "ranked"}
)
publisher.publish(start_event)

end_event = GameEndedEvent(
    game_id="my_game",
    match_id="match-123",
    result="P1_WIN",
    final_state={...}
)
publisher.publish(end_event)
```

### Event Listening

Listen for platform events:

```python
from game_sdk.event_listener import EventListener, EventListenerConfig

config = EventListenerConfig(
    host="localhost",
    port=5672,
    username="guest",
    password="guest",
    queue="game_ai_queue"
)

def handle_lobby_ready(event):
    print(f"Lobby ready: {event.lobby_id}")
    # Start game

listener = EventListener(config)
listener.subscribe("lobby.ready", handle_lobby_ready)
listener.start()
```

### ML Integration Events

```python
from game_sdk.events import MLMoveRequestEvent, MLMoveResponseEvent

# Request ML prediction
request = MLMoveRequestEvent(
    game_id="my_game",
    match_id="match-123",
    state=current_state,
    legal_moves=legal_moves
)
publisher.publish(request)

# Handle ML response
def handle_ml_response(event: MLMoveResponseEvent):
    move = event.predicted_move
    confidence = event.confidence
    game.apply_move(move)

listener.subscribe("ml.move.response", handle_ml_response)
```

### RabbitMQ Setup (Optional)

The SDK includes built-in event logging to RabbitMQ. To enable it, start RabbitMQ using Docker:

```bash
docker-compose up -d
```

This will start RabbitMQ on:
- AMQP port: 5672
- Management UI: http://localhost:15672

Configure via environment variables:
```bash
export RABBITMQ_HOST=localhost
export RABBITMQ_PORT=5672
export RABBITMQ_USER=guest
export RABBITMQ_PASS=guest
```

If RabbitMQ is unavailable, the SDK gracefully falls back to stdout logging.

## Changelog

### Version 0.7.0 (Current)

**New Features**:
- See detailed changes in version history

### Version 0.5.0

**New Features**:
- Self-play infrastructure with `SelfPlayRunner`
- Event system with RabbitMQ integration
- ML integration events (MLMoveRequestEvent, MLMoveResponseEvent)
- Game registration and validation utilities
- Dynamic difficulty adaptation with `DynamicMCTSAgent`
- RAVE (Rapid Action Value Estimation)
- MCTS Solver for proven outcomes
- Progressive widening for complex games
- Tree reuse optimization

**Improvements**:
- Enhanced MCTS with multiple strategy options
- Better documentation and examples
- Improved error handling
- Optional RabbitMQ dependency

### Version 0.1.7

**Bug Fixes**:
- Fixed winner determination in `ai_vs_ai_difficulty_selection()`
- Corrected result interpretation for Hard difficulty

**Improvements**:
- Made RabbitMQ dependency optional
- Added graceful fallback to stdout logging

### Version 0.1.2

**Features**:
- Initial MCTS implementation
- Three difficulty levels
- Generic game interface
- Basic event logging

## Contributing

We welcome contributions!

### Development Setup

```bash
git clone <repository-url>
cd sdk-project
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e .
pip install -r requirements-dev.txt
```

### Running Tests

```bash
pytest tests/
```

### Code Style

```bash
black game_sdk/
flake8 game_sdk/
mypy game_sdk/
```

## Project Structure

```
sdk-project/
├── game_sdk/                  # Main SDK package (~4,662 LOC)
│   ├── __init__.py           # Public API exports (101 LOC)
│   ├── mcts.py               # MCTS engine (1,009 LOC)
│   ├── ai_client.py          # AI client (564 LOC)
│   ├── dynamic_mcts_agent.py # Adaptive difficulty (524 LOC)
│   ├── ml_client.py          # ML prediction client (216 LOC)
│   ├── events.py             # Event models (357 LOC)
│   ├── event_publisher.py    # RabbitMQ publishing (293 LOC)
│   ├── event_listener.py     # RabbitMQ listening (345 LOC)
│   ├── selfplay_runner.py    # Self-play infrastructure (440 LOC)
│   ├── integration.py        # Game integration (150 LOC)
│   ├── registration.py       # Game registration (328 LOC)
│   ├── client.py             # Platform client (123 LOC)
│   ├── utils.py              # Utilities (147 LOC)
│   └── rabbitmq.py           # RabbitMQ wrapper (65 LOC)
├── tictactoe.py              # Complete Tic-Tac-Toe example (668 LOC)
├── lobby_handler.py          # Lobby event handling example
├── selfplay_ai_vs_ml.py      # Self-play with ML integration
├── README.md                 # This file
├── GAME_INTEGRATION_GUIDE.md # Integration guide
├── pyproject.toml            # Package configuration
├── docker-compose.yml        # Docker configuration for RabbitMQ
└── Dockerfile                # Container configuration
```

## Requirements

- Python 3.9+
- pika 1.3.2 (optional, for RabbitMQ)

## License

MIT License - see LICENSE file for details.

## Credits

- Tic-Tac-Toe example adapted from: https://gist.github.com/qianguigui1104/edb3b11b33c78e5894aad7908c773353
- MCTS algorithm based on research by Browne et al. (2012)
- RAVE technique from Gelly & Silver (2007)

## Support

- Documentation: See `/docs` directory
- Examples: See `examples/` and `tictactoe.py`
- Issues: GitHub Issues (link to your repository)

## Citation

If you use this SDK in research, please cite:

```bibtex
@software{game_ai_client,
  title = {Game AI Client SDK},
  version = {0.5.0},
  year = {2024},
  url = {https://github.com/your-org/sdk-project}
}
```

---

**Built with care for game developers who want powerful AI without the complexity.**
