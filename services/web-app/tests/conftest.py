"""
Test configuration and shared fixtures
"""

"""
PyTest Configuration for API Contract Tests

This file sets up the test environment and provides reusable fixtures for all contract tests.
Ensures proper database setup, cleanup, and authentication for testing.
"""

import pytest
import os
import os
import tempfile
from app.app import create_app
from app.extensions import db


@pytest.fixture
def app():
    """Create application for testing"""
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp()

    # Configure for testing
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test-secret-key',
        'JWT_SECRET_KEY': 'test-jwt-secret-key',
        'WTF_CSRF_ENABLED': False
    }

    app, socketio = create_app("testing")
    app.config.update(test_config)

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner"""
    return app.test_cli_runner()


@pytest.fixture
def db_setup(app):
    """Setup database with test data"""
    from app.models.models import User, HealthProfile, StaffDetail
    from app.extensions import db

    with app.app_context():
        # Create test users
        admin = User(
            account='test_admin',
            first_name='Admin',
            last_name='User',
            email='admin@test.com',
            is_staff=True,
            is_admin=True
        )
        admin.set_password('testpass')

        therapist = User(
            account='test_therapist',
            first_name='Therapist',
            last_name='User',
            email='therapist@test.com',
            is_staff=True,
            is_admin=False
        )
        therapist.set_password('testpass')

        patient = User(
            account='test_patient',
            first_name='Patient',
            last_name='User',
            email='patient@test.com',
            line_user_id='U_test_patient_line_id',
            is_staff=False,
            is_admin=False
        )
        patient.set_password('testpass')

        db.session.add_all([admin, therapist, patient])
        db.session.commit()

        # Create staff details
        admin_staff = StaffDetail(user_id=admin.id, title='系統管理員')
        therapist_staff = StaffDetail(user_id=therapist.id, title='呼吸治療師')
        db.session.add_all([admin_staff, therapist_staff])

        # Create health profile for patient
        patient_profile = HealthProfile(
            user_id=patient.id,
            height_cm=170,
            weight_kg=65,
            smoke_status='never',
            staff_id=therapist.id
        )
        db.session.add(patient_profile)
        db.session.commit()

        yield db

        # Cleanup
        db.session.remove()


@pytest.fixture
def admin_user(db_setup):
    """Get admin user"""
    from app.models.models import User
    return User.query.filter_by(account='test_admin').first()


@pytest.fixture
def therapist_user(db_setup):
    """Get therapist user"""
    from app.models.models import User
    return User.query.filter_by(account='test_therapist').first()


@pytest.fixture
def patient_user(db_setup):
    """Get patient user"""
    from app.models.models import User
    return User.query.filter_by(account='test_patient').first()


@pytest.fixture
def admin_auth_headers(app, admin_user):
    """Get admin authentication headers"""
    from flask_jwt_extended import create_access_token
    from datetime import timedelta

    with app.app_context():
        identity = str(admin_user.id)
        additional_claims = {'roles': ['staff', 'admin']}
        access_token = create_access_token(
            identity=identity,
            expires_delta=timedelta(hours=1),
            additional_claims=additional_claims
        )
        return {'Authorization': f'Bearer {access_token}'}


@pytest.fixture
def therapist_auth_headers(app, therapist_user):
    """Get therapist authentication headers"""
    from flask_jwt_extended import create_access_token
    from datetime import timedelta

    with app.app_context():
        identity = str(therapist_user.id)
        additional_claims = {'roles': ['staff']}
        access_token = create_access_token(
            identity=identity,
            expires_delta=timedelta(hours=1),
            additional_claims=additional_claims
        )
        return {'Authorization': f'Bearer {access_token}'}


@pytest.fixture
def patient_auth_headers(app, patient_user):
    """Get patient authentication headers"""
    from flask_jwt_extended import create_access_token
    from datetime import timedelta

    with app.app_context():
        identity = str(patient_user.id)
        additional_claims = {'roles': ['patient']}
        access_token = create_access_token(
            identity=identity,
            expires_delta=timedelta(days=7),
            additional_claims=additional_claims
        )
        return {'Authorization': f'Bearer {access_token}'}