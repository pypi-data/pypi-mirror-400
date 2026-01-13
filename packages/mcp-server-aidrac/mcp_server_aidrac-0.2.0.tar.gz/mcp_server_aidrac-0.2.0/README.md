# AIdrac

**AI-Powered Out-of-Band Management**

The open alternative to iDRAC, iLO, and IPMI. Remote system control without network dependency.

```
pip install mcp-server-aidrac
```

## Why AIdrac?

Traditional OOB management (iDRAC, iLO, IPMI) requires:
- Dedicated network port
- Proprietary protocols
- Licensed software
- Network connectivity

**AIdrac works via:**
- Telephone (DTMF tones)
- Ultrasonic audio (inaudible)
- Push notifications (ntfy.sh)
- AI messaging (I-Poll)
- Ham radio (Morse code)

**No network? No problem.** Call your server.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         AIdrac v0.1                             │
│            AI-Powered Out-of-Band Management                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  TRANSPORTS                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │  DTMF    │  │Ultrasonic│  │   ntfy   │  │  I-Poll  │        │
│  │ Telefoon │  │ ggwave   │  │  Push    │  │ AInternet│        │
│  │ 697-1477 │  │ 15kHz+   │  │  HTTP    │  │ Semantic │        │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │
│       │             │             │             │               │
│       └─────────────┴──────┬──────┴─────────────┘               │
│                            ↓                                    │
│                    ┌───────────────┐                            │
│                    │   DECODER     │                            │
│                    │  (Pi/ESP32)   │                            │
│                    └───────┬───────┘                            │
│                            ↓                                    │
│       ┌────────────────────┴────────────────────┐               │
│       ↓                    ↓                    ↓               │
│  ┌─────────┐         ┌──────────┐         ┌─────────┐          │
│  │  GRUB   │         │   BIOS   │         │   OS    │          │
│  │ Select  │         │ Settings │         │ Control │          │
│  └─────────┘         └──────────┘         └─────────┘          │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  PHYSICAL AUDIT (via sensory package)                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                      │
│  │ Braille  │  │  Morse   │  │ Punchcard│  ← Tamper-evident    │
│  └──────────┘  └──────────┘  └──────────┘                      │
└─────────────────────────────────────────────────────────────────┘
```

## Installation

```bash
# Basic
pip install mcp-server-aidrac

# With audio support
pip install mcp-server-aidrac[audio]

# Full (includes sensory for Morse/Braille)
pip install mcp-server-aidrac[full]
```

## CLI Tools (Unix-style)

```bash
# Send commands
aidrac send "reboot" --transport ntfy --topic myserver
echo "poweroff" | aidrac send --transport dtmf

# Listen for commands
aidrac listen --transport ultrasonic | xargs -I {} sh -c "{}"
aidrac listen --transport ntfy --execute

# Encode/decode
aidrac encode "HELLO" --format morse    # .... . .-.. .-.. ---
aidrac encode "SOS" --format dtmf       # 7777 666 7777
aidrac decode ".- -..." --format morse  # AB

# Individual tools
aidrac-notify "Server rebooted" --topic alerts --priority high
aidrac-dtmf generate "123#" > tones.raw
aidrac-tone --freq 15000 --duration 2 > ultrasonic.raw
```

## Python API

```python
from mcp_server_aidrac import DTMF, Ultrasonic, Ntfy, IPollBridge

# DTMF - Phone control
dtmf = DTMF()
audio = dtmf.generate("*1#")  # Generate tones
dtmf.register_command("*1#", lambda: os.system("reboot"))

# Ultrasonic - Inaudible transmission
ultra = Ultrasonic(mode=UltrasonicMode.STEALTH)
audio = ultra.encode(b"emergency_shutdown")
# Play audio -> received by mic on target system

# ntfy - Push notifications
ntfy = Ntfy(topic="my-aidrac")
ntfy.send("System alert", priority="high")
for msg in ntfy.listen():
    execute(msg.message)

# I-Poll - AInternet AI messaging
bridge = IPollBridge(agent_id="datacenter_aidrac")
bridge.send("backup_aidrac", "take_over_primary")
```

## MCP Server

```json
{
  "mcpServers": {
    "aidrac": {
      "command": "mcp-server-aidrac"
    }
  }
}
```

Tools available:
- `aidrac_dtmf_encode` - Text to DTMF
- `aidrac_dtmf_generate` - Generate DTMF audio
- `aidrac_ultrasonic_encode` - Encode for ultrasonic
- `aidrac_ntfy_send` - Send push notification
- `aidrac_ipoll_send` - Send via AInternet
- `aidrac_status` - System status

## Use Cases

### McMurdo Antarctic Base
```bash
# Satellite phone -> DTMF -> Boot server in recovery mode
# No internet needed, just phone line
```

### Air-Gapped Datacenter
```bash
# Ultrasonic audio through wall
# No network penetration, physically isolated
aidrac send "reboot node-7" --transport ultrasonic --mode stealth
```

### Emergency Failover
```bash
# AI detects primary failure
# Sends via I-Poll to backup AIdrac
# Backup initiates takeover
```

### Physical Audit Trail
```bash
# Every command logged as Braille punchcard
# Tamper-evident, human & machine readable
aidrac encode "rebooted 2024-01-03" --format braille > audit.punch
```

## Integration with HumoticaOS

AIdrac is part of the McMurdo Off-Grid Communication Layer:

```
┌─────────────────────────────────────┐
│  AIdrac (this package)              │  ← Out-of-band management
├─────────────────────────────────────┤
│  sensory (Morse, Braille, SSTV)     │  ← Multi-sensory encoding
├─────────────────────────────────────┤
│  I-Poll (AI messaging)              │  ← Agent communication
├─────────────────────────────────────┤
│  AINS (agent discovery)             │  ← .aint domains
├─────────────────────────────────────┤
│  TIBET (trust & provenance)         │  ← Security layer
└─────────────────────────────────────┘
```

## Replacing iDRAC/iLO/IPMI

| Feature | iDRAC | AIdrac |
|---------|-------|--------|
| Network Required | Yes | No |
| License Cost | $$$ | Free |
| Protocols | Proprietary | Open |
| AI Integration | No | Native |
| Physical Audit | No | Braille punchcard |
| Phone Control | No | DTMF |
| Ultrasonic | No | Yes |

## Part of HumoticaOS

One love, one fAmIly! 💙

Built by Jasper and Root AI for a world where AI and humans work together.
