"""
API Contract Tests

These tests ensure that our API endpoints maintain their contracts during refactoring.
They validate the exact input/output structure of each endpoint.

As per the refactoring plan: "編寫契約測試：使用 pytest 編寫一套測試，直接透過 HTTP 呼叫 API 端點，
並嚴格驗證其返回的 JSON 是否與 OpenAPI 規格完全一致。"
"""

import pytest
import json
from datetime import datetime, date
from flask import Flask
from app.app import create_app
from app.extensions import db
from app.models.models import User, HealthProfile, StaffDetail


class APIContractTester:
    """Base class for API contract testing"""

    def __init__(self, client, auth_headers=None):
        self.client = client
        self.auth_headers = auth_headers or {}

    def validate_error_response(self, response, expected_status_code):
        """Validate error response structure matches OpenAPI spec"""
        assert response.status_code == expected_status_code
        data = response.get_json()
        assert "error" in data
        assert "code" in data["error"]
        assert "message" in data["error"]
        assert isinstance(data["error"]["code"], str)
        assert isinstance(data["error"]["message"], str)

    def validate_pagination_meta(self, pagination_data):
        """Validate pagination metadata structure"""
        required_fields = ["total_items", "total_pages", "current_page", "per_page"]
        for field in required_fields:
            assert field in pagination_data
            assert isinstance(pagination_data[field], int)


@pytest.fixture
def app():
    """Create application for testing"""
    app, _ = create_app("testing")
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def db_setup(app):
    """Setup database for testing"""
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()


@pytest.fixture
def admin_user(app, db_setup):
    """Create admin user for testing"""
    with app.app_context():
        admin = User(
            account="admin",
            first_name="Test",
            last_name="Admin",
            email="admin@test.com",
            is_staff=True,
            is_admin=True
        )
        admin.set_password("admin")
        db_setup.session.add(admin)
        db_setup.session.commit()
        return admin


@pytest.fixture
def therapist_user(app, db_setup):
    """Create therapist user for testing"""
    with app.app_context():
        therapist = User(
            account="therapist",
            first_name="Test",
            last_name="Therapist",
            email="therapist@test.com",
            is_staff=True,
            is_admin=False
        )
        therapist.set_password("therapist")
        db_setup.session.add(therapist)
        db_setup.session.commit()
        return therapist


@pytest.fixture
def patient_user(app, db_setup, therapist_user):
    """Create patient user for testing"""
    with app.app_context():
        patient = User(
            line_user_id="U123456789test",
            first_name="Test",
            last_name="Patient",
            gender="male",
            phone="0912345678"
        )
        db_setup.session.add(patient)
        db_setup.session.commit()

        # Create health profile
        health_profile = HealthProfile(
            user_id=patient.id,
            height_cm=170,
            weight_kg=70,
            smoke_status="never",
            staff_id=therapist_user.id
        )
        db_setup.session.add(health_profile)
        db_setup.session.commit()
        return patient


@pytest.fixture
def admin_auth_headers(client, admin_user):
    """Get auth headers for admin user"""
    response = client.post('/api/v1/auth/login', json={
        'account': 'admin',
        'password': 'admin'
    })
    assert response.status_code == 200
    token = response.get_json()['data']['token']
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def therapist_auth_headers(client, therapist_user):
    """Get auth headers for therapist user"""
    response = client.post('/api/v1/auth/login', json={
        'account': 'therapist',
        'password': 'therapist'
    })
    assert response.status_code == 200
    token = response.get_json()['data']['token']
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def patient_auth_headers(client, patient_user):
    """Get auth headers for patient user"""
    response = client.post('/api/v1/auth/line/login', json={
        'lineUserId': 'U123456789test'
    })
    assert response.status_code == 200
    token = response.get_json()['data']['token']
    return {'Authorization': f'Bearer {token}'}


