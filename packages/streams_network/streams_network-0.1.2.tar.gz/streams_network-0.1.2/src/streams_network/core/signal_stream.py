import asyncio
import logging
import time
from typing import Dict, Optional, Set, Callable, Any
import contextlib

from streams_network.models import (
    MessageType,
    SignalRequest,
    SignalResponse,
    SignalData,
    TopicRequest,
    TopicResponse,
    parse_message,
)

from .topic_manager import TopicManager

logger = logging.getLogger(__name__)


class SignalRegistry:
    """
    Registry for signal data sources.
    Allows users to register callbacks that provide signal values.
    """

    def __init__(self):
        # {signal_name: callback_function}
        self._signal_sources: Dict[str, Callable[[], float]] = {}

        # {signal_name: latest_value} - cache for push-based updates
        self._signal_cache: Dict[str, float] = {}

    def register_signal(
        self, signal_name: str, callback: Optional[Callable[[], float]] = None
    ):
        """
        Register a signal with either a callback (pull) or cache (push).

        Args:
            signal_name: Name of the signal
            callback: Optional function that returns the current value

        If callback is None, use push() to update values manually.
        """
        if callback:
            self._signal_sources[signal_name] = callback
            logger.info(f"Registered pull-based signal: {signal_name}")
        else:
            # Push-based signal - initialize cache
            self._signal_cache[signal_name] = 0.0
            logger.info(f"Registered push-based signal: {signal_name}")

    def unregister_signal(self, signal_name: str):
        """Remove a signal from the registry."""
        self._signal_sources.pop(signal_name, None)
        self._signal_cache.pop(signal_name, None)
        logger.info(f"Unregistered signal: {signal_name}")

    def push(self, signal_name: str, value: float):
        """
        Push a new value for a signal (for push-based signals).

        Args:
            signal_name: Name of the signal
            value: New value to cache
        """
        if (
            signal_name not in self._signal_cache
            and signal_name not in self._signal_sources
        ):
            logger.warning(
                f"Signal {signal_name} not registered. Call register_signal() first."
            )
            return

        self._signal_cache[signal_name] = value

    def get_value(self, signal_name: str) -> Optional[float]:
        """
        Get current value of a signal.

        Returns:
            Current value or None if signal doesn't exist
        """
        # Try callback first (pull-based)
        if signal_name in self._signal_sources:
            try:
                return self._signal_sources[signal_name]()
            except Exception as e:
                logger.error(f"Error getting value for {signal_name}: {e}")
                return None

        # Fall back to cache (push-based)
        if signal_name in self._signal_cache:
            return self._signal_cache[signal_name]

        return None

    def list_signals(self) -> list[str]:
        """Get list of all registered signals."""
        return list(set(self._signal_sources.keys()) | set(self._signal_cache.keys()))


