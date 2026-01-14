"""
Session manager for wa_socket.

Responsibilities:
- Manage multiple WhatsAppSocket instances
- Ensure one socket per session_id
- Start / stop sessions cleanly
"""

from typing import Dict, List

from .client import WhatsAppSocket


class WhatsAppSession:
    """
    Manages multiple WhatsAppSocket sessions.
    """

    def __init__(self):
        self._sessions: Dict[str, WhatsAppSocket] = {}

    # ------------------ public API ------------------

    def start_session(self, session_id: str) -> WhatsAppSocket:
        """
        Start or return an existing WhatsApp session.
        """
        if session_id in self._sessions:
            return self._sessions[session_id]

        socket = WhatsAppSocket(session_id).start()
        self._sessions[session_id] = socket
        return socket

    def stop_session(self, session_id: str):
        """
        Stop and remove a WhatsApp session.
        """
        socket = self._sessions.pop(session_id, None)
        if socket:
            socket.stop()

    def stop_all(self):
        """
        Stop all active sessions.
        """
        for session_id in list(self._sessions.keys()):
            self.stop_session(session_id)

    def list_sessions(self) -> List[str]:
        """
        List all active session IDs.
        """
        return list(self._sessions.keys())
