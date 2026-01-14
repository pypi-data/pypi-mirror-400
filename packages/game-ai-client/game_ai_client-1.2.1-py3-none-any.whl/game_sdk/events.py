"""
Event models for the gaming platform.

This module defines typed event models for communication between game services
and the platform. Events follow the platform's standardized format with:
- eventPit: ISO_LOCAL_DATE_TIME timestamp (no timezone offset)
- Strongly typed fields
- UUID support for lobby/session IDs
- JSON serialization compatible with Java backend
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import UUID
from enum import Enum
import json


class EventCatalog(str, Enum):
    """
    Event catalog types for platform events.

    This enum defines the different types of platform events that can be emitted.
    Inherits from str to ensure proper JSON serialization.
    """
    ACHIEVEMENT_UNLOCKED = "ACHIEVEMENT_UNLOCKED"


@dataclass
class DomainEvent:
    """
    Base class for all platform events.

    All events include an eventPit (timestamp) that represents when the event occurred.
    This matches the platform's Java DomainEvent structure and uses ISO_LOCAL_DATE_TIME
    formatting (no timezone offset) for compatibility with Java LocalDateTime.
    """
    event_pit: str

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert event to dictionary for serialization.

        Handles UUID conversion to string format and snake_case to camelCase conversion.
        """
        data = asdict(self)
        # Convert snake_case keys to camelCase and handle UUID conversion
        camel_data = {}
        for key, value in data.items():
            # Convert snake_case to camelCase
            camel_key = _snake_to_camel(key)

            # Convert UUIDs to strings
            if isinstance(value, UUID):
                camel_data[camel_key] = str(value)
            else:
                camel_data[camel_key] = value

        return camel_data

    def to_json(self) -> str:
        """Serialize event to JSON string."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DomainEvent":
        """
        Create event instance from dictionary.

        Handles UUID parsing from string format and camelCase to snake_case conversion.
        """
        # Convert camelCase keys to snake_case
        converted_data = {}
        for key, value in data.items():
            # Convert camelCase to snake_case
            snake_key = ''.join(['_' + c.lower() if c.isupper() else c for c in key]).lstrip('_')

            # Parse UUIDs from strings
            if snake_key.endswith("_id") and isinstance(value, str):
                try:
                    converted_data[snake_key] = UUID(value)
                except (ValueError, AttributeError):
                    converted_data[snake_key] = value  # Keep as string if not a valid UUID
            else:
                converted_data[snake_key] = value

        return cls(**converted_data)

    @classmethod
    def from_json(cls, json_str: str) -> "DomainEvent":
        """Deserialize event from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)


# ============================================================================
# OUTGOING EVENTS (Game → Platform)
# ============================================================================

@dataclass
class GameStartedEvent(DomainEvent):
    """
    Event published when a game session starts.

    Sent by game services to notify the platform that a match has begun.
    The platform uses this to track active sessions and update lobby state.

    Routing:
        Queue: game.started
        Routing Key: sdk.game.started.v1

    Attributes:
        sessionId: Unique identifier for the game session
        lobbyId: UUID of the lobby that created this session
        gameId: Identifier for the game type (e.g., "tic-tac-toe")
        playerIds: List of player IDs participating in the session
        mode: Game mode ("PvP" or "PvE")
        eventPit: ISO timestamp when the game started
    """
    session_id: str
    lobby_id: UUID
    # game_id: str
    # player_ids: list[str]
    # mode: str  # "PvP" or "PvE"


@dataclass
class GameEndedEvent(DomainEvent):
    """
    Event published when a game session ends.

    Sent by game services to notify the platform of match results.
    The platform uses this for:
    - Updating player statistics
    - Closing the session
    - Triggering post-game workflows (rewards, rankings, etc.)

    Routing:
        Queue: game.ended
        Routing Key: sdk.game.ended.v1

    Attributes:
        sessionId: Unique identifier for the game session
        results: List of player results (playerId and result: WIN/LOSS/DRAW)
        lobbyId: UUID of the lobby that created this session
        eventPit: ISO timestamp when the game ended
    """
    session_id: str
    results: list[Dict[str, str]]  # List of {"playerId": str, "result": "WIN"|"LOSS"|"DRAW"}
    lobby_id: UUID


@dataclass
class AchievementUnlockedEvent(DomainEvent):
    """
    Event published when a player unlocks an achievement.

    Sent by game services to notify the platform that a player has achieved
    a specific milestone or goal. The platform uses this for:
    - Tracking player achievements
    - Updating achievement statistics
    - Triggering rewards or notifications

    Package: be.kdg.sillysealplatform.common.events.platform

    Routing:
        Queue: achievement.unlocked
        Routing Key: sdk.achievement.unlocked.v1

    Attributes:
        event_catalog: Event type, always "ACHIEVEMENT_UNLOCKED"
        subject_id: ID of the player/user who unlocked the achievement
        achievement_name: Generic achievement key/code (e.g., "ACH_WIN_10_MATCHES")
        developer_api_key: Game's registered UUID identifier on the platform
        event_pit: ISO timestamp when the achievement was unlocked
    """
    event_catalog: str
    subject_id: str
    achievement_name: str
    developer_api_key: str


