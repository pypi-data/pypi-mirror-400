"""
Sentinel Bridge - The Mother Module Integration
================================================

Connects AIdrac to Sentinel AI for intelligent hardware management.

Flow:
    User Intent → AiDrac → Sentinel (interpret + validate) → Command → Execute

Sentinel provides:
- Natural language intent → exact command translation
- TIBET compliance checking
- Risk assessment (LOW/MEDIUM/CRITICAL)
- McMurdo fallback encoding
"""

import httpx
from typing import Optional, Dict, Any
import json


class SentinelBridge:
    """Bridge to Sentinel AI - The Mother Module"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_prefix = "/api/sentinel"

    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to Sentinel API"""
        url = f"{self.base_url}{self.api_prefix}{endpoint}"
        try:
            with httpx.Client(timeout=30.0) as client:
                if method == "GET":
                    response = client.get(url)
                else:
                    response = client.post(url, json=data)
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException:
            return {"status": "error", "error": "Sentinel timeout"}
        except httpx.HTTPStatusError as e:
            return {"status": "error", "error": f"HTTP {e.response.status_code}"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def status(self) -> Dict[str, Any]:
        """Check if Sentinel is operational"""
        return self._request("GET", "/status")

    def hardware_command(self, intent: str) -> Dict[str, Any]:
        """
        Translate natural language intent to hardware command.

        Examples:
            "reboot the server" → "sudo systemctl reboot"
            "open port 443" → "sudo ufw allow 443/tcp"
            "check disk health" → "sudo smartctl -H /dev/sda"

        Returns dict with:
            - command: The exact command to run
            - risk_level: LOW/MEDIUM/CRITICAL
            - tibet_required: Whether TIBET audit token is needed
            - explanation: What the command does
        """
        return self._request("POST", "/hardware", {"intent": intent})

    def check_compliance(self, action: str, region: str = "EU") -> Dict[str, Any]:
        """
        Check TIBET compliance for an action before executing.

        Args:
            action: What we're about to do
            region: Regulatory region (EU, Japan, etc.)

        Returns compliance info and any required steps.
        """
        return self._request("POST", "/compliance", {
            "action": action,
            "region": region
        })

    def mcmurdo_encode(self, message: str, method: str = "morse") -> Dict[str, Any]:
        """
        Encode message for McMurdo off-grid transmission.

        Args:
            message: Message to encode
            method: morse, dtmf, braille

        Returns encoded message ready for transmission.
        """
        return self._request("POST", "/mcmurdo", {
            "message": message,
            "method": method
        })

    def query(self, question: str, include_knowledge: bool = True) -> Dict[str, Any]:
        """
        Query Sentinel AI with any question.

        Sentinel has access to:
            - KIT-hardware-instructions
            - KIT-AIdrac protocols
            - KIT-sensory encoding
            - KIT-tibet-compliance
            - KIT-prompt-injection detection
        """
        return self._request("POST", "/query", {
            "question": question,
            "include_knowledge": include_knowledge
        })


class SentinelCommand:
    """
    Represents a validated hardware command from Sentinel.

    Usage:
        bridge = SentinelBridge()
        result = bridge.hardware_command("restart nginx")
        cmd = SentinelCommand.from_response(result)

        if cmd.is_safe:
            os.system(cmd.command)
        elif cmd.needs_tibet:
            # Create TIBET audit token first
            pass
    """

    def __init__(self, command: str, risk_level: str, tibet_required: bool,
                 explanation: str = "", raw_response: str = ""):
        self.command = command
        self.risk_level = risk_level
        self.tibet_required = tibet_required
        self.explanation = explanation
        self.raw_response = raw_response

    @classmethod
    def from_response(cls, response: Dict) -> "SentinelCommand":
        """Parse Sentinel response into SentinelCommand"""
        raw = response.get("response", "")

        # Default values
        command = ""
        risk_level = "UNKNOWN"
        tibet_required = False
        explanation = raw

        # Try to parse structured response
        if "```" in raw:
            # Extract command from code block
            lines = raw.split("```")
            if len(lines) >= 2:
                command = lines[1].strip()
                if command.startswith("bash\n"):
                    command = command[5:]
                elif command.startswith("sh\n"):
                    command = command[3:]

        # Look for risk level
        raw_upper = raw.upper()
        if "CRITICAL" in raw_upper:
            risk_level = "CRITICAL"
            tibet_required = True
        elif "MEDIUM" in raw_upper:
            risk_level = "MEDIUM"
        elif "LOW" in raw_upper:
            risk_level = "LOW"

        return cls(
            command=command,
            risk_level=risk_level,
            tibet_required=tibet_required,
            explanation=explanation,
            raw_response=raw
        )

    @property
    def is_safe(self) -> bool:
        """Command is safe to execute without additional checks"""
        return self.risk_level == "LOW" and not self.tibet_required

    @property
    def needs_tibet(self) -> bool:
        """Command requires TIBET audit token"""
        return self.tibet_required or self.risk_level == "CRITICAL"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "command": self.command,
            "risk_level": self.risk_level,
            "tibet_required": self.tibet_required,
            "explanation": self.explanation,
            "is_safe": self.is_safe
        }


# Quick test
if __name__ == "__main__":
    bridge = SentinelBridge()

    print("=== Sentinel Bridge Test ===\n")

    # Test status
    status = bridge.status()
    print(f"Status: {status.get('status', 'unknown')}")

    # Test hardware command
    result = bridge.hardware_command("check if firewall is enabled")
    print(f"\nHardware command result:")
    print(result.get("response", result.get("error", "No response"))[:300])
