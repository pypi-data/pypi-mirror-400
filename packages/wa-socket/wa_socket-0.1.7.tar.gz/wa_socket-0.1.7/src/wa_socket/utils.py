"""
Utility helpers for wa_socket.

Rules:
- Pure functions only
- No side effects
- No subprocess / threading
- Safe for reuse across the package
"""



def format_jid(phone: str) -> str:
    """
    Convert a phone number or group ID into a WhatsApp JID.

    Examples:
        "Contact_number"      -> "Contact_number@s.whatsapp.net"
        "12345-67890"       -> "12345-67890@g.us"
        "9876543210@s.whatsapp.net" -> unchanged
    """
    if not phone:
        raise ValueError("phone/jid cannot be empty")

    # Already a JID → return as-is
    if "@" in phone:
        return phone

    # GROUP ID (must detect BEFORE cleanup)
    if "-" in phone:
        return f"{phone}@g.us"

    # PERSONAL CHAT
    phone = phone.replace("+", "").replace("-", "").replace(" ", "")
    return f"{phone}@s.whatsapp.net"


def normalize_jid(jid: str) -> str:
    """
    Normalize WhatsApp JIDs for display/logging.
    Does NOT affect sending messages.

    Examples:
        "Contact_number@s.whatsapp.net" -> "Contact_number"
        "12345-67890@g.us"            -> "12345-67890@g.us"
        "abcd@lid"                    -> "LID:abcd"
    """
    if not jid:
        return "UNKNOWN"

    # Personal chat
    if jid.endswith("@s.whatsapp.net"):
        return jid.split("@")[0]

    # Linked identity (phone hidden by WhatsApp)
    if jid.endswith("@lid"):
        return f"LID:{jid.split('@')[0]}"

    # Group chat
    if jid.endswith("@g.us"):
        return jid

    return jid