# ============================================================================
# INCOMING EVENTS (Platform → Game)
# ============================================================================

@dataclass
class LobbyOfOnePlayerIsReadyToPlayPveEvent(DomainEvent):
    """
    Event received when a PvE (Player vs Environment) lobby is ready.

    Sent by the platform's matchmaking system when a player wants to play
    against AI. The game service should:
    1. Create a new session
    2. Assign the player to a symbol/side
    3. Initialize AI opponent
    4. Publish GameStartedEvent

    Routing:
        Queue: lobby.ready.pve (or game-specific queue)
        Routing Key: platform.lobby.pve.ready.v1

    Attributes:
        lobby_id: UUID of the ready lobby
        player_id: Player ID of the human player
        ai_mode: AI mode/type ("MCTS", "ML_CATBOOST", "ML_XGBOOST", "ML_DECISION_TREE")
        event_pit: ISO timestamp when lobby became ready
    """
    lobby_id: UUID
    player_id: str
    ai_mode: str


@dataclass
class LobbyOfTwoPlayersIsReadyToPlayPvPEvent(DomainEvent):
    """
    Event received when a PvP (Player vs Player) lobby is ready.

    Sent by the platform's matchmaking system when two players are matched.
    The game service should:
    1. Create a new session
    2. Assign players to symbols/sides
    3. Determine starting player
    4. Publish GameStartedEvent

    Routing:
        Queue: lobby.ready.pvp (or game-specific queue)
        Routing Key: platform.lobby.pvp.ready.v1

    Attributes:
        lobbyId: UUID of the ready lobby
        gameId: Identifier for the game type
        player1Id: First player's ID
        player1Name: First player's display name
        player2Id: Second player's ID
        player2Name: Second player's display name
        sessionId: Pre-generated session ID from platform
        eventPit: ISO timestamp when lobby became ready
    """
    lobby_id: UUID
    player1_idp_id: str
    player2_idp_id: str


# ============================================================================
# ML PLAYER EVENTS
# ============================================================================

@dataclass
class MLMoveRequestEvent(DomainEvent):
    """
    Event to request ML move prediction from ML Player Worker.

    Published by game when ML player needs to make a move.

    Routing:
        Exchange: sillyseal.events
        Routing Key: game.ml.move.request.v1
        Queue: ml_move_requests

    Attributes:
        session_id: Game session identifier
        game_state: Current game state with board and turn info
        model_type: ML model to use ("catboost", "xgboost", or "decision_tree")
        event_pit: ISO timestamp when request was made
    """
    session_id: str
    game_state: Dict[str, Any]
    model_type: str = "catboost"


@dataclass
class MLMoveResponseEvent(DomainEvent):
    """
    Event with ML move prediction result from ML Player Worker.

    Published by ML Player Worker after getting prediction from ML API.

    Routing:
        Exchange: sillyseal.events
        Routing Key: game.ml.move.response.v1

    Attributes:
        session_id: Game session identifier
        predicted_move: Predicted cell index (0-8 for tic-tac-toe)
        predicted_position: Predicted position as {"row": int, "col": int}
        probability: Confidence probability (0.0-1.0)
        model_type: ML model that made the prediction
        event_pit: ISO timestamp when response was sent
    """
    session_id: str
    predicted_move: int
    predicted_position: Dict[str, int]
    probability: float
    model_type: str


# ============================================================================
# EVENT UTILITIES
# ============================================================================

def parse_event(json_str: str, event_type: str) -> DomainEvent:
    """
    Parse a JSON event string into the appropriate event class.

    Args:
        json_str: JSON string containing event data
        event_type: Type of event ("game_started", "game_ended", "achievement_unlocked",
                    "lobby_pve_ready", "lobby_pvp_ready", "ml_move_request", "ml_move_response")

    Returns:
        Parsed event instance

    Raises:
        ValueError: If event_type is unknown
    """
    event_map = {
        "game_started": GameStartedEvent,
        "game_ended": GameEndedEvent,
        "achievement_unlocked": AchievementUnlockedEvent,
        "lobby_pve_ready": LobbyOfOnePlayerIsReadyToPlayPveEvent,
        "lobby_pvp_ready": LobbyOfTwoPlayersIsReadyToPlayPvPEvent,
        "ml_move_request": MLMoveRequestEvent,
        "ml_move_response": MLMoveResponseEvent,
    }

    if event_type not in event_map:
        raise ValueError(f"Unknown event type: {event_type}")

    event_class = event_map[event_type]
    return event_class.from_json(json_str)


