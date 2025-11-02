"""
Chat Mapper

Converts between SQLAlchemy chat profile models and pure domain chat objects.
"""

from typing import Optional
from datetime import datetime
from ..domain.chat_session import UserProfile, ChatSession, ChatMessage, MessageType, SessionStatus
from ..llm_app.models.chat_profile import ChatUserProfile


class ChatMapper:
    """Maps between SQLAlchemy ChatUserProfile and domain objects"""

    @staticmethod
    def profile_to_domain(sql_profile: ChatUserProfile) -> UserProfile:
        """Convert SQLAlchemy ChatUserProfile to domain UserProfile"""
        return UserProfile(
            user_id=str(sql_profile.user_id),
            line_user_id=sql_profile.line_user_id,
            personal_background=sql_profile.profile_personal_background or {},
            health_status=sql_profile.profile_health_status or {},
            life_events=sql_profile.profile_life_events or {},
            last_contact_ts=sql_profile.last_contact_ts,
            created_at=sql_profile.created_at,
            updated_at=sql_profile.updated_at
        )

    @staticmethod
    def profile_to_sql(domain_profile: UserProfile, existing_profile: Optional[ChatUserProfile] = None) -> ChatUserProfile:
        """Convert domain UserProfile to SQLAlchemy ChatUserProfile"""
        if existing_profile:
            profile = existing_profile
        else:
            profile = ChatUserProfile()

        profile.user_id = int(domain_profile.user_id)
        profile.line_user_id = domain_profile.line_user_id
        profile.profile_personal_background = domain_profile.personal_background
        profile.profile_health_status = domain_profile.health_status
        profile.profile_life_events = domain_profile.life_events
        profile.last_contact_ts = domain_profile.last_contact_ts
        profile.updated_at = datetime.utcnow()

        return profile

    @staticmethod
    def task_data_to_domain_session(task_data: dict) -> ChatSession:
        """Convert task data to domain ChatSession"""
        user_id = str(task_data.get('patient_id') or task_data.get('user_id'))
        line_user_id = task_data.get('line_user_id')

        session = ChatSession.create_new_session(user_id, line_user_id)

        # Add initial message if present
        if task_data.get('text'):
            message_type = MessageType.AUDIO if task_data.get('object_name') else MessageType.TEXT
            audio_id = task_data.get('object_name')

            session.add_message(
                content=task_data['text'],
                message_type=message_type,
                audio_id=audio_id
            )

        return session