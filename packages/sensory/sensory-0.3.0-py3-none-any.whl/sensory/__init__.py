"""
Sensory - Multi-Sensory AI Communication
=========================================

Alias package for mcp-server-sensory.

pip install sensory

Features:
- Morse code encoding/decoding
- Braille text and punchcard patterns
- SSTV/Robot36 image transmission (coming)
- ggwave ultrasonic audio (coming)

Part of HumoticaOS McMurdo Off-Grid Communication Layer.
"""

try:
    from mcp_server_sensory import *
    from mcp_server_sensory import morse, braille
    from mcp_server_sensory import __version__
except ImportError:
    __version__ = "0.1.0"

__all__ = ["morse", "braille", "__version__"]
