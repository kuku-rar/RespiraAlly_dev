"""
Chat Session Domain Model

Pure Python data class representing a chat session in the AI worker domain.
Contains business logic for session management, memory handling, and conversation flow.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum
import hashlib
import json


class SessionStatus(Enum):
    ACTIVE = "active"
    IDLE = "idle"
    FINALIZED = "finalized"


class MessageType(Enum):
    TEXT = "text"
    AUDIO = "audio"
    SYSTEM = "system"


@dataclass
class ChatMessage:
    """Individual chat message within a session"""
    message_id: str
    user_id: str
    content: str
    message_type: MessageType
    timestamp: datetime
    audio_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_recent(self, minutes: int = 5) -> bool:
        """Check if message was sent within the last N minutes"""
        return datetime.utcnow() - self.timestamp < timedelta(minutes=minutes)

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            "message_id": self.message_id,
            "user_id": self.user_id,
            "content": self.content,
            "message_type": self.message_type.value,
            "timestamp": self.timestamp.isoformat(),
            "audio_id": self.audio_id,
            "metadata": self.metadata
        }


@dataclass
class UserProfile:
    """User profile information for personalized responses"""
    user_id: str
    line_user_id: Optional[str] = None
    personal_background: Dict[str, Any] = field(default_factory=dict)
    health_status: Dict[str, Any] = field(default_factory=dict)
    life_events: Dict[str, Any] = field(default_factory=dict)
    last_contact_ts: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def update_contact_time(self) -> None:
        """Update last contact timestamp"""
        self.last_contact_ts = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def get_personalization_context(self) -> str:
        """Get context string for AI personalization"""
        context_parts = []

        if self.personal_background:
            context_parts.append(f"Personal: {json.dumps(self.personal_background, ensure_ascii=False)}")

        if self.health_status:
            context_parts.append(f"Health: {json.dumps(self.health_status, ensure_ascii=False)}")

        if self.life_events:
            context_parts.append(f"Events: {json.dumps(self.life_events, ensure_ascii=False)}")

        return "; ".join(context_parts) if context_parts else ""

    def has_health_concerns(self) -> bool:
        """Check if user has recorded health concerns"""
        return bool(self.health_status and
                   any(concern in str(self.health_status).lower()
                       for concern in ['pain', 'difficulty', 'problem', 'concern', '疼痛', '困難', '問題']))

    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary"""
        return {
            "user_id": self.user_id,
            "line_user_id": self.line_user_id,
            "personal_background": self.personal_background,
            "health_status": self.health_status,
            "life_events": self.life_events,
            "last_contact_ts": self.last_contact_ts.isoformat() if self.last_contact_ts else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


@dataclass
class ChatSession:
    """Chat session domain object with business logic"""
    session_id: str
    user_id: str
    status: SessionStatus = SessionStatus.ACTIVE
    messages: List[ChatMessage] = field(default_factory=list)
    user_profile: Optional[UserProfile] = None
    last_activity: datetime = field(default_factory=datetime.utcnow)
    created_at: datetime = field(default_factory=datetime.utcnow)
    finalized_at: Optional[datetime] = None
    session_metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create_new_session(cls, user_id: str, line_user_id: Optional[str] = None) -> 'ChatSession':
        """Create a new chat session for a user"""
        session_id = cls._generate_session_id(user_id)

        return cls(
            session_id=session_id,
            user_id=user_id,
            user_profile=UserProfile(user_id=user_id, line_user_id=line_user_id)
        )

    @staticmethod
    def _generate_session_id(user_id: str) -> str:
        """Generate unique session ID"""
        timestamp = datetime.utcnow().isoformat()
        content = f"{user_id}_{timestamp}"
        return hashlib.md5(content.encode()).hexdigest()[:16]

    def add_message(self, content: str, message_type: MessageType, audio_id: Optional[str] = None) -> ChatMessage:
        """Add a new message to the session"""
        message_id = self._generate_message_id(content)

        message = ChatMessage(
            message_id=message_id,
            user_id=self.user_id,
            content=content,
            message_type=message_type,
            timestamp=datetime.utcnow(),
            audio_id=audio_id
        )

        self.messages.append(message)
        self.update_activity()

        return message

    def _generate_message_id(self, content: str) -> str:
        """Generate unique message ID"""
        timestamp = datetime.utcnow().isoformat()
        hash_content = f"{self.user_id}_{content}_{timestamp}"
        return hashlib.md5(hash_content.encode()).hexdigest()[:12]

    def update_activity(self) -> None:
        """Update last activity timestamp"""
        self.last_activity = datetime.utcnow()
        if self.status == SessionStatus.FINALIZED:
            self.status = SessionStatus.ACTIVE

    def is_idle(self, idle_threshold_minutes: int = 5) -> bool:
        """Check if session has been idle for specified minutes"""
        if self.status == SessionStatus.FINALIZED:
            return True

        idle_time = datetime.utcnow() - self.last_activity
        return idle_time > timedelta(minutes=idle_threshold_minutes)

    def should_finalize(self, finalize_threshold_minutes: int = 5) -> bool:
        """Check if session should be finalized due to inactivity"""
        return self.status == SessionStatus.ACTIVE and self.is_idle(finalize_threshold_minutes)

    def finalize_session(self) -> None:
        """Mark session as finalized"""
        self.status = SessionStatus.FINALIZED
        self.finalized_at = datetime.utcnow()

    def get_recent_messages(self, limit: int = 10) -> List[ChatMessage]:
        """Get recent messages for context"""
        return self.messages[-limit:] if self.messages else []

    def get_conversation_context(self, max_chars: int = 2000) -> str:
        """Get conversation context for AI, respecting character limits"""
        recent_messages = self.get_recent_messages()

        context_parts = []
        total_chars = 0

        # Add user profile context if available
        if self.user_profile:
            profile_context = self.user_profile.get_personalization_context()
            if profile_context:
                context_header = f"User Profile: {profile_context}\n\nConversation:\n"
                if len(context_header) < max_chars:
                    context_parts.append(context_header)
                    total_chars += len(context_header)

        # Add recent messages
        for message in reversed(recent_messages):
            message_text = f"[{message.timestamp.strftime('%H:%M')}] User: {message.content}\n"
            if total_chars + len(message_text) > max_chars:
                break
            context_parts.insert(-1 if context_parts else 0, message_text)
            total_chars += len(message_text)

        return "".join(context_parts)

    def calculate_session_metrics(self) -> Dict[str, Any]:
        """Calculate session engagement metrics"""
        if not self.messages:
            return {
                "message_count": 0,
                "session_duration_minutes": 0,
                "avg_message_length": 0,
                "has_audio_messages": False
            }

        session_duration = (self.last_activity - self.created_at).total_seconds() / 60
        message_lengths = [len(msg.content) for msg in self.messages]
        avg_message_length = sum(message_lengths) / len(message_lengths) if message_lengths else 0
        has_audio = any(msg.message_type == MessageType.AUDIO for msg in self.messages)

        return {
            "message_count": len(self.messages),
            "session_duration_minutes": round(session_duration, 2),
            "avg_message_length": round(avg_message_length, 1),
            "has_audio_messages": has_audio,
            "last_activity": self.last_activity.isoformat()
        }

    def needs_health_followup(self) -> bool:
        """Determine if session indicates need for health follow-up"""
        if not self.user_profile or not self.messages:
            return False

        # Check for health concerns in profile
        if self.user_profile.has_health_concerns():
            return True

        # Check for health-related keywords in recent messages
        health_keywords = ['pain', 'hurt', 'sick', 'tired', 'problem', 'difficult',
                          '疼痛', '不舒服', '生病', '累', '問題', '困難']

        recent_content = " ".join([msg.content.lower() for msg in self.get_recent_messages(5)])
        return any(keyword in recent_content for keyword in health_keywords)

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "status": self.status.value,
            "message_count": len(self.messages),
            "messages": [msg.to_dict() for msg in self.messages],
            "user_profile": self.user_profile.to_dict() if self.user_profile else None,
            "last_activity": self.last_activity.isoformat(),
            "created_at": self.created_at.isoformat(),
            "finalized_at": self.finalized_at.isoformat() if self.finalized_at else None,
            "session_metadata": self.session_metadata,
            "metrics": self.calculate_session_metrics()
        }