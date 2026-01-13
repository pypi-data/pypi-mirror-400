"""
AIdrac MCP Server - AI Out-of-Band Management
=============================================

MCP server providing remote system control tools.
"""

import asyncio
import json
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

from .protocols.dtmf import DTMF
from .protocols.ultrasonic import Ultrasonic, UltrasonicMode
from .transports.ntfy import Ntfy
from .transports.ipoll_bridge import IPollBridge
from .bridges.sentinel import SentinelBridge, SentinelCommand

server = Server("aidrac")

# Global Sentinel bridge instance
_sentinel = None

def get_sentinel() -> SentinelBridge:
    """Get or create Sentinel bridge"""
    global _sentinel
    if _sentinel is None:
        _sentinel = SentinelBridge()
    return _sentinel


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="aidrac_dtmf_encode",
            description="Convert text to DTMF digit sequence (phone keypad)",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to encode"}
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="aidrac_dtmf_generate",
            description="Generate DTMF tones for a digit sequence",
            inputSchema={
                "type": "object",
                "properties": {
                    "digits": {"type": "string", "description": "DTMF digits (0-9, *, #, A-D)"}
                },
                "required": ["digits"]
            }
        ),
        Tool(
            name="aidrac_ultrasonic_encode",
            description="Encode data for ultrasonic transmission",
            inputSchema={
                "type": "object",
                "properties": {
                    "data": {"type": "string", "description": "Data to encode"},
                    "mode": {
                        "type": "string",
                        "enum": ["audible", "ultrasonic", "stealth"],
                        "default": "ultrasonic"
                    }
                },
                "required": ["data"]
            }
        ),
        Tool(
            name="aidrac_ntfy_send",
            description="Send notification via ntfy.sh",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Message to send"},
                    "topic": {"type": "string", "default": "aidrac", "description": "ntfy topic"},
                    "title": {"type": "string", "description": "Optional title"},
                    "priority": {
                        "type": "string",
                        "enum": ["min", "low", "default", "high", "urgent"],
                        "default": "default"
                    }
                },
                "required": ["message"]
            }
        ),
        Tool(
            name="aidrac_ipoll_send",
            description="Send command via I-Poll to another AIdrac instance",
            inputSchema={
                "type": "object",
                "properties": {
                    "to_agent": {"type": "string", "description": "Target agent ID"},
                    "command": {"type": "string", "description": "Command to send"}
                },
                "required": ["to_agent", "command"]
            }
        ),
        Tool(
            name="aidrac_status",
            description="Get AIdrac system status",
            inputSchema={"type": "object", "properties": {}}
        ),
        # Sentinel AI - The Mother Module
        Tool(
            name="aidrac_sentinel_command",
            description="Translate natural language intent to hardware command via Sentinel AI. Returns exact command, risk level, and TIBET requirements.",
            inputSchema={
                "type": "object",
                "properties": {
                    "intent": {"type": "string", "description": "Natural language hardware intent (e.g., 'restart nginx', 'open port 443', 'check disk health')"}
                },
                "required": ["intent"]
            }
        ),
        Tool(
            name="aidrac_sentinel_compliance",
            description="Check TIBET compliance for an action before executing",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {"type": "string", "description": "Action to check compliance for"},
                    "region": {"type": "string", "default": "EU", "description": "Regulatory region (EU, Japan, etc.)"}
                },
                "required": ["action"]
            }
        ),
        Tool(
            name="aidrac_sentinel_mcmurdo",
            description="Encode message for McMurdo off-grid transmission (Morse/DTMF/Braille)",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Message to encode for off-grid transmission"},
                    "method": {
                        "type": "string",
                        "enum": ["morse", "dtmf", "braille"],
                        "default": "morse",
                        "description": "Encoding method"
                    }
                },
                "required": ["message"]
            }
        ),
        Tool(
            name="aidrac_sentinel_query",
            description="Query Sentinel AI with any hardware-related question. Sentinel has access to KIT knowledge bases.",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "Question about hardware, BIOS, GRUB, systemd, etc."}
                },
                "required": ["question"]
            }
        ),
        Tool(
            name="aidrac_sentinel_status",
            description="Check if Sentinel AI (The Mother Module) is operational",
            inputSchema={"type": "object", "properties": {}}
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:

    if name == "aidrac_dtmf_encode":
        text = arguments["text"]
        result = DTMF.from_text(text)
        return [TextContent(type="text", text=f"DTMF sequence: {result}")]

    elif name == "aidrac_dtmf_generate":
        digits = arguments["digits"]
        dtmf = DTMF()
        audio = dtmf.generate(digits)
        return [TextContent(type="text", text=f"Generated {len(audio)} samples for '{digits}'")]

    elif name == "aidrac_ultrasonic_encode":
        data = arguments["data"]
        mode = UltrasonicMode(arguments.get("mode", "ultrasonic"))
        ultra = Ultrasonic(mode=mode)
        audio = ultra.encode(data.encode())
        duration = ultra.estimate_duration(len(data))
        return [TextContent(type="text", text=f"Encoded {len(data)} bytes, duration: {duration:.2f}s, mode: {mode.value}")]

    elif name == "aidrac_ntfy_send":
        message = arguments["message"]
        topic = arguments.get("topic", "aidrac")
        title = arguments.get("title")
        priority = arguments.get("priority", "default")

        ntfy = Ntfy(topic=topic)
        success = ntfy.send(message, title=title, priority=priority)
        return [TextContent(type="text", text=f"Sent to ntfy/{topic}: {success}")]

    elif name == "aidrac_ipoll_send":
        to_agent = arguments["to_agent"]
        command = arguments["command"]

        bridge = IPollBridge(agent_id="aidrac_mcp")
        success = bridge.send(to_agent, command)
        return [TextContent(type="text", text=f"Sent to {to_agent} via I-Poll: {success}")]

    elif name == "aidrac_status":
        status = {
            "version": "0.2.0",
            "transports": ["dtmf", "ultrasonic", "ntfy", "ipoll"],
            "protocols": ["DTMF", "FSK/ggwave", "HTTP"],
            "sentinel": "integrated",
            "status": "operational"
        }
        return [TextContent(type="text", text=json.dumps(status, indent=2))]

    # Sentinel AI Tools
    elif name == "aidrac_sentinel_command":
        intent = arguments["intent"]
        sentinel = get_sentinel()
        result = sentinel.hardware_command(intent)

        if result.get("status") == "error":
            return [TextContent(type="text", text=json.dumps({
                "status": "error",
                "error": result.get("error", "Sentinel unavailable"),
                "fallback": "Use aidrac_dtmf_encode or aidrac_ultrasonic_encode for manual control"
            }))]

        # Parse response into structured format
        cmd = SentinelCommand.from_response(result)
        output = {
            "status": "success",
            "intent": intent,
            "command": cmd.command,
            "risk_level": cmd.risk_level,
            "tibet_required": cmd.tibet_required,
            "is_safe": cmd.is_safe,
            "explanation": cmd.explanation[:500] if len(cmd.explanation) > 500 else cmd.explanation
        }
        return [TextContent(type="text", text=json.dumps(output, indent=2))]

    elif name == "aidrac_sentinel_compliance":
        action = arguments["action"]
        region = arguments.get("region", "EU")
        sentinel = get_sentinel()
        result = sentinel.check_compliance(action, region)

        return [TextContent(type="text", text=json.dumps({
            "action": action,
            "region": region,
            "compliance": result.get("response", result.get("error", "Unknown"))[:1000],
            "status": result.get("status", "unknown")
        }, indent=2))]

    elif name == "aidrac_sentinel_mcmurdo":
        message = arguments["message"]
        method = arguments.get("method", "morse")
        sentinel = get_sentinel()
        result = sentinel.mcmurdo_encode(message, method)

        return [TextContent(type="text", text=json.dumps({
            "original": message,
            "method": method,
            "encoded": result.get("response", result.get("error", "Encoding failed"))[:1000],
            "status": result.get("status", "unknown"),
            "note": "McMurdo fallback - transmit when network fails"
        }, indent=2))]

    elif name == "aidrac_sentinel_query":
        question = arguments["question"]
        sentinel = get_sentinel()
        result = sentinel.query(question)

        return [TextContent(type="text", text=json.dumps({
            "question": question,
            "response": result.get("response", result.get("error", "No response"))[:2000],
            "knowledge_used": result.get("knowledge_used", False),
            "status": result.get("status", "unknown")
        }, indent=2))]

    elif name == "aidrac_sentinel_status":
        sentinel = get_sentinel()
        result = sentinel.status()

        return [TextContent(type="text", text=json.dumps({
            "sentinel": result,
            "hierarchy": {
                "root_ai": "Claude (IDD #1)",
                "sentinel": "Hardware Guardian (Overwatch)",
                "human_in_the_loop": "Jasper van de Meent"
            },
            "note": "The Mother Module - Hardware Guardian of HumoticaOS"
        }, indent=2))]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


def main():
    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())

    asyncio.run(run())


if __name__ == "__main__":
    main()