def create_game_started_event(
    session_id: str,
    lobby_id: UUID,
    game_id: str,
    player_ids: list[str],
    mode: str,
    event_pit: Optional[str] = None
) -> GameStartedEvent:
    """
    Convenience factory for GameStartedEvent.

    Example:
        event = create_game_started_event(
            session_id="session-123",
            lobby_id=UUID("12345678-1234-5678-1234-567812345678"),
            game_id="tic-tac-toe",
            player_ids=["player1", "player2"],
            mode="PvP"
        )
    """
    return GameStartedEvent(
        session_id=session_id,
        lobby_id=lobby_id,
        # gameId=game_id,
        # playerIds=player_ids,
        # mode=mode,
        event_pit=event_pit or _format_event_timestamp()
    )


def create_game_ended_event(
    session_id: str,
    lobby_id: UUID,
    results: list[Dict[str, str]],
    game_id: Optional[str] = None,
    winner_id: Optional[str] = None,
    reason: Optional[str] = None,
    final_state: Optional[Dict[str, Any]] = None,
    event_pit: Optional[str] = None
) -> GameEndedEvent:
    """
    Convenience factory for GameEndedEvent.

    Args:
        session_id: Game session ID
        lobby_id: Lobby UUID
        results: List of player results [{"playerId": str, "result": "WIN"|"LOSS"|"DRAW"}]
        game_id: (Deprecated) Game identifier
        winner_id: (Deprecated) Winner's player ID
        reason: (Deprecated) Game end reason
        final_state: (Deprecated) Final game state
        event_pit: Optional ISO timestamp

    Example:
        event = create_game_ended_event(
            session_id="session-123",
            lobby_id=UUID("12345678-1234-5678-1234-567812345678"),
            results=[
                {"playerId": "player1", "result": "WIN"},
                {"playerId": "player2", "result": "LOSS"}
            ]
        )
    """
    return GameEndedEvent(
        session_id=session_id,
        results=results,
        lobby_id=lobby_id,
        event_pit=event_pit or _format_event_timestamp()
    )


def create_achievement_unlocked_event(
    subject_id: str,
    achievement_name: str,
    developer_api_key: str,
    event_pit: Optional[str] = None
) -> AchievementUnlockedEvent:
    """
    Convenience factory for AchievementUnlockedEvent.

    Args:
        subject_id: ID of the player/user who unlocked the achievement
        achievement_name: Generic achievement key/code (e.g., "ACH_WIN_10_MATCHES")
        developer_api_key: Game's registered UUID identifier on the platform
        event_pit: Optional ISO timestamp (defaults to now)

    Returns:
        AchievementUnlockedEvent instance

    Raises:
        ValueError: If developer_api_key is not a valid UUID string

    Example:
        event = create_achievement_unlocked_event(
            subject_id="player-123",
            achievement_name="ACH_WIN_10_MATCHES",
            developer_api_key="7b1b8a1f-4d2c-4f6b-9d2c-2b3fd8d9a9f1"
        )
    """
    # Validate that developer_api_key is a valid UUID
    try:
        UUID(developer_api_key)
    except (ValueError, AttributeError) as e:
        raise ValueError(
            f"developer_api_key must be a valid UUID string, got: {developer_api_key}"
        ) from e

    return AchievementUnlockedEvent(
        event_catalog=EventCatalog.ACHIEVEMENT_UNLOCKED.value,
        subject_id=subject_id,
        achievement_name=achievement_name,
        developer_api_key=developer_api_key,
        event_pit=event_pit or _format_event_timestamp()
    )


def _snake_to_camel(snake_str: str) -> str:
    """
    Convert snake_case string to camelCase.

    Args:
        snake_str: String in snake_case format

    Returns:
        String in camelCase format

    Example:
        _snake_to_camel("event_pit") -> "eventPit"
        _snake_to_camel("player_id") -> "playerId"
    """
    components = snake_str.split('_')
    # Keep the first component lowercase, capitalize the rest
    return components[0] + ''.join(x.title() for x in components[1:])


def _format_event_timestamp(dt: Optional[datetime] = None) -> str:
    """
    Format event timestamp in a Java LocalDateTime-compatible form.

    Produces an ISO_LOCAL_DATE_TIME string with millisecond precision and no timezone offset.
    """
    dt = dt or datetime.now(timezone.utc)
    utc_without_tz = dt.astimezone(timezone.utc).replace(tzinfo=None)
    return utc_without_tz.isoformat(timespec="milliseconds")
