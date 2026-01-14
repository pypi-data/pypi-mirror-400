import logging
from typing import Dict, List, Optional, Tuple

from streams_network.models import TopicResponse

logger = logging.getLogger(__name__)


def _normalize_topic(topic: str) -> str:
    return topic if topic.startswith("/") else f"/{topic}"


class TopicManager:
    """
    Manages locally shared topics and topics discovered from remote peers.
    """

    def __init__(self) -> None:
        self.shared_topics: Dict[str, List[str]] = {}
        self.discovered_topics: Dict[str, Dict[str, List[str]]] = {}

    def add_shared_topic(self, topic: str, signals: List[str]) -> None:
        topic = _normalize_topic(topic)
        self.shared_topics[topic] = signals
        logger.info(
            "Shared topic registered: %s (%d signals)",
            topic,
            len(signals),
        )

    def has_topic(self, topic: str) -> bool:
        return _normalize_topic(topic) in self.shared_topics

    def get_signals(self, topic: str) -> Optional[List[str]]:
        return self.shared_topics.get(_normalize_topic(topic))

    def store_discovered_topic(
        self,
        peer_id: str,
        topic: str,
        signals: List[str],
    ) -> None:
        topic = _normalize_topic(topic)
        self.discovered_topics.setdefault(peer_id, {})[topic] = signals
        logger.info(
            "Discovered topic %s from peer %s",
            topic,
            peer_id[:12],
        )

    def find_signal(self, signal_name: str) -> Optional[Tuple[str, str]]:
        """
        Returns (peer_id, topic) where the signal is available.
        """
        for peer_id, topics in self.discovered_topics.items():
            for topic, signals in topics.items():
                if signal_name in signals:
                    return peer_id, topic
        return None

    def handle_topic_request(
        self,
        node_id: str,
        request_data: Dict,
    ) -> Optional[TopicResponse]:
        """
        Handles incoming TOPIC_REQUEST messages.

        Returns TopicResponse or None if the request should not be forwarded.
        """
        detail = request_data.get("detail", {})
        topic = detail.get("topic_name", "")
        msg_id = request_data.get("id")
        maxhop = request_data.get("maxhop", 0) - 1

        if maxhop < 0:
            return None

        topic = _normalize_topic(topic)

        if topic in self.shared_topics:
            return TopicResponse(
                topic_name=topic,
                status=True,
                signals=self.shared_topics[topic],
                msg_id=msg_id,
                maxhop=maxhop,
            )

        return TopicResponse(
            topic_name=topic,
            status=False,
            msg_id=msg_id,
            maxhop=maxhop,
        )
