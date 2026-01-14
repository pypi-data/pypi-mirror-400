"""
Event reader for wa_socket.

Responsibilities:
- Read stdout from Node.js backend
- Parse structured output lines
- Update shared state
- Trigger registered callbacks

NO process lifecycle here.
NO command sending here.
"""

import json
import threading
from typing import Any
import time



class EventReader:
    """
    Reads and processes stdout lines from the Node.js process.
    """

    def __init__(self, socket: Any):
        self.socket = socket

    # ------------------ main loop ------------------

    def run(self):
        while (
        self.socket.process is None
        or self.socket.process.stdout is None
        or self.socket.process.stderr is None
        ):
            time.sleep(0.05)
        def _read_stderr():
            for line in self.socket.process.stderr:
                print(f"[Node STDERR] {line.strip()}")

        threading.Thread(target=_read_stderr, daemon=True).start()

        for raw_line in self.socket.process.stdout:
            line = raw_line.rstrip()
            if not line:
                continue
            self._handle_line(line)

    # ------------------ dispatcher ------------------

    def _handle_line(self, line: str):
        # ---- QR handling ----
        # if line in ("QR_START", "QR_END"):
        #     print(line)
        #     return

        # if self._is_qr_ascii(line):
        #     print(line)
        #     return
        
        #Qr data 
        if line.startswith("QR_DATA:"):
            payload = json.loads(line.split(":", 1)[1])
            self._handle_qr(payload)
            return

        # ---- connection status ----
        if line.startswith("STATUS:"):
            self._handle_status(line)
            return

        # ---- account info ----
        if line.startswith("ACCOUNT_INFO:"):
            payload = json.loads(line.split(":", 1)[1])
            self.socket.account_info = payload
            return

        # ---- new message ----
        if line.startswith("NEW_MESSAGE:"):
            payload = json.loads(line.split(":", 1)[1])
            if self.socket._message_callback:
                self.socket._message_callback(payload)
            return

        # ---- presence update ----
        if line.startswith("PRESENCE_UPDATE:"):
            self._handle_presence_update(line)
            return
        
        if line.startswith("MESSAGE_READ:"):
            payload = json.loads(line.split(":", 1)[1])
            if self.socket._message_read_callback:
                self.socket._message_read_callback(payload)
            return
        

        #reaction handler---
        if line.startswith("MESSAGE_REACTION:"):
            payload = json.loads(line.split(":", 1)[1])
            if self.socket._reaction_callback:
                self.socket._reaction_callback(payload)
            return

        # ---- command response ----
        if line.startswith("COMMAND_RESPONSE:"):
            payload = json.loads(line.split(":", 1)[1])
            self._handle_command_response(payload)
            return

        # ---- command error ----
        if line.startswith("COMMAND_ERROR:"):
            error = json.loads(line.split(":", 1)[1])
            raise RuntimeError(f"Command error from Node: {error}")

    # ------------------ handlers ------------------

    def _handle_qr(self, payload: dict):
        """
        Handle raw QR payload from Node.
        """
     # Store it on socket for user access
        self.socket.last_qr = payload["data"]

    # Optional: user callback later
        if self.socket._qr_callback:
            self.socket._qr_callback(payload["data"])

    def _handle_status(self, line: str):
        status = line.split(":", 1)[1]

        if status == "CONNECTED":
            self.socket.is_connected = True
            self.socket.is_ready = True
            if self.socket._connection_callback:
                self.socket._connection_callback({"connection": "open"})
            return

        if status.startswith("CLOSED"):
            was_connected = self.socket.is_connected
            self.socket.is_connected = False
            self.socket.is_ready = False

            if was_connected and self.socket._connection_callback:
                self.socket._connection_callback({"connection": "close"})
            return

    def _handle_command_response(self, response: dict):
        request_id = response.get("request_id")
        if not request_id:
            return

        with self.socket._response_lock:
            if request_id in self.socket._pending_responses:
                self.socket._pending_responses[request_id] = response.get("data")

    def _handle_presence_update(self, line: str):
        try:
            payload = json.loads(line.split(":", 1)[1])
        except Exception:
            return

        # Forward to user callback only
        if self.socket._presence_callback:
            self.socket._presence_callback(payload)

    # ------------------ helpers ------------------

    def _is_qr_ascii(self, line: str) -> bool:
        return "█" in line or "▄" in line or "▀" in line