class SignalStream:
    """
    Manages signal discovery and streaming between peers.
    """

    def __init__(self, network, topic_manager: TopicManager) -> None:
        self.network = network
        self.topic_manager = topic_manager

        # Signal registry for user data
        self.registry = SignalRegistry()

        # {peer_id: {topic: {signal_name}}}
        self.active_streams: Dict[str, Dict[str, Set[str]]] = {}

        # {peer_id: asyncio.Task}
        self.stream_tasks: Dict[str, asyncio.Task] = {}

        # Callbacks for incoming stream data
        self._data_callbacks: list[Callable[[str, SignalData], None]] = []

    # ------------------------------------------------------------------
    # Signal Registry API (for users)
    # ------------------------------------------------------------------

    def register_signal(
        self, signal_name: str, callback: Optional[Callable[[], float]] = None
    ):
        """
        Register a signal for streaming.

        Example (pull-based):
            def get_voltage():
                return sensor.read_voltage()
            signal_stream.register_signal("Voltage", get_voltage)

        Example (push-based):
            signal_stream.register_signal("Temperature")
            # Later, when data arrives:
            signal_stream.push_value("Temperature", 25.3)
        """
        self.registry.register_signal(signal_name, callback)

    def push_value(self, signal_name: str, value: float):
        """
        Push a new value for a signal (for push-based updates).

        Args:
            signal_name: Name of the signal
            value: New value
        """
        self.registry.push(signal_name, value)

    def unregister_signal(self, signal_name: str):
        """Remove a signal from the registry."""
        self.registry.unregister_signal(signal_name)

    def on_data_received(self, callback: Callable[[str, SignalData], None]):
        """
        Register a callback for incoming stream data.

        Args:
            callback: Function that takes (peer_id, SignalData)

        Example:
            def handle_data(peer_id, data):
                print(f"{data.key}: {data.value}")

            signal_stream.on_data_received(handle_data)
        """
        self._data_callbacks.append(callback)

    def remove_data_callback(self, callback: Callable[[str, SignalData], None]):
        """Remove a data callback."""
        if callback in self._data_callbacks:
            self._data_callbacks.remove(callback)

    # ------------------------------------------------------------------
    # Incoming control-plane handling
    # ------------------------------------------------------------------

    def handle_signal_request(
        self,
        node_id: str,
        request_data: Dict,
    ) -> Optional[SignalResponse]:
        detail = request_data.get("detail", {})
        topic = detail.get("topic", "")
        signal = detail.get("signal", "")
        msg_id = request_data.get("id")
        maxhop = request_data.get("maxhop", 0) - 1

        if maxhop < 0:
            return None

        # Check if we have this signal in our registry
        available_signals = self.topic_manager.get_signals(topic)
        registered_signals = self.registry.list_signals()

        if not available_signals or signal not in available_signals:
            return SignalResponse(
                topic=topic,
                signal=signal,
                status=False,
                msg_id=msg_id,
                maxhop=maxhop,
            )

        # Also verify signal is actually registered with data
        if signal not in registered_signals:
            logger.warning(
                f"Signal {signal} in topic {topic} but not registered in registry"
            )
            return SignalResponse(
                topic=topic,
                signal=signal,
                status=False,
                msg_id=msg_id,
                maxhop=maxhop,
            )

        peer_topics = self.active_streams.setdefault(node_id, {})
        peer_topics.setdefault(topic, set()).add(signal)

        if node_id not in self.stream_tasks:
            self.stream_tasks[node_id] = asyncio.create_task(self._stream_loop(node_id))

        return SignalResponse(
            topic=topic,
            signal=signal,
            status=True,
            msg_id=msg_id,
            maxhop=maxhop,
        )

    # ------------------------------------------------------------------
    # Streaming loop
    # ------------------------------------------------------------------

    async def _stream_loop(self, peer_id: str) -> None:
        try:
            await self.network.start_stream(peer_id)
            logger.info("Stream started to peer %s", peer_id[:12])

            while peer_id in self.active_streams:
                topics = self.active_streams.get(peer_id, {})
                for signals in topics.values():
                    for signal in list(signals):
                        # Get value from registry
                        value = self.registry.get_value(signal)

                        if value is None:
                            logger.debug(f"No value for signal {signal}, skipping")
                            continue

                        data = SignalData(
                            key=signal,
                            value=value,
                            time=time.time(),
                        )

                        # Convert to bytes
                        payload = data.to_bytes()

                        # Add length prefix (2 bytes, big-endian)
                        frame = len(payload).to_bytes(2, "big") + payload

                        # Send framed message
                        await self.network.send_stream_message(
                            peer_id,
                            frame,
                        )

                await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            pass
        except Exception as exc:
            logger.error(
                "Stream error to peer %s: %s",
                peer_id[:12],
                exc,
            )
        finally:
            await self._cleanup_stream(peer_id)

    async def _cleanup_stream(self, peer_id: str) -> None:
        task = self.stream_tasks.pop(peer_id, None)
        if task:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task

        self.active_streams.pop(peer_id, None)

        try:
            await self.network.close_stream(peer_id)
        except Exception:
            pass

        logger.info("Stream cleaned up for peer %s", peer_id[:12])

    # ------------------------------------------------------------------
    # Incoming data handling
    # ------------------------------------------------------------------

    def handle_stream_data(self, peer_id: str, data: SignalData):
        """
        Handle incoming stream data and notify callbacks.

        Args:
            peer_id: Source peer ID
            data: Parsed SignalData
        """
        for callback in self._data_callbacks:
            try:
                callback(peer_id, data)
            except Exception as e:
                logger.error(f"Error in data callback: {e}")

    # ------------------------------------------------------------------
    # Outgoing control-plane requests
    # ------------------------------------------------------------------

    async def request_topic(
        self,
        peer_id: str,
        topic: str,
        timeout: float = 10.0,
    ) -> Optional[TopicResponse]:
        request = TopicRequest(topic_name=topic)
        response_queue = asyncio.Queue()
        self.network.handler.on_message_queues.append(response_queue)

        try:
            await self.network.send(
                peer_id,
                request.to_json(self.network.boot.config.get_peer_id()).encode(),
            )

            loop = asyncio.get_running_loop()
            deadline = loop.time() + timeout

            while loop.time() < deadline:
                try:
                    node_id, data = await asyncio.wait_for(
                        response_queue.get(),
                        timeout=1.0,
                    )
                except asyncio.TimeoutError:
                    continue

                msg = parse_message(data)
                if not msg:
                    continue

                if (
                    node_id == peer_id
                    and msg.get("id") == request.msg_id
                    and msg.get("type") == MessageType.TOPIC_RESPONSE.value
                ):
                    detail = msg.get("detail", {})
                    response = TopicResponse(
                        topic_name=detail.get("topic_name", topic),
                        status=detail.get("status", False),
                        signals=detail.get("signals"),
                        msg_id=msg.get("id"),
                        maxhop=msg.get("maxhop", 0),
                    )

                    if response.status and response.signals:
                        self.topic_manager.store_discovered_topic(
                            peer_id,
                            response.topic_name,
                            response.signals,
                        )

                    return response

            return None

        finally:
            self.network.handler.on_message_queues.remove(response_queue)

    async def request_signal(
        self,
        signal_name: str,
        timeout: float = 10.0,
    ) -> bool:
        location = self.topic_manager.find_signal(signal_name)
        if not location:
            return False

        peer_id, topic = location
        request = SignalRequest(topic=topic, signal=signal_name)

        response_queue = asyncio.Queue()
        self.network.handler.on_message_queues.append(response_queue)

        try:
            await self.network.send(
                peer_id,
                request.to_json(self.network.boot.config.get_peer_id()).encode(),
            )

            loop = asyncio.get_running_loop()
            deadline = loop.time() + timeout

            while loop.time() < deadline:
                try:
                    node_id, data = await asyncio.wait_for(
                        response_queue.get(),
                        timeout=1.0,
                    )
                except asyncio.TimeoutError:
                    continue

                msg = parse_message(data)
                if not msg:
                    continue

                if (
                    node_id == peer_id
                    and msg.get("id") == request.msg_id
                    and msg.get("type") == MessageType.SIGNAL_RESPONSE.value
                ):
                    return msg.get("detail", {}).get("status", False)

            return False

        finally:
            self.network.handler.on_message_queues.remove(response_queue)

    async def stop_all_streams(self) -> None:
        for peer_id in list(self.stream_tasks):
            await self._cleanup_stream(peer_id)
