"""
Event publisher for the gaming platform.

This module handles publishing typed events to RabbitMQ with proper
exchange and routing key configuration compatible with the Java backend.
"""

try:
    import pika
    PIKA_AVAILABLE = True
except ImportError:
    PIKA_AVAILABLE = False
    pika = None

import os
import json
from typing import Optional
from uuid import UUID

from .events import (
    DomainEvent,
    GameStartedEvent,
    GameEndedEvent,
    AchievementUnlockedEvent,
    MLMoveRequestEvent,
    MLMoveResponseEvent,
    MLMoveRequestEvent,
    MLMoveResponseEvent,
)


class EventPublisherConfig:
    """Configuration for event publishing."""

    def __init__(
        self,
        exchange_name: str = "sillyseal.events",
        exchange_type: str = "topic",
        rabbitmq_host: Optional[str] = None,
        rabbitmq_port: Optional[int] = None,
        rabbitmq_user: Optional[str] = None,
        rabbitmq_password: Optional[str] = None,
        developer_api_key: Optional[str] = None,
    ):
        """
        Initialize publisher configuration.

        Args:
            exchange_name: RabbitMQ exchange name (default: "sillyseal.events")
            exchange_type: Exchange type (default: "topic" for routing key patterns)
            rabbitmq_host: RabbitMQ host (default: from env or localhost)
            rabbitmq_port: RabbitMQ port (default: from env or 5672)
            rabbitmq_user: Username (default: from env or "user")
            rabbitmq_password: Password (default: from env or "password")
            developer_api_key: Game's registered UUID on the platform (default: from env or None)

        Raises:
            ValueError: If developer_api_key is provided but not a valid UUID string
        """
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type
        self.host = rabbitmq_host or os.getenv('RABBITMQ_HOST', 'localhost')
        self.port = rabbitmq_port or int(os.getenv('RABBITMQ_PORT', 5672))
        self.user = rabbitmq_user or os.getenv('RABBITMQ_USER', 'user')
        self.password = rabbitmq_password or os.getenv('RABBITMQ_PASSWORD', 'password')
        self.developer_api_key = developer_api_key or os.getenv('DEVELOPER_API_KEY')

        # Validate developer_api_key if provided
        if self.developer_api_key:
            try:
                UUID(self.developer_api_key)
            except (ValueError, AttributeError) as e:
                raise ValueError(
                    f"developer_api_key must be a valid UUID string, got: {self.developer_api_key}"
                ) from e


