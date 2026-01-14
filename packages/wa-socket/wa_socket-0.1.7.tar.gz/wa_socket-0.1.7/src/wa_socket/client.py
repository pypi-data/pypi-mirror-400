"""
Main client interface for wa_socket.

Responsibilities:
- Manage Node.js process lifecycle  
"""
import os
import threading
import time
from pathlib import Path
from typing import Optional, Callable, Dict, Any, List

from .process import NodeProcess
from .commands import CommandMixin
from .events import EventReader
from wa_socket.utils import format_jid


class WhatsAppSocket(CommandMixin):
    """
    Main WhatsApp socket interface (Baileys-style).
    """

    def __init__(self, session_id: str = "default", auth_base_dir: Optional[Path] = None):
        self.session_id = session_id

        # -------- paths --------
        if auth_base_dir is None:
            auth_base_dir = Path.home() / ".wa_socket"
        self.auth_dir = auth_base_dir / f"session_{session_id}"

        # -------- process --------
        self.node: Optional[NodeProcess] = None
        self.process = None

        # -------- connection state --------
        self.is_connected = False
        self.is_ready = False
        self.account_info: Optional[Dict[str, Any]] = None
        self.last_qr: Optional[str] = None
        self._qr_callback: Optional[Callable] = None

        # -------- callbacks --------
        self._message_callback: Optional[Callable] = None
        self._connection_callback: Optional[Callable] = None
        self._presence_callback: Optional[Callable] = None
        self._group_participants_callback: Optional[Callable] = None
        self._reaction_callback: Optional[Callable] = None

        # -------- command response tracking --------
        self._pending_responses: Dict[str, Any] = {}
        self._response_lock = threading.Lock()

    
    
    # ================== lifecycle ==================

    def start(self) -> "WhatsAppSocket":
        """
        Start the WhatsApp Node backend and event reader.
        """
        if self.process:
            raise RuntimeError("Socket already started")
        
        # Ensure auth directory exists
        self.auth_dir.mkdir(parents=True, exist_ok=True)
        
        # Start Node backend
        self.node = NodeProcess(self.session_id, self.auth_dir)
        self.process = self.node.start()

        # Start event reader thread
        reader = EventReader(self)

        threading.Thread(
        target=reader.run,
        daemon=True,
        ).start()
        return self

    def stop(self):
        """
        Stop the WhatsApp backend.
        """
        if self.node:
            self.node.stop()

        self.process = None
        self.node = None
        self.is_connected = False
        self.is_ready = False

    def wait_for_connection(self, timeout: int = 120) -> "WhatsAppSocket":
        """
        Block until WhatsApp is connected or timeout occurs.
        """
        start = time.time()
        while not self.is_ready:
            if time.time() - start > timeout:
                raise TimeoutError("WhatsApp connection timeout")
            time.sleep(0.2)
        return self

    # ================== callbacks ==================

    def on_qr(self, callback: Callable[[str], None]) -> "WhatsAppSocket":
        """
        Register QR callback.
        Receives raw QR string.
        """
        self._qr_callback = callback
        return self

    def on_message(self, callback: Callable) -> "WhatsAppSocket":
        self._message_callback = callback
        return self

    def on_connection_update(self, callback: Callable) -> "WhatsAppSocket":
        self._connection_callback = callback
        return self

    def on_presence_update(self, callback: Callable) -> "WhatsAppSocket":
        self._presence_callback = callback
        return self
    
    def on_message_read(self, callback: Callable) -> "WhatsAppSocket":
        """
        Register message read/seen handler
        Like: sock.ev.on('messages.update', handler)
        """
        self._message_read_callback = callback
        return self
    
    def on_reaction(self, callback: Callable) -> "WhatsAppSocket":
        """
        Register reaction handler
        Like: sock.ev.on('messages.reaction', handler)
        """
        self._reaction_callback = callback
        return self
    
    def on_group_participants_update(self, callback: Callable) -> 'WhatsAppSocket':
        """
        Register group participants update handler
        Like: sock.ev.on('group-participants.update', handler)
        """
        self._group_participants_callback = callback
        return self

    # ==================== USER QUERIES ====================

    def on_whatsapp(self, phone: str) -> Dict:
        """
        Check if ID exists on WhatsApp
        Like: sock.onWhatsApp(jid)
        
        Args:
            phone: Phone number to check
            
        Returns:
            {'exists': bool, 'jid': str}
        """
        jid = format_jid(phone)
        response = self._send_command_sync({
            "action": "on_whatsapp",
            "data": {"jid": jid}
        })
        return response
    
    def fetch_status(self, jid: str) -> str:
        """
        Fetch user's WhatsApp status
        Like: sock.fetchStatus(jid)
        
        Args:
            jid: WhatsApp JID
            
        Returns:
            Status text
        """
        response = self._send_command_sync({
            "action": "fetch_status",
            "data": {"jid": jid}
        })
        return response.get('status', '')
    
    def profile_picture_url(self, jid: str, type: str = 'preview') -> Optional[str]:
        """
        Get profile picture URL
        Like: sock.profilePictureUrl(jid, type)
        
        Args:
            jid: WhatsApp JID
            type: 'preview' for low-res, 'image' for high-res
            
        Returns:
            Profile picture URL or None
        """
        response = self._send_command_sync({
            "action": "profile_picture_url",
            "data": {"jid": jid, "type": type}
        })
        return response.get('url')
    
    def get_business_profile(self, jid: str) -> Optional[Dict]:
        """
        Fetch business profile
        Like: sock.getBusinessProfile(jid)
        
        Args:
            jid: WhatsApp JID
            
        Returns:
            {'description': str, 'category': str, ...}
        """
        response = self._send_command_sync({
            "action": "get_business_profile",
            "data": {"jid": jid}
        })
        return response

    # ==================== PROFILE MANAGEMENT ====================

    def update_profile_status(self, status: str):
        """
        Update your profile status
        Like: sock.updateProfileStatus(status)
        
        Args:
            status: New status text
        """
        return self._send_command({
            "action": "update_profile_status",
            "data": {"status": status}
        })
    
    def update_profile_name(self, name: str):
        """
        Update your profile name
        Like: sock.updateProfileName(name)
        
        Args:
            name: New profile name
        """
        return self._send_command({
            "action": "update_profile_name",
            "data": {"name": name}
        })
    
    def update_profile_picture(self, jid: str, image_path: str):
        """
        Update profile picture (yours or group's)
        Like: sock.updateProfilePicture(jid, {url: path})
        
        Args:
            jid: Your JID or group JID
            image_path: Path to image file
        """
        return self._send_command({
            "action": "update_profile_picture",
            "data": {"jid": jid, "image": image_path}
        })
    
    def remove_profile_picture(self, jid: str):
        """
        Remove profile picture
        Like: sock.removeProfilePicture(jid)
        
        Args:
            jid: Your JID or group JID
        """
        return self._send_command({
            "action": "remove_profile_picture",
            "data": {"jid": jid}
        })

    # ================== Messaging ==================
    
    def send_message(self, to: str, text: str):
        """
        Send text message
        Like: sock.sendMessage(jid, {text: message})
        
        Args:
            to: Phone number or JID
            text: Message text
        """
        jid = format_jid(to)
        return self._send_command({
            "action": "send_message",
            "data": {"to": jid, "text": text}
        })
    
    def send_image(self, to: str, image_path: str, caption: str = ""):
        """
        Send image with optional caption
        Like: sock.sendMessage(jid, {image: buffer, caption: text})
        
        Args:
            to: Phone number or JID
            image_path: Path to image
            caption: Optional caption
        """
        jid = format_jid(to)
        return self._send_command({
            "action": "send_image",
            "data": {"to": jid, "image": image_path, "caption": caption}
        })
    
    def send_video(self, to: str, video_path: str, caption: str = ""):
        """
        Send video with optional caption
        
        Args:
            to: Phone number or JID
            video_path: Path to video
            caption: Optional caption
        """
        jid = format_jid(to)
        return self._send_command({
            "action": "send_video",
            "data": {"to": jid, "video": video_path, "caption": caption}
        })
    
    def send_audio(self, to: str, audio_path: str):
        """
        Send audio file
        
        Args:
            to: Phone number or JID
            audio_path: Path to audio file
        """
        jid = format_jid(to)
        return self._send_command({
            "action": "send_audio",
            "data": {"to": jid, "audio": audio_path}
        })
    
    def send_document(self, to: str, document_path: str, filename: str = None):
        """
        Send document
        
        Args:
            to: Phone number or JID
            document_path: Path to document
            filename: Optional filename override
        """
        jid = format_jid(to)
        return self._send_command({
            "action": "send_document",
            "data": {
                "to": jid, 
                "document": document_path,
                "filename": filename or os.path.basename(document_path)
            }
        })
    
    def send_presence_update(self, state: str, to: str = None):
        """
        Send presence update (typing, recording, etc.)
        Like: sock.sendPresenceUpdate(state, jid)
        
        FIXED: Now properly sends typing indicators
        
        Args:
            state: 'composing', 'recording', 'paused', 'available', 'unavailable'
            to: JID to send presence to (required for typing)
        """
        if not to:
            raise ValueError("'to' parameter is required for presence updates")
            
        data = {
            "state": state,
            "to": format_jid(to)
        }
        
        return self._send_command({
            "action": "send_presence_update",
            "data": data
        })
    
    def typing(self, to: str, is_typing: bool = True):
        """
        Show/hide typing indicator
        Convenience method for send_presence_update
        
        FIXED: Now properly sends typing to specific chat
        
        Args:
            to: Phone number or JID
            is_typing: True to show typing, False to hide
        """
        jid = format_jid(to)
        return self.send_presence_update(
            'composing' if is_typing else 'paused',
            jid
        )
    
    def read_messages(self, keys: List[Dict]):
        """
        Mark messages as read
        Like: sock.readMessages(keys)
        
        Args:
            keys: List of message keys [{id, remoteJid, participant}]
        """
        return self._send_command({
            "action": "read_messages",
            "data": {"keys": keys}
        })

    # ==================== GROUP OPERATIONS ====================
    
    def group_metadata(self, jid: str) -> Dict:
        """
        Get group metadata
        Like: sock.groupMetadata(jid)
        
        Args:
            jid: Group JID
            
        Returns:
            Group metadata dict
        """
        response = self._send_command_sync({
            "action": "group_metadata",
            "data": {"jid": jid}
        })
        return response
    
    def group_create(self, subject: str, participants: List[str]) -> Dict:
        """
        Create a new group
        Like: sock.groupCreate(subject, participants)
        
        Args:
            subject: Group name
            participants: List of phone numbers/JIDs
            
        Returns:
            {'id': group_jid, 'subject': name}
        """
        formatted_participants = [format_jid(p) for p in participants]
        response = self._send_command_sync({
            "action": "group_create",
            "data": {"subject": subject, "participants": formatted_participants}
        })
        return response
    
    def group_leave(self, jid: str):
        """
        Leave a group
        Like: sock.groupLeave(jid)
        
        Args:
            jid: Group JID
        """
        return self._send_command({
            "action": "group_leave",
            "data": {"jid": jid}
        })
    
    def group_update_subject(self, jid: str, subject: str):
        """
        Update group subject/name
        Like: sock.groupUpdateSubject(jid, subject)
        
        Args:
            jid: Group JID
            subject: New group name
        """
        return self._send_command({
            "action": "group_update_subject",
            "data": {"jid": jid, "subject": subject}
        })
    
    def group_update_description(self, jid: str, description: str):
        """
        Update group description
        Like: sock.groupUpdateDescription(jid, description)
        
        Args:
            jid: Group JID
            description: New description
        """
        return self._send_command({
            "action": "group_update_description",
            "data": {"jid": jid, "description": description}
        })
    
    def group_participants_update(self, jid: str, participants: List[str], action: str):
        """
        Add/remove/promote/demote group participants
        Like: sock.groupParticipantsUpdate(jid, participants, action)
        
        Args:
            jid: Group JID
            participants: List of phone numbers/JIDs
            action: 'add', 'remove', 'promote', 'demote'
        """
        formatted_participants = [format_jid(p) for p in participants]
        return self._send_command({
            "action": "group_participants_update",
            "data": {
                "jid": jid,
                "participants": formatted_participants,
                "action": action
            }
        })
    
    def group_setting_update(self, jid: str, setting: str):
        """
        Update group settings
        Like: sock.groupSettingUpdate(jid, setting)
        
        Args:
            jid: Group JID
            setting: 'announcement' (only admins) or 'not_announcement' (all members)
        """
        return self._send_command({
            "action": "group_setting_update",
            "data": {"jid": jid, "setting": setting}
        })

    # ==================== HELPER METHODS ====================
    
    def get_chat_jid(self, message: dict) -> str:
        """
        Return the chat JID exactly as WhatsApp uses it
        (may be @lid, @s.whatsapp.net, or @g.us)
    """
        return message.get("chat_jid")

    def get_sender_jid(self, message: dict) -> str:
        """
        Return the sender JID (never guess or rewrite).
            """
        return message.get("sender_jid")

    def get_sender_phone(self, message: dict) -> str:
        """
        Human-readable phone display with proper @lid handling
        """
        return message.get("phone_number", "UNKNOWN")

    def get_message_text(self, message: dict) -> str | None:
        """
        Return text content if this is a text/emoji message.
        """
        if message.get("type") == "text":
            return message.get("text")
        return None

    def get_message_type(self, message: dict) -> str:
        """
        Return semantic message type:
        text, image, video, gif, audio, sticker, document
        """
        return message.get("type", "unknown")

    def is_group_message(self, message: dict) -> bool:
        """
        Check if message is from a group
        """
        return message.get("is_group", False)

    def get_message_id(self, message: dict) -> str:
        """
        Get the message ID
        """
        return message.get("message_id")

    def get_sender_name(self, message: dict) -> str:
        """
        Get the sender's push name
        """
        return message.get("sender_name", "Unknown")

    def get_caption(self, message: dict) -> str | None:
        """
        Get caption for media messages
        """
        return message.get("caption")

    def get_file_name(self, message: dict) -> str | None:
        """
        Get filename for document messages
        """
        return message.get("fileName")

    def get_mime_type(self, message: dict) -> str | None:
        """
        Get MIME type for document messages
        """
        return message.get("mimeType")

    def is_from_me(self, message: dict) -> bool:
        """
        Check if message was sent by you
        """
        return message.get("from_me", False)

    def get_timestamp(self, message: dict) -> int:
        """
        Get message timestamp
        """
        return message.get("timestamp", 0)

    def get_reply_hint(self, message: dict) -> dict:
        """
        Return safe reply targets.
        """
        if self.is_group_message(message):
            return {
            "group": message.get("chat_jid"),
            "sender": message.get("sender_jid")
        }
        return {
            "reply": message.get("chat_jid") }