class TestAuthenticationContracts:
    """Test authentication endpoint contracts"""

    def test_staff_login_success_contract(self, client):
        """Test staff login success response structure"""
        response = client.post('/api/v1/auth/login', json={
            'account': 'admin',
            'password': 'admin'
        })

        assert response.status_code == 200
        data = response.get_json()

        # Validate top-level structure
        assert "data" in data
        assert isinstance(data["data"], dict)

        # Validate token structure
        token_data = data["data"]
        assert "token" in token_data
        assert "expires_in" in token_data
        assert "user" in token_data
        assert isinstance(token_data["token"], str)
        assert isinstance(token_data["expires_in"], (int, float))

        # Validate user structure
        user_data = token_data["user"]
        required_user_fields = ["id", "account", "first_name", "last_name", "is_staff", "is_admin"]
        for field in required_user_fields:
            assert field in user_data
        assert isinstance(user_data["id"], int)
        assert isinstance(user_data["account"], str)
        assert isinstance(user_data["is_staff"], bool)
        assert isinstance(user_data["is_admin"], bool)

    def test_staff_login_invalid_credentials_contract(self, client):
        """Test staff login error response structure"""
        tester = APIContractTester(client)
        response = client.post('/api/v1/auth/login', json={
            'account': 'invalid',
            'password': 'invalid'
        })
        tester.validate_error_response(response, 401)

    def test_staff_login_missing_fields_contract(self, client):
        """Test staff login missing fields error structure"""
        tester = APIContractTester(client)
        response = client.post('/api/v1/auth/login', json={
            'account': 'admin'
        })
        tester.validate_error_response(response, 400)

    def test_line_login_success_contract(self, client, patient_user):
        """Test LINE login success response structure"""
        response = client.post('/api/v1/auth/line/login', json={
            'lineUserId': 'U123456789test'
        })

        assert response.status_code == 200
        data = response.get_json()

        # Validate structure according to OpenAPI spec
        assert "data" in data
        token_data = data["data"]
        assert "token" in token_data
        assert "expires_in" in token_data
        assert "user" in token_data

        # Validate user structure for LINE login
        user_data = token_data["user"]
        required_fields = ["id", "line_user_id", "first_name", "last_name", "health_profile"]
        for field in required_fields:
            assert field in user_data

        # Validate health_profile structure
        health_profile = user_data["health_profile"]
        assert isinstance(health_profile, dict)
        health_fields = ["height_cm", "weight_kg", "smoke_status"]
        for field in health_fields:
            assert field in health_profile

    def test_line_register_success_contract(self, client):
        """Test LINE register success response structure"""
        response = client.post('/api/v1/auth/line/register', json={
            'lineUserId': 'U_new_user_12345',
            'first_name': '新',
            'last_name': '使用者',
            'gender': 'female',
            'phone': '0912345678',
            'height_cm': 160,
            'weight_kg': 55,
            'smoke_status': 'never'
        })

        assert response.status_code == 201
        data = response.get_json()

        # Validate structure matches OpenAPI spec
        assert "data" in data
        token_data = data["data"]
        assert "token" in token_data
        assert "expires_in" in token_data
        assert "user" in token_data


class TestPatientManagementContracts:
    """Test patient management endpoint contracts"""

    def test_get_therapist_patients_success_contract(self, client, therapist_auth_headers, patient_user):
        """Test therapist patients list response structure"""
        response = client.get('/api/v1/therapist/patients', headers=therapist_auth_headers)

        assert response.status_code == 200
        data = response.get_json()

        # Validate structure according to OpenAPI spec
        assert "data" in data
        assert isinstance(data["data"], list)

        # If there are patients, validate patient structure
        if data["data"]:
            patient = data["data"][0]
            expected_fields = ["user_id", "first_name", "last_name"]
            for field in expected_fields:
                assert field in patient

    def test_get_therapist_patients_unauthorized_contract(self, client):
        """Test unauthorized access to therapist patients"""
        tester = APIContractTester(client)
        response = client.get('/api/v1/therapist/patients')
        tester.validate_error_response(response, 401)

    def test_get_patient_profile_success_contract(self, client, therapist_auth_headers, patient_user):
        """Test patient profile response structure"""
        response = client.get(f'/api/v1/patients/{patient_user.id}/profile',
                            headers=therapist_auth_headers)

        assert response.status_code == 200
        data = response.get_json()

        # Validate structure according to OpenAPI spec
        assert "data" in data
        patient_data = data["data"]

        required_fields = ["user_id", "first_name", "last_name", "gender", "email", "phone", "health_profile"]
        for field in required_fields:
            assert field in patient_data

        # Validate health_profile structure
        health_profile = patient_data["health_profile"]
        assert isinstance(health_profile, dict)
        health_fields = ["height_cm", "weight_kg", "smoke_status", "updated_at"]
        for field in health_fields:
            assert field in health_profile

    def test_get_patient_kpis_success_contract(self, client, therapist_auth_headers, patient_user):
        """Test patient KPIs response structure"""
        response = client.get(f'/api/v1/patients/{patient_user.id}/kpis',
                            headers=therapist_auth_headers)

        assert response.status_code == 200
        data = response.get_json()

        # Validate structure according to OpenAPI spec
        assert "data" in data
        assert "meta" in data

        # Validate meta structure
        meta = data["meta"]
        required_meta_fields = ["patient_id", "calculation_days", "calculated_at"]
        for field in required_meta_fields:
            assert field in meta
        assert isinstance(meta["patient_id"], int)
        assert isinstance(meta["calculation_days"], int)
        assert isinstance(meta["calculated_at"], str)


