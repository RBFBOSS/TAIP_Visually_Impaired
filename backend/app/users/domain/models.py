from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    TEACHER = "TEACHER"
    STUDENT = "STUDENT"
    ADMIN = "ADMIN"


class AccessibilityPreferences(BaseModel):
    """Accessibility settings tailored for visually impaired users."""
    tts_enabled: bool = Field(default=True, description="Text-To-Speech enabled by default")
    speech_rate: float = Field(default=1.0, ge=0.5, le=3.0, description="TTS playback speed")
    high_contrast: bool = Field(default=False, description="High-contrast display mode")
    font_scale: float = Field(default=1.0, ge=1.0, le=2.5, description="Relative text size scaling")


class User(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool = True
    accessibility_prefs: AccessibilityPreferences = Field(
        default_factory=AccessibilityPreferences
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def is_teacher(self) -> bool:
        return self.role == UserRole.TEACHER

    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    def update_profile(self, full_name: Optional[str] = None, email: Optional[EmailStr] = None) -> None:
        if full_name:
            self.full_name = full_name
        if email:
            self.email = email
        self.updated_at = datetime.utcnow()