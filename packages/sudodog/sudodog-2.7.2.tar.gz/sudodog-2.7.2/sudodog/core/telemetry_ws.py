"""
WebSocket-based telemetry service for sending data to SudoDog backend.

Provides much better performance and scalability compared to HTTP:
- Persistent connection (no handshake overhead)
- Lower latency (5-10ms vs 50-100ms)
- Bi-directional communication
- Automatic reconnection
"""

import asyncio
import websockets
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import time
from queue import Queue, Empty
import threading

logger = logging.getLogger(__name__)


class WebSocketTelemetryService:
    """WebSocket-based service for sending telemetry data to backend"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize WebSocket telemetry service.

        Args:
            config: Configuration dict with api_key and endpoint
        """
        self.config = config
        self.api_key = config.get('api_key', '')
        self.endpoint = config.get('endpoint', 'wss://api.sudodog.com/v1/ws/agent')
        self.enabled = config.get('telemetry_enabled', True)

        # WebSocket connection
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.connected = False
        self.reconnect_delay = 1  # Start with 1 second
        self.max_reconnect_delay = 60  # Max 60 seconds

        # Event queue for buffering when disconnected
        self.event_queue = Queue(maxsize=1000)

        # Background thread for WebSocket connection
        self.ws_thread: Optional[threading.Thread] = None
        self.running = False

        # Stats
        self.events_sent = 0
        self.events_failed = 0
        self.reconnect_count = 0

    def start(self):
        """Start the WebSocket connection in a background thread"""
        if self.running:
            return

        self.running = True
        self.ws_thread = threading.Thread(target=self._run_websocket_loop, daemon=True)
        self.ws_thread.start()
        logger.info("WebSocket telemetry service started")

    def _run_websocket_loop(self):
        """Run the WebSocket event loop in a separate thread"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(self._websocket_handler())
        except Exception as e:
            logger.error(f"WebSocket loop error: {e}")
        finally:
            loop.close()

    async def _websocket_handler(self):
        """Main WebSocket connection handler with auto-reconnect"""
        while self.running:
            try:
                # Build WebSocket URL with API key
                ws_url = f"{self.endpoint}?api_key={self.api_key}"

                async with websockets.connect(
                    ws_url,
                    ping_interval=30,
                    ping_timeout=10,
                    close_timeout=5
                ) as websocket:
                    self.ws = websocket
                    self.connected = True
                    self.reconnect_delay = 1  # Reset reconnect delay on successful connection

                    logger.info("WebSocket telemetry connection established")

                    # Wait for welcome message
                    welcome = await websocket.recv()
                    logger.debug(f"WebSocket welcome: {welcome}")

                    # Process queued events and incoming messages
                    await self._process_events(websocket)

            except websockets.exceptions.ConnectionClosed:
                self.connected = False
                logger.warning("WebSocket connection closed, reconnecting...")
                await self._handle_reconnect()

            except Exception as e:
                self.connected = False
                logger.error(f"WebSocket error: {e}, reconnecting...")
                await self._handle_reconnect()

    async def _handle_reconnect(self):
        """Handle reconnection with exponential backoff"""
        self.reconnect_count += 1

        # Exponential backoff
        await asyncio.sleep(self.reconnect_delay)
        self.reconnect_delay = min(self.reconnect_delay * 2, self.max_reconnect_delay)

        logger.info(f"Attempting reconnect #{self.reconnect_count} (delay: {self.reconnect_delay}s)")

    async def _process_events(self, websocket):
        """Process events from queue and send over WebSocket"""
        try:
            while self.running and self.connected:
                try:
                    # Get event from queue (non-blocking)
                    event = self.event_queue.get(timeout=0.1)

                    # Send event over WebSocket
                    await websocket.send(json.dumps(event))
                    self.events_sent += 1

                    # Optionally wait for ACK
                    # response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    # logger.debug(f"Event ACK: {response}")

                except Empty:
                    # No events in queue, wait a bit
                    await asyncio.sleep(0.01)

                except Exception as e:
                    logger.error(f"Error sending event: {e}")
                    self.events_failed += 1

        except Exception as e:
            logger.error(f"Event processing error: {e}")

    def send(self, data: Dict[str, Any]) -> bool:
        """
        Send telemetry data to backend via WebSocket.

        Args:
            data: Telemetry data to send

        Returns:
            True if queued successfully, False otherwise
        """
        if not self.enabled:
            logger.debug("Telemetry disabled, skipping send")
            return False

        try:
            # Add timestamp if not present
            if 'timestamp' not in data:
                data['timestamp'] = datetime.utcnow().isoformat()

            # Add type field
            if 'type' not in data:
                data['type'] = 'telemetry'

            # Queue the event
            try:
                self.event_queue.put_nowait(data)
                return True
            except:
                # Queue is full, drop oldest event and add new one
                try:
                    self.event_queue.get_nowait()
                    self.event_queue.put_nowait(data)
                    logger.warning("Telemetry queue full, dropped oldest event")
                    return True
                except:
                    logger.error("Failed to queue telemetry event")
                    return False

        except Exception as e:
            logger.error(f"Error sending telemetry: {e}")
            return False

    def send_batch(self, data_list: list) -> bool:
        """
        Send batch of telemetry data.

        Args:
            data_list: List of telemetry data dicts

        Returns:
            True if queued successfully, False otherwise
        """
        if not self.enabled:
            return False

        try:
            batch_event = {
                "type": "batch",
                "events": data_list,
                "timestamp": datetime.utcnow().isoformat()
            }

            self.event_queue.put_nowait(batch_event)
            return True

        except Exception as e:
            logger.error(f"Batch telemetry send failed: {e}")
            return False

    def send_event(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """
        Send a single event.

        Args:
            event_type: Type of event (e.g., 'agent_start', 'agent_stop')
            event_data: Event data

        Returns:
            True if queued successfully
        """
        data = {
            "event_type": event_type,
            "data": event_data,
            "timestamp": datetime.utcnow().isoformat()
        }

        return self.send(data)

    def close(self):
        """Close the WebSocket connection"""
        logger.info("Closing WebSocket telemetry service")
        self.running = False

        # Wait for thread to finish (with timeout)
        if self.ws_thread and self.ws_thread.is_alive():
            self.ws_thread.join(timeout=2)

        # Close WebSocket if still connected
        if self.ws and self.connected:
            try:
                asyncio.run(self.ws.close())
            except:
                pass

        logger.info(f"WebSocket telemetry stats: {self.events_sent} sent, {self.events_failed} failed, {self.reconnect_count} reconnects")

    def get_stats(self) -> Dict[str, Any]:
        """Get telemetry statistics"""
        return {
            "connected": self.connected,
            "events_sent": self.events_sent,
            "events_failed": self.events_failed,
            "reconnect_count": self.reconnect_count,
            "queue_size": self.event_queue.qsize()
        }

    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
        return False
