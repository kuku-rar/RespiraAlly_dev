"""
Patient Mapper

Converts between SQLAlchemy Patient/User models and pure domain Patient objects.
This creates a clean boundary between persistence and domain logic.
"""

from typing import Optional
from ..domain.patient import Patient, HealthProfile, SmokeStatus, Gender
from ..domain.user import User as DomainUser, StaffDetails
from ...models.models import User as SQLUser, HealthProfile as SQLHealthProfile, StaffDetail as SQLStaffDetail


class PatientMapper:
    """Maps between SQLAlchemy models and Patient domain objects"""

    @staticmethod
    def to_domain(sql_user: SQLUser, sql_health_profile: Optional[SQLHealthProfile] = None) -> Patient:
        """Convert SQLAlchemy User + HealthProfile to domain Patient"""
        if sql_health_profile is None:
            sql_health_profile = sql_user.health_profile

        # Map health profile
        health_profile = None
        if sql_health_profile:
            smoke_status = None
            if sql_health_profile.smoke_status:
                try:
                    smoke_status = SmokeStatus(sql_health_profile.smoke_status)
                except ValueError:
                    smoke_status = None

            health_profile = HealthProfile(
                height_cm=sql_health_profile.height_cm,
                weight_kg=sql_health_profile.weight_kg,
                smoke_status=smoke_status,
                updated_at=sql_health_profile.updated_at
            )

        # Map gender
        gender = None
        if sql_user.gender:
            try:
                gender = Gender(sql_user.gender)
            except ValueError:
                gender = None

        # Get therapist ID from health profile
        therapist_id = sql_health_profile.staff_id if sql_health_profile else None

        return Patient(
            user_id=sql_user.id,
            first_name=sql_user.first_name or "",
            last_name=sql_user.last_name or "",
            gender=gender,
            email=sql_user.email,
            phone=sql_user.phone,
            line_user_id=sql_user.line_user_id,
            health_profile=health_profile,
            therapist_id=therapist_id,
            last_login=sql_user.last_login,
            created_at=sql_user.created_at
        )

    @staticmethod
    def to_sql_health_profile(patient: Patient, existing_profile: Optional[SQLHealthProfile] = None) -> SQLHealthProfile:
        """Convert domain Patient's health profile to SQLAlchemy HealthProfile"""
        if existing_profile:
            profile = existing_profile
        else:
            profile = SQLHealthProfile(user_id=patient.user_id)

        if patient.health_profile:
            profile.height_cm = patient.health_profile.height_cm
            profile.weight_kg = patient.health_profile.weight_kg
            profile.smoke_status = patient.health_profile.smoke_status.value if patient.health_profile.smoke_status else None
            profile.staff_id = patient.therapist_id

        return profile

    @staticmethod
    def update_sql_user_from_patient(sql_user: SQLUser, patient: Patient) -> SQLUser:
        """Update SQLAlchemy User from domain Patient (non-destructive)"""
        sql_user.first_name = patient.first_name
        sql_user.last_name = patient.last_name
        sql_user.gender = patient.gender.value if patient.gender else None
        sql_user.email = patient.email
        sql_user.phone = patient.phone
        sql_user.line_user_id = patient.line_user_id

        return sql_user


class UserMapper:
    """Maps between SQLAlchemy User models and User domain objects"""

    @staticmethod
    def to_domain(sql_user: SQLUser) -> DomainUser:
        """Convert SQLAlchemy User to domain User"""
        # Map staff details
        staff_details = None
        if sql_user.staff_details:
            staff_details = StaffDetails(
                title=sql_user.staff_details.title,
                department=None,  # Not in current schema
                license_number=None  # Not in current schema
            )

        return DomainUser(
            user_id=sql_user.id,
            account=sql_user.account,
            first_name=sql_user.first_name or "",
            last_name=sql_user.last_name or "",
            email=sql_user.email,
            phone=sql_user.phone,
            line_user_id=sql_user.line_user_id,
            is_staff=sql_user.is_staff,
            is_admin=sql_user.is_admin,
            staff_details=staff_details,
            last_login=sql_user.last_login,
            created_at=sql_user.created_at,
            updated_at=sql_user.updated_at
        )

    @staticmethod
    def to_sql(domain_user: DomainUser, existing_user: Optional[SQLUser] = None) -> SQLUser:
        """Convert domain User to SQLAlchemy User"""
        if existing_user:
            user = existing_user
        else:
            user = SQLUser()

        user.account = domain_user.account
        user.first_name = domain_user.first_name
        user.last_name = domain_user.last_name
        user.email = domain_user.email
        user.phone = domain_user.phone
        user.line_user_id = domain_user.line_user_id
        user.is_staff = domain_user.is_staff
        user.is_admin = domain_user.is_admin

        return user

    @staticmethod
    def to_sql_staff_detail(domain_user: DomainUser, user_id: int, existing_detail: Optional[SQLStaffDetail] = None) -> Optional[SQLStaffDetail]:
        """Convert domain User's staff details to SQLAlchemy StaffDetail"""
        if not domain_user.staff_details:
            return None

        if existing_detail:
            detail = existing_detail
        else:
            detail = SQLStaffDetail(user_id=user_id)

        detail.title = domain_user.staff_details.title

        return detail