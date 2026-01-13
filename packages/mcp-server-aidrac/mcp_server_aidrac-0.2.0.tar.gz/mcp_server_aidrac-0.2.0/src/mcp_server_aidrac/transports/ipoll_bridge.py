"""
I-Poll Bridge - AInternet Integration for AIdrac
================================================

Connects AIdrac to the AInternet messaging layer.
Allows AI agents to send OOB commands to physical machines.

Usage:
    bridge = IPollBridge(agent_id="aidrac_server1")

    # Send command to another AIdrac
    bridge.send("aidrac_server2", "reboot")

    # Listen for commands
    for cmd in bridge.listen():
        execute(cmd)
"""

import httpx
from typing import Optional, Iterator, Dict, Any
from dataclasses import dataclass


@dataclass
class IPollConfig:
    """I-Poll connection configuration."""
    base_url: str = "https://brein.jaspervandemeent.nl/api/ipoll"
    local_url: str = "http://localhost:8000/api/ipoll"
    use_local: bool = True
    poll_type: str = "PUSH"


class IPollMessage:
    """Message from I-Poll."""

    def __init__(self, data: Dict[str, Any]):
        self.id = data.get("id", "")
        self.from_agent = data.get("from", "")
        self.to_agent = data.get("to", "")
        self.content = data.get("content", "")
        self.poll_type = data.get("type", "PUSH")
        self.created_at = data.get("created_at", "")
        self.raw = data

    def __str__(self):
        return f"{self.from_agent}: {self.content}"


class IPollBridge:
    """
    Bridge between AIdrac and I-Poll (AInternet messaging).

    Enables:
    - AI agents to control physical machines
    - Cross-network OOB management
    - Audit trail via TIBET integration

    Example:
        # Server side
        bridge = IPollBridge(agent_id="datacenter_aidrac")

        for msg in bridge.listen():
            if msg.content == "emergency_shutdown":
                os.system("poweroff")

        # Client side (from any AI)
        bridge = IPollBridge(agent_id="root_ai")
        bridge.send("datacenter_aidrac", "emergency_shutdown")
    """

    def __init__(self, agent_id: str, config: Optional[IPollConfig] = None):
        self.agent_id = agent_id
        self.config = config or IPollConfig()
        self._client = httpx.Client(timeout=30.0)

    @property
    def base_url(self) -> str:
        return self.config.local_url if self.config.use_local else self.config.base_url

    def send(self, to_agent: str, content: str,
             poll_type: str = "PUSH", metadata: Optional[Dict] = None) -> bool:
        """
        Send a command to another AIdrac instance.

        Args:
            to_agent: Target agent ID
            content: Command content
            poll_type: PUSH, PULL, SYNC, TASK
            metadata: Additional metadata

        Returns:
            True if sent successfully
        """
        url = f"{self.base_url}/push"

        payload = {
            "from_agent": self.agent_id,
            "to_agent": to_agent,
            "content": content,
            "poll_type": poll_type,
        }

        if metadata:
            payload["metadata"] = metadata

        try:
            response = self._client.post(url, json=payload)
            return response.status_code == 200
        except Exception as e:
            print(f"I-Poll send error: {e}")
            return False

    def pull(self, mark_read: bool = False) -> list[IPollMessage]:
        """
        Pull pending messages.

        Args:
            mark_read: Whether to mark messages as read

        Returns:
            List of messages
        """
        url = f"{self.base_url}/pull/{self.agent_id}"
        params = {"mark_read": str(mark_read).lower()}

        try:
            response = self._client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return [IPollMessage(p) for p in data.get("polls", [])]
        except Exception as e:
            print(f"I-Poll pull error: {e}")

        return []

    def listen(self, interval: float = 5.0) -> Iterator[IPollMessage]:
        """
        Continuously listen for messages.

        Args:
            interval: Polling interval in seconds

        Yields:
            IPollMessage objects
        """
        import time

        seen_ids = set()

        while True:
            messages = self.pull(mark_read=True)
            for msg in messages:
                if msg.id not in seen_ids:
                    seen_ids.add(msg.id)
                    yield msg

            time.sleep(interval)

    def ack(self, message_id: str, response: str = "ACK") -> bool:
        """
        Acknowledge a received message.

        Args:
            message_id: ID of message to acknowledge
            response: Acknowledgment content

        Returns:
            True if acknowledged
        """
        # Send ACK as new message
        return self.send(
            to_agent=self.agent_id,  # Will be overwritten with original sender
            content=response,
            poll_type="ACK"
        )

    def status(self) -> Dict[str, Any]:
        """Get I-Poll status."""
        url = f"{self.base_url}/status"
        try:
            response = self._client.get(url)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def close(self):
        """Close HTTP client."""
        self._client.close()


# Convenience functions
def send(from_agent: str, to_agent: str, content: str) -> bool:
    """Send a message via I-Poll."""
    return IPollBridge(from_agent).send(to_agent, content)


def pull(agent_id: str) -> list[IPollMessage]:
    """Pull messages for an agent."""
    return IPollBridge(agent_id).pull()


if __name__ == "__main__":
    print("=== I-Poll Bridge Test ===")

    bridge = IPollBridge(agent_id="aidrac_test")
    print(f"Agent: {bridge.agent_id}")
    print(f"Base URL: {bridge.base_url}")

    status = bridge.status()
    print(f"Status: {status}")