class TestQuestionnaireContracts:
    """Test questionnaire endpoint contracts"""

    def test_get_cat_history_success_contract(self, client, patient_auth_headers, patient_user):
        """Test CAT history response structure"""
        response = client.get(f'/api/v1/patients/{patient_user.id}/questionnaires/cat',
                            headers=patient_auth_headers)

        assert response.status_code == 200
        data = response.get_json()

        # Validate structure according to OpenAPI spec
        assert "data" in data
        assert "pagination" in data
        assert isinstance(data["data"], list)

        # Validate pagination structure
        tester = APIContractTester(client)
        tester.validate_pagination_meta(data["pagination"])

    def test_submit_cat_questionnaire_success_contract(self, client, patient_auth_headers, patient_user):
        """Test CAT questionnaire submission response structure"""
        cat_data = {
            "record_date": "2025-01-15",
            "cough_score": 2,
            "phlegm_score": 1,
            "chest_score": 3,
            "breath_score": 2,
            "limit_score": 1,
            "confidence_score": 2,
            "sleep_score": 2,
            "energy_score": 2
        }

        response = client.post(f'/api/v1/patients/{patient_user.id}/questionnaires/cat',
                             json=cat_data, headers=patient_auth_headers)

        assert response.status_code == 201
        data = response.get_json()

        # Validate structure according to OpenAPI spec
        assert "data" in data
        response_data = data["data"]
        required_fields = ["record_id", "total_score", "message"]
        for field in required_fields:
            assert field in response_data
        assert isinstance(response_data["record_id"], int)
        assert isinstance(response_data["total_score"], int)
        assert isinstance(response_data["message"], str)

    def test_submit_cat_questionnaire_invalid_data_contract(self, client, patient_auth_headers, patient_user):
        """Test CAT questionnaire submission with invalid data"""
        tester = APIContractTester(client)
        response = client.post(f'/api/v1/patients/{patient_user.id}/questionnaires/cat',
                             json={}, headers=patient_auth_headers)
        tester.validate_error_response(response, 400)


class TestDailyMetricsContracts:
    """Test daily metrics endpoint contracts"""

    def test_get_daily_metrics_success_contract(self, client, patient_auth_headers, patient_user):
        """Test daily metrics list response structure"""
        response = client.get(f'/api/v1/patients/{patient_user.id}/daily_metrics',
                            headers=patient_auth_headers)

        assert response.status_code == 200
        data = response.get_json()

        # Validate structure according to OpenAPI spec
        assert "data" in data
        assert "pagination" in data
        assert isinstance(data["data"], list)

        # Validate pagination structure
        tester = APIContractTester(client)
        tester.validate_pagination_meta(data["pagination"])

    def test_add_daily_metric_success_contract(self, client, patient_auth_headers, patient_user):
        """Test daily metric creation response structure"""
        metric_data = {
            "water_cc": 2000,
            "medication": True,
            "exercise_min": 30,
            "cigarettes": 0
        }

        response = client.post(f'/api/v1/patients/{patient_user.id}/daily_metrics',
                             json=metric_data, headers=patient_auth_headers)

        assert response.status_code == 201
        data = response.get_json()

        # Validate structure according to OpenAPI spec
        assert "data" in data
        metric_response = data["data"]
        required_fields = ["log_id", "created_at", "water_cc", "medication", "exercise_min", "cigarettes"]
        for field in required_fields:
            assert field in metric_response

        # Validate data types
        assert isinstance(metric_response["log_id"], int)
        assert isinstance(metric_response["created_at"], str)
        assert isinstance(metric_response["water_cc"], int)
        assert isinstance(metric_response["medication"], bool)
        assert isinstance(metric_response["exercise_min"], int)
        assert isinstance(metric_response["cigarettes"], int)

    def test_add_daily_metric_empty_body_contract(self, client, patient_auth_headers, patient_user):
        """Test daily metric creation with empty body"""
        tester = APIContractTester(client)
        response = client.post(f'/api/v1/patients/{patient_user.id}/daily_metrics',
                             json={}, headers=patient_auth_headers)
        tester.validate_error_response(response, 400)


class TestUserManagementContracts:
    """Test user management endpoint contracts"""

    def test_create_user_success_contract(self, client, admin_auth_headers):
        """Test user creation response structure"""
        user_data = {
            "account": "new_therapist_01",
            "password": "strong_password_123",
            "first_name": "新",
            "last_name": "治療師",
            "email": "new@therapist.com",
            "is_staff": True,
            "is_admin": False,
            "title": "呼吸治療師"
        }

        response = client.post('/api/v1/users/', json=user_data, headers=admin_auth_headers)

        assert response.status_code == 201
        data = response.get_json()

        # Validate structure according to OpenAPI spec
        assert "data" in data
        user_response = data["data"]
        required_fields = ["id", "account", "first_name", "last_name", "email", "is_staff", "is_admin", "created_at"]
        for field in required_fields:
            assert field in user_response

        # Validate data types
        assert isinstance(user_response["id"], int)
        assert isinstance(user_response["account"], str)
        assert isinstance(user_response["is_staff"], bool)
        assert isinstance(user_response["is_admin"], bool)

    def test_create_user_unauthorized_contract(self, client, therapist_auth_headers):
        """Test user creation with insufficient permissions"""
        tester = APIContractTester(client)
        user_data = {
            "account": "unauthorized_user",
            "password": "password",
            "is_staff": False,
            "is_admin": False
        }
        response = client.post('/api/v1/users/', json=user_data, headers=therapist_auth_headers)
        tester.validate_error_response(response, 403)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])