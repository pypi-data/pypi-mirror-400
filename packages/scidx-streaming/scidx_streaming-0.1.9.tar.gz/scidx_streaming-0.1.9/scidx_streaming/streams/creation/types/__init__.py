"""Type-specific creation helpers."""

from .kafka import KafkaDerivedResult, create_kafka_stream

__all__ = ["KafkaDerivedResult", "create_kafka_stream"]