class EventPublisher:
    """
    Publishes typed events to RabbitMQ with proper routing.

    This publisher:
    - Uses topic exchanges for flexible routing
    - Declares queues and bindings automatically
    - Maps event types to routing keys
    - Handles graceful degradation if RabbitMQ unavailable
    """

    # Routing configuration for outgoing events
    # Each event can optionally specify an "exchange" to override the default
    ROUTING_CONFIG = {
        GameStartedEvent: {
            "queue": "game.started",
            "routing_key": "sdk.game.started.v1"
        },
        GameEndedEvent: {
            "queue": "game.ended",
            "routing_key": "sdk.game.ended.v1"
        },
        AchievementUnlockedEvent: {
            "queue": "achievement.unlocked",
            "routing_key": "platform.achievement.unlocked.v1"
        },
        MLMoveRequestEvent: {
            "queue": "ml_move_requests",
            "routing_key": "game.ml.move.request.v1"
        },
        MLMoveResponseEvent: {
            "queue": "ml_move_responses",
            "routing_key": "game.ml.move.response.v1"
        },
    }

    def __init__(self, config: Optional[EventPublisherConfig] = None):
        """
        Initialize event publisher.

        Args:
            config: Publisher configuration (uses defaults if None)
        """
        self.config = config or EventPublisherConfig()
        self.connection = None
        self.channel = None
        self.connected = False

        if not PIKA_AVAILABLE:
            print("WARNING: pika not available, events will be printed to stdout")
            return

        try:
            self._connect()
            self._setup_infrastructure()
        except Exception as e:
            print(f"WARNING: Failed to connect to RabbitMQ: {e}")
            print("Events will be printed to stdout instead")
            self.connected = False

    def _connect(self):
        """Establish connection to RabbitMQ."""
        credentials = pika.PlainCredentials(self.config.user, self.config.password)
        parameters = pika.ConnectionParameters(
            host=self.config.host,
            port=self.config.port,
            credentials=credentials
        )
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        self.connected = True

    def _setup_infrastructure(self):
        """
        Declare exchange, queues, and bindings.

        This ensures all infrastructure exists before publishing.
        Supports per-event exchange overrides.
        """
        if not self.channel:
            return

        # Collect all unique exchanges from routing config
        exchanges = {self.config.exchange_name}
        for routing in self.ROUTING_CONFIG.values():
            if "exchange" in routing:
                exchanges.add(routing["exchange"])

        # Declare all exchanges
        for exchange in exchanges:
            self.channel.exchange_declare(
                exchange=exchange,
                exchange_type=self.config.exchange_type,
                durable=True
            )

        # Declare queues and bindings for each event type
        for event_class, routing in self.ROUTING_CONFIG.items():
            queue_name = routing["queue"]
            routing_key = routing["routing_key"]
            # Use per-event exchange if specified, otherwise use default
            exchange = routing.get("exchange", self.config.exchange_name)

            # Declare queue
            self.channel.queue_declare(queue=queue_name, durable=True)

            # Bind queue to exchange with routing key
            self.channel.queue_bind(
                exchange=exchange,
                queue=queue_name,
                routing_key=routing_key
            )

    def publish(self, event: DomainEvent):
        """
        Publish a typed event.

        Args:
            event: Event instance to publish

        Raises:
            ValueError: If event type has no routing configuration
        """
        event_class = type(event)

        # Get routing configuration
        if event_class not in self.ROUTING_CONFIG:
            raise ValueError(f"No routing configuration for {event_class.__name__}")

        routing = self.ROUTING_CONFIG[event_class]
        routing_key = routing["routing_key"]
        # Use per-event exchange if specified, otherwise use default
        exchange = routing.get("exchange", self.config.exchange_name)

        # Serialize event
        message_body = event.to_json()

        # Publish to RabbitMQ or fallback to stdout
        if self.connected and self.channel:
            self._publish_to_rabbitmq(exchange, routing_key, message_body)
        else:
            self._print_to_stdout(event_class.__name__, routing_key, message_body)

    def _publish_to_rabbitmq(self, exchange: str, routing_key: str, message_body: str):
        """Publish message to RabbitMQ."""
        self.channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=message_body.encode('utf-8'),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Persistent
                content_type='application/json'
            )
        )
        print(f"✓ Published event to {exchange}: {routing_key}")

    def _print_to_stdout(self, event_name: str, routing_key: str, message_body: str):
        """Fallback: print event to stdout."""
        print(f"\n[EVENT] {event_name}")
        print(f"  Routing Key: {routing_key}")
        print(f"  Body: {message_body}")

    def publish_game_started(
        self,
        session_id: str,
        lobby_id: UUID,
        game_id: str,
        player_ids: list[str],
        mode: str
    ):
        """
        Convenience method to publish GameStartedEvent.

        Args:
            session_id: Game session ID
            lobby_id: Lobby UUID
            game_id: Game identifier
            player_ids: List of player IDs
            mode: "PvP" or "PvE"
        """
        from .events import create_game_started_event

        event = create_game_started_event(
            session_id=session_id,
            lobby_id=lobby_id,
            game_id=game_id,
            player_ids=player_ids,
            mode=mode
        )
        self.publish(event)

    def publish_game_ended(
        self,
        session_id: str,
        lobby_id: UUID,
        results: list[dict],
        game_id: Optional[str] = None,
        winner_id: Optional[str] = None,
        reason: Optional[str] = None,
        final_state: Optional[dict] = None
    ):
        """
        Convenience method to publish GameEndedEvent.

        Args:
            session_id: Game session ID
            lobby_id: Lobby UUID
            results: List of player results [{"playerId": str, "result": "WIN"|"LOSS"|"DRAW"}]
            game_id: (Deprecated) Game identifier
            winner_id: (Deprecated) Winner's player ID (None for draws)
            reason: (Deprecated) "win", "draw", "forfeit", "disconnect"
            final_state: (Deprecated) Optional game state data

        Example:
            publisher.publish_game_ended(
                session_id="session-123",
                lobby_id=UUID("..."),
                results=[
                    {"playerId": "player1", "result": "WIN"},
                    {"playerId": "player2", "result": "LOSS"}
                ]
            )
        """
        from .events import create_game_ended_event

        event = create_game_ended_event(
            session_id=session_id,
            lobby_id=lobby_id,
            results=results,
            game_id=game_id,
            winner_id=winner_id,
            reason=reason,
            final_state=final_state
        )
        self.publish(event)

    def publish_achievement_unlocked(
        self,
        subject_id: str,
        achievement_name: str,
        developer_api_key: Optional[str] = None
    ):
        """
        Convenience method to publish AchievementUnlockedEvent.

        Uses the developer_api_key from config if not explicitly provided.

        Args:
            subject_id: ID of the player/user who unlocked the achievement
            achievement_name: Generic achievement key/code (e.g., "ACH_WIN_10_MATCHES")
            developer_api_key: Optional override for the configured developer API key

        Raises:
            ValueError: If no developer_api_key is configured or provided

        Example:
            publisher.publish_achievement_unlocked(
                subject_id="player-123",
                achievement_name="ACH_WIN_10_MATCHES"
            )
        """
        from .events import create_achievement_unlocked_event

        # Use provided key or fall back to config
        api_key = developer_api_key or self.config.developer_api_key

        if not api_key:
            raise ValueError(
                "developer_api_key must be configured in EventPublisherConfig "
                "or provided as a parameter. You can set it via:\n"
                "  - EventPublisherConfig(developer_api_key='your-uuid')\n"
                "  - Environment variable: DEVELOPER_API_KEY='your-uuid'\n"
                "  - Or pass it directly to this method"
            )

        event = create_achievement_unlocked_event(
            subject_id=subject_id,
            achievement_name=achievement_name,
            developer_api_key=api_key
        )
        self.publish(event)

    def publish_ml_move_request(
        self,
        session_id: str,
        game_state: dict,
        model_type: str = "catboost"
    ):
        """
        Publish ML move request event to request a move from ML Player Worker.

        Args:
            session_id: Game session identifier
            game_state: Current game state with board and turn info
            model_type: ML model to use ("catboost", "xgboost", or "decision_tree")

        Example:
            publisher.publish_ml_move_request(
                session_id="session-123",
                game_state={
                    "board": [[0, 0, 0], [0, 1, 0], [0, 0, 0]],
                    "current_player": 2,
                    "turn": 1
                },
                model_type="catboost"
            )
        """
        from .events import _format_event_timestamp

        event = MLMoveRequestEvent(
            session_id=session_id,
            game_state=game_state,
            model_type=model_type,
            event_pit=_format_event_timestamp()
        )
        self.publish(event)

    def close(self):
        """Close RabbitMQ connection."""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            self.connected = False

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
