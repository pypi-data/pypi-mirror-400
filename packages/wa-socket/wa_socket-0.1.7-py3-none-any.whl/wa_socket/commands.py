"""
Command transport layer for wa_socket.

Responsibilities:
- Send JSON commands to Node via stdin
- Track request_id for sync calls
- Provide async and sync command helpers

NO process lifecycle here.
NO stdout parsing here.
"""

import json
import time
import threading
from typing import Dict, Any, Optional


class CommandMixin:
    """
    Mixin that provides command-sending capabilities.

    Requires the host class to have:
    - self.process (subprocess.Popen)
    - self._pending_responses (dict)
    - self._response_lock (threading.Lock)
    """

    # ------------------ async ------------------

    def _send_command(self, payload: Dict[str, Any]) -> bool:
        """
        Send a command asynchronously (fire-and-forget).
        """
        if not self.process or not self.process.stdin:
            raise RuntimeError("Node process is not running")

        try:
            message = json.dumps(payload) + "\n"
            self.process.stdin.write(message)
            self.process.stdin.flush()
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to send command: {e}")

    # ------------------ sync ------------------

    def _send_command_sync(
        self,
        payload: Dict[str, Any],
        timeout: int = 10,
    ) -> Dict[str, Any]:
        """
        Send a command and wait for a response with matching request_id.
        """
        request_id = f"{payload.get('action', 'cmd')}_{int(time.time() * 1000)}"
        payload["request_id"] = request_id

        with self._response_lock:
            self._pending_responses[request_id] = None

        self._send_command(payload)

        start = time.time()
        while time.time() - start < timeout:
            with self._response_lock:
                response = self._pending_responses.get(request_id)
                if response is not None:
                    del self._pending_responses[request_id]
                    return response

            time.sleep(0.05)

        # timeout cleanup
        with self._response_lock:
            self._pending_responses.pop(request_id, None)

        raise TimeoutError(f"Command timed out: {payload.get('action')}")
