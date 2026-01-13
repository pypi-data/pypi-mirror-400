"""
AIdrac - AI-Powered Out-of-Band Management
==========================================

The open alternative to iDRAC, iLO, and IPMI.
Remote system control without network dependency.

TRANSPORT LAYERS:
    ├── DTMF      - Telephone/modem control (697-1477 Hz)
    ├── Ultrasonic - ggwave inaudible data (15+ kHz)
    ├── Audible   - ggwave audible data (~2 kHz)
    ├── Morse     - CW audio or visual
    ├── ntfy      - Push notifications (short range)
    └── I-Poll    - AInternet messaging bridge

CONTROL TARGETS:
    ├── GRUB      - Boot menu selection
    ├── BIOS/UEFI - Firmware settings
    ├── Systemd   - Service control
    ├── Power     - Shutdown/reboot/wake
    └── Custom    - User-defined actions

PHYSICAL AUDIT:
    ├── Braille   - Punchcard generation
    ├── QR Code   - Visual encoding
    └── Barcode   - 1D scanning

UNIX PHILOSOPHY:
    - Do one thing well
    - Text streams as universal interface
    - Composable tools
    - Everything is a file (or pipe)

Usage:
    # CLI tools (pipe-friendly)
    echo "reboot" | aidrac-send --transport dtmf --device /dev/ttyUSB0
    aidrac-listen --transport ultrasonic | aidrac --execute
    aidrac-dtmf --decode < audio.wav
    aidrac-notify "System booted" --topic aidrac-alerts

    # Python API
    from mcp_server_aidrac import AIdrac, DTMF, Ultrasonic

    drac = AIdrac()
    drac.send("boot linux", transport="dtmf")
    drac.listen(transport="ultrasonic", callback=handle_command)

Part of HumoticaOS McMurdo Off-Grid Communication Layer.
One love, one fAmIly!
"""

__version__ = "0.2.0"

from .protocols.dtmf import DTMF, DTMFTone
from .protocols.ultrasonic import Ultrasonic, UltrasonicMode
from .transports.ntfy import Ntfy
from .transports.ipoll_bridge import IPollBridge
from .bridges.sentinel import SentinelBridge, SentinelCommand

__all__ = [
    "__version__",
    "DTMF",
    "DTMFTone",
    "Ultrasonic",
    "UltrasonicMode",
    "Ntfy",
    "IPollBridge",
    "SentinelBridge",
    "SentinelCommand",
]
