"""
ntfy Transport - Push Notifications for Short-Range Communication
================================================================

ntfy.sh is an open source pub-sub notification service.
Perfect for local network AI communication.

Features:
    - HTTP POST = send notification
    - HTTP GET/SSE = receive notifications
    - Self-hostable
    - No SDK needed, just curl!
    - Works on any device

Usage:
    # Send
    curl -d "reboot" ntfy.sh/aidrac-commands

    # Listen
    curl -s ntfy.sh/aidrac-commands/sse

    # Python
    ntfy = Ntfy(topic="aidrac-commands")
    ntfy.send("reboot")
    for msg in ntfy.listen():
        print(msg)

Part of AIdrac - AI Out-of-Band Management
"""

import httpx
import asyncio
import json
from typing import Optional, Iterator, AsyncIterator, Callable, Dict, Any
from dataclasses import dataclass


@dataclass
class NtfyConfig:
    """Configuration for ntfy transport."""
    server: str = "https://ntfy.sh"          # Public server or self-hosted
    default_topic: str = "aidrac"
    timeout: float = 30.0
    priority: str = "default"                 # min, low, default, high, urgent
    tags: list = None                         # Emoji tags


class NtfyMessage:
    """Received ntfy message."""

    def __init__(self, data: Dict[str, Any]):
        self.id = data.get("id", "")
        self.time = data.get("time", 0)
        self.event = data.get("event", "message")
        self.topic = data.get("topic", "")
        self.message = data.get("message", "")
        self.title = data.get("title", "")
        self.priority = data.get("priority", 3)
        self.tags = data.get("tags", [])
        self.raw = data

    def __str__(self):
        return self.message

    def __repr__(self):
        return f"NtfyMessage(topic={self.topic}, message={self.message[:50]})"


class Ntfy:
    """
    ntfy.sh transport for push notification based communication.

    Can be used for:
    - Short-range AI-to-AI messaging
    - Alert notifications
    - Command distribution
    - Status updates

    Example:
        ntfy = Ntfy(topic="my-aidrac")

        # Send command
        ntfy.send("reboot", title="AIdrac Command", priority="high")

        # Listen for commands
        for msg in ntfy.listen():
            if msg.message == "reboot":
                os.system("reboot")
    """

    def __init__(self, topic: Optional[str] = None, config: Optional[NtfyConfig] = None):
        self.config = config or NtfyConfig()
        self.topic = topic or self.config.default_topic
        self._client = httpx.Client(timeout=self.config.timeout)
        self._async_client: Optional[httpx.AsyncClient] = None

    @property
    def url(self) -> str:
        """Full URL for the topic."""
        return f"{self.config.server}/{self.topic}"

    def send(self, message: str, title: Optional[str] = None,
             priority: Optional[str] = None, tags: Optional[list] = None,
             topic: Optional[str] = None) -> bool:
        """
        Send a notification/command.

        Args:
            message: The message content
            title: Optional title
            priority: min, low, default, high, urgent
            tags: List of emoji tags (e.g., ["warning", "robot"])
            topic: Override default topic

        Returns:
            True if sent successfully
        """
        url = f"{self.config.server}/{topic or self.topic}"

        headers = {}
        if title:
            headers["Title"] = title
        if priority:
            headers["Priority"] = priority
        if tags:
            headers["Tags"] = ",".join(tags)

        try:
            response = self._client.post(url, content=message, headers=headers)
            return response.status_code == 200
        except Exception as e:
            print(f"ntfy send error: {e}")
            return False

    def send_json(self, data: Dict[str, Any], topic: Optional[str] = None) -> bool:
        """
        Send structured JSON data.

        Args:
            data: Dictionary to send as JSON
            topic: Override default topic

        Returns:
            True if sent successfully
        """
        url = f"{self.config.server}/{topic or self.topic}"

        payload = {
            "topic": topic or self.topic,
            "message": json.dumps(data),
            "title": "AIdrac JSON",
            "tags": ["robot", "package"],
        }

        try:
            response = self._client.post(
                self.config.server,
                json=payload
            )
            return response.status_code == 200
        except Exception as e:
            print(f"ntfy send_json error: {e}")
            return False

    def listen(self, since: str = "all") -> Iterator[NtfyMessage]:
        """
        Listen for messages using Server-Sent Events.

        Args:
            since: "all" for all messages, or timestamp

        Yields:
            NtfyMessage objects
        """
        url = f"{self.url}/sse"
        params = {"since": since} if since != "all" else {}

        try:
            with self._client.stream("GET", url, params=params) as response:
                for line in response.iter_lines():
                    if line.startswith("data: "):
                        data = json.loads(line[6:])
                        if data.get("event") == "message":
                            yield NtfyMessage(data)
        except Exception as e:
            print(f"ntfy listen error: {e}")

    async def listen_async(self, callback: Callable[[NtfyMessage], None],
                           since: str = "all") -> None:
        """
        Async listener with callback.

        Args:
            callback: Function to call for each message
            since: Start point for messages
        """
        if not self._async_client:
            self._async_client = httpx.AsyncClient(timeout=None)

        url = f"{self.url}/sse"
        params = {"since": since} if since != "all" else {}

        async with self._async_client.stream("GET", url, params=params) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    if data.get("event") == "message":
                        callback(NtfyMessage(data))

    def poll(self, since: str = "1h") -> list[NtfyMessage]:
        """
        Poll for recent messages (non-blocking).

        Args:
            since: How far back to look (e.g., "1h", "30m", "1d")

        Returns:
            List of messages
        """
        url = f"{self.url}/json"
        params = {"since": since, "poll": "1"}

        try:
            response = self._client.get(url, params=params)
            messages = []
            for line in response.text.strip().split("\n"):
                if line:
                    data = json.loads(line)
                    if data.get("event") == "message":
                        messages.append(NtfyMessage(data))
            return messages
        except Exception as e:
            print(f"ntfy poll error: {e}")
            return []

    def close(self):
        """Close HTTP clients."""
        self._client.close()
        if self._async_client:
            asyncio.get_event_loop().run_until_complete(self._async_client.aclose())

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


# CLI-friendly functions
def send(message: str, topic: str = "aidrac", server: str = "https://ntfy.sh") -> bool:
    """Send a notification."""
    config = NtfyConfig(server=server)
    return Ntfy(topic=topic, config=config).send(message)


def listen(topic: str = "aidrac", server: str = "https://ntfy.sh") -> Iterator[NtfyMessage]:
    """Listen for notifications."""
    config = NtfyConfig(server=server)
    return Ntfy(topic=topic, config=config).listen()


if __name__ == "__main__":
    print("=== ntfy Test ===")
    print(f"Topic URL: https://ntfy.sh/aidrac-test")
    print("Sending test message...")

    ntfy = Ntfy(topic="aidrac-test")
    success = ntfy.send("AIdrac test message", title="Test", tags=["robot"])
    print(f"Sent: {success}")
