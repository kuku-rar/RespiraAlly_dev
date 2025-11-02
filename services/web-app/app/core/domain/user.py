"""
User Domain Model

Pure Python data class representing a User in our domain.
This separates user identity and authentication from database concerns.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum


class UserRole(Enum):
    PATIENT = "patient"
    STAFF = "staff"
    ADMIN = "admin"


@dataclass
class StaffDetails:
    """Staff-specific information"""
    title: Optional[str] = None
    department: Optional[str] = None
    license_number: Optional[str] = None


@dataclass
class User:
    """Core User domain object"""
    user_id: int
    account: Optional[str] = None
    first_name: str = ""
    last_name: str = ""
    email: Optional[str] = None
    phone: Optional[str] = None
    line_user_id: Optional[str] = None
    is_staff: bool = False
    is_admin: bool = False
    staff_details: Optional[StaffDetails] = None
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def full_name(self) -> str:
        """Get user's full name"""
        return f"{self.last_name}{self.first_name}"

    @property
    def primary_role(self) -> UserRole:
        """Get user's primary role"""
        if self.is_admin:
            return UserRole.ADMIN
        elif self.is_staff:
            return UserRole.STAFF
        else:
            return UserRole.PATIENT

    @property
    def roles(self) -> list[UserRole]:
        """Get all roles assigned to this user"""
        roles = [UserRole.PATIENT]  # All users are at least patients

        if self.is_staff:
            roles.append(UserRole.STAFF)

        if self.is_admin:
            roles.append(UserRole.ADMIN)

        return roles

    def can_access_patient_data(self, patient_id: int) -> bool:
        """
        Check if user can access specific patient's data

        Rules:
        - Users can access their own data
        - Staff/Admin can access data for patients they manage
        """
        # Users can always access their own data
        if self.user_id == patient_id:
            return True

        # Staff and admin can access patient data (specific patient assignment
        # would need to be checked at the service layer with actual relationships)
        return self.is_staff or self.is_admin

    def can_manage_users(self) -> bool:
        """Check if user can manage other users"""
        return self.is_admin

    def can_assign_patients(self) -> bool:
        """Check if user can assign patients to therapists"""
        return self.is_admin

    def has_line_integration(self) -> bool:
        """Check if user has LINE integration enabled"""
        return self.line_user_id is not None

    def is_active_today(self) -> bool:
        """Check if user has logged in today"""
        if not self.last_login:
            return False

        today = datetime.now().date()
        return self.last_login.date() == today

    def get_display_name(self) -> str:
        """Get appropriate display name based on user type"""
        if self.is_staff and self.staff_details and self.staff_details.title:
            return f"{self.staff_details.title} {self.full_name}"
        else:
            return self.full_name

    def to_dict(self) -> dict:
        """Convert user to dictionary representation"""
        return {
            "user_id": self.user_id,
            "account": self.account,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "display_name": self.get_display_name(),
            "email": self.email,
            "phone": self.phone,
            "line_user_id": self.line_user_id,
            "is_staff": self.is_staff,
            "is_admin": self.is_admin,
            "primary_role": self.primary_role.value,
            "roles": [role.value for role in self.roles],
            "staff_details": {
                "title": self.staff_details.title,
                "department": self.staff_details.department,
                "license_number": self.staff_details.license_number
            } if self.staff_details else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }