"""
Basic API Contract Tests

These tests verify the API endpoints return the expected response structure.
They use a more lightweight approach to testing the contracts.
"""

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.app import create_app


def test_auth_login_contract():
    """Test that login endpoint returns expected structure"""
    app, _ = create_app("testing")

    with app.test_client() as client:
        # Test with invalid credentials to check error structure
        response = client.post('/api/v1/auth/login', json={
            'account': 'invalid',
            'password': 'invalid'
        })

        # Should return 401 with proper error structure
        assert response.status_code == 401
        data = response.get_json()

        # Validate error response structure
        assert "error" in data
        assert "code" in data["error"]
        assert "message" in data["error"]
        assert isinstance(data["error"]["code"], str)
        assert isinstance(data["error"]["message"], str)


def test_auth_login_missing_fields_contract():
    """Test login with missing required fields"""
    app, _ = create_app("testing")

    with app.test_client() as client:
        response = client.post('/api/v1/auth/login', json={
            'account': 'admin'
            # missing password
        })

        # Should return 400 with proper error structure
        assert response.status_code == 400
        data = response.get_json()

        # Validate error response structure
        assert "error" in data
        assert "code" in data["error"]
        assert "message" in data["error"]


def test_auth_line_login_missing_fields_contract():
    """Test LINE login with missing required fields"""
    app, _ = create_app("testing")

    with app.test_client() as client:
        response = client.post('/api/v1/auth/line/login', json={})

        # Should return 400 with proper error structure
        assert response.status_code == 400
        data = response.get_json()

        # Validate error response structure
        assert "error" in data
        assert "code" in data["error"]
        assert "message" in data["error"]


def test_therapist_patients_unauthorized_contract():
    """Test unauthorized access to therapist patients endpoint"""
    app, _ = create_app("testing")

    with app.test_client() as client:
        response = client.get('/api/v1/therapist/patients')

        # Should return 401 with proper error structure
        assert response.status_code == 422  # JWT library returns 422 for missing token
        # Note: This might vary depending on JWT configuration


def test_openapi_spec_exists():
    """Test that OpenAPI specification file exists and is valid YAML"""
    import yaml

    spec_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'openapi.yaml'
    )

    assert os.path.exists(spec_path), "OpenAPI specification file should exist"

    with open(spec_path, 'r', encoding='utf-8') as f:
        spec = yaml.safe_load(f)

    # Validate basic OpenAPI structure
    assert "openapi" in spec
    assert "info" in spec
    assert "paths" in spec
    assert "components" in spec

    # Validate info section
    assert "title" in spec["info"]
    assert "version" in spec["info"]

    # Validate that key endpoints are documented
    expected_paths = [
        "/auth/login",
        "/auth/line/login",
        "/auth/line/register",
        "/therapist/patients",
        "/patients/{patient_id}/profile",
        "/patients/{patient_id}/questionnaires/cat",
        "/patients/{patient_id}/daily_metrics",
        "/users"
    ]

    for path in expected_paths:
        assert path in spec["paths"], f"Path {path} should be documented in OpenAPI spec"


def test_response_headers_contract():
    """Test that responses include expected CORS headers"""
    app, _ = create_app("testing")

    with app.test_client() as client:
        response = client.get('/api/v1/therapist/patients')

        # Check CORS headers are present
        assert 'Access-Control-Allow-Origin' in response.headers
        assert response.headers['Access-Control-Allow-Origin'] == '*'


def test_options_preflight_contract():
    """Test that OPTIONS requests are handled correctly for CORS"""
    app, _ = create_app("testing")

    with app.test_client() as client:
        response = client.options('/api/v1/therapist/patients')

        # Should return 200 with CORS headers
        assert response.status_code == 200
        assert 'Access-Control-Allow-Origin' in response.headers
        assert 'Access-Control-Allow-Methods' in response.headers
        assert 'Access-Control-Allow-Headers' in response.headers


if __name__ == "__main__":
    pytest.main([__file__, "-v"])