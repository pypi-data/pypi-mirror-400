# wa-socket

`wa-socket` is a Python library that provides a WhatsApp Web socket interface using a
Node.js backend powered by the Baileys library.

The goal is to let Python developers interact with WhatsApp Web **without writing Node.js code**.

---

## Features

- WhatsApp Web connection via QR code
- Session persistence (scan once, reconnect automatically)
- Python-first API
- Node.js backend managed automatically
- Suitable for scripts, services, and FastAPI apps

---

## Requirements

- **Python 3.11.9**
- **Node.js 22+**

⚠️ **Node.js 18 /20  are not  supported**  
This is due to upstream dependency constraints in Baileys.

Download Node.js 22 from:
https://nodejs.org/en/download

Verify installation:
```bash
node -v
npm -v


## How it works

`wa-socket` runs a lightweight Node.js process internally.

- Python controls everything
- Node.js is only used for WhatsApp Web (Baileys)
- Communication happens via stdin/stdout (JSON events)
- QR codes are rendered directly in the terminal

QR is rendered via Python stdout (PIPE mode). Terminal compatibility may vary by system.


## Quick Start

```python
from wa_socket import WhatsAppSocket

sock = WhatsAppSocket(session_id="default")

sock.on_message(lambda msg: print(msg))
sock.start()
sock.wait_for_connection()

sock.send_message("919XXXXXXXXX", "Hello from Python")
