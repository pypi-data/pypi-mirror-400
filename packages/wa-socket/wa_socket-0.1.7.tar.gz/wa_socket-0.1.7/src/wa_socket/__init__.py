"""
wa_socket package

Main WhatsApp socket client using Baileys backend.
"""
from .client import WhatsAppSocket
from .session import WhatsAppSession as Session

__version__ = "0.1.5"
__all__ = ["WhatsAppSocket", "Session"]