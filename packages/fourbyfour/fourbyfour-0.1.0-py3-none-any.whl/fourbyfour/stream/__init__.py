from ..http import HttpClient
from .topics import Topics
from .types import ConsumeResponse, ProduceResponse, Record, Topic, TopicStats


class Stream:
    """Stream service client."""

    def __init__(self, http: HttpClient):
        self.topics = Topics(http)


__all__ = [
    "Stream",
    "Topics",
    "Topic",
    "ProduceResponse",
    "Record",
    "ConsumeResponse",
    "TopicStats",
]
