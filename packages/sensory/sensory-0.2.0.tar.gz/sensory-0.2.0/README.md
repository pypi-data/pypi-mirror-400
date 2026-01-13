# Sensory

**Multi-Sensory AI Communication** - *"Een 7B model krijgt opeens ogen"*

Alias for [`mcp-server-sensory`](https://pypi.org/project/mcp-server-sensory/).

[![PyPI version](https://badge.fury.io/py/sensory.svg)](https://pypi.org/project/sensory/)

```bash
pip install sensory
```

## Features

- **Morse** - Text to dots/dashes, audio timing, visual patterns
- **Braille** - Unicode braille, punchcard patterns, binary grids
- **SSTV / REFLUX** - Robot36, Scottie, Martin image modes (NEW!)
- **Ponskaart** - McMurdo authentication cards
- **ggwave** - Ultrasonic data transmission (coming)

## REFLUX - The Concept

Give "eyes" to text-only LLMs via audio:

```
Text → Image → SSTV Audio → Radio → Audio → Image → OCR → Text
```

## Quick Start

```python
from sensory import morse, braille, sstv

# Morse
print(morse.encode("SOS"))  # ... --- ...

# Braille
print(braille.encode("hello"))  # ⠓⠑⠇⠇⠕

# SSTV / REFLUX - NEW!
audio = sstv.encode_text("STATUS: OK", mode="robot36")
# Returns WAV bytes for radio transmission

# McMurdo Ponskaart
ponskaart = sstv.encode_ponskaart("user", "token", "REBOOT")
```

Part of HumoticaOS - One love, one fAmIly!
