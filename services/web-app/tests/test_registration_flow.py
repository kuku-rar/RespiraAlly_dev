"""
Integration test for LINE registration flow
Tests the complete registration flow from frontend to backend
"""

import pytest


class TestRegistrationFlow:
    """Test complete registration flow with firstName/lastName"""

    def test_registration_with_chinese_name(self, client):
        """Test registration with Chinese name (no space separation)"""
        # Simulate frontend request with separate first_name and last_name
        registration_data = {
            'lineUserId': 'U_chen_meili_12345',
            'first_name': '美麗',  # 名
            'last_name': '陳',     # 姓
            'gender': 'female',
            'phone': '0987654321',
            'height_cm': 165,
            'weight_kg': 58,
            'smoke_status': 'never'
        }

        response = client.post('/api/v1/auth/line/register', json=registration_data)

        # Verify successful registration
        assert response.status_code == 201
        data = response.get_json()

        # Verify response structure
        assert "data" in data
        token_data = data["data"]
        assert "token" in token_data
        assert "user" in token_data

        # Verify user data contains correct names
        user = token_data["user"]
        assert user["first_name"] == "美麗"
        assert user["last_name"] == "陳"
        assert user["line_user_id"] == "U_chen_meili_12345"

    def test_registration_with_english_name(self, client):
        """Test registration with English name"""
        registration_data = {
            'lineUserId': 'U_john_doe_67890',
            'first_name': 'John',
            'last_name': 'Doe',
            'gender': 'male',
            'phone': '0912345678'
        }

        response = client.post('/api/v1/auth/line/register', json=registration_data)

        assert response.status_code == 201
        data = response.get_json()

        user = data["data"]["user"]
        assert user["first_name"] == "John"
        assert user["last_name"] == "Doe"

    def test_registration_missing_firstname(self, client):
        """Test registration fails when first_name is missing"""
        registration_data = {
            'lineUserId': 'U_missing_firstname',
            'last_name': '陳',
            'gender': 'male',
            'phone': '0912345678'
        }

        response = client.post('/api/v1/auth/line/register', json=registration_data)

        # Should fail validation
        assert response.status_code == 400

    def test_registration_missing_lastname(self, client):
        """Test registration fails when last_name is missing"""
        registration_data = {
            'lineUserId': 'U_missing_lastname',
            'first_name': '美麗',
            'gender': 'female',
            'phone': '0912345678'
        }

        response = client.post('/api/v1/auth/line/register', json=registration_data)

        # Should fail validation
        assert response.status_code == 400

    def test_registration_with_optional_health_data(self, client):
        """Test registration with optional health information"""
        registration_data = {
            'lineUserId': 'U_with_health_data',
            'first_name': '小明',
            'last_name': '王',
            'gender': 'male',
            'phone': '0911222333',
            'height_cm': 175,
            'weight_kg': 70,
            'smoke_status': 'former'
        }

        response = client.post('/api/v1/auth/line/register', json=registration_data)

        assert response.status_code == 201
        data = response.get_json()

        # Verify user was created successfully
        # Note: health_profile is created in database but not returned in registration response
        user = data["data"]["user"]
        assert user["first_name"] == "小明"
        assert user["last_name"] == "王"
        assert user["line_user_id"] == "U_with_health_data"

    def test_duplicate_line_user_id_updates_data(self, client):
        """Test registration with duplicate LINE user ID updates existing user (upsert)"""
        # Initial registration
        initial_data = {
            'lineUserId': 'U_upsert_test',
            'first_name': '測試',
            'last_name': '重複',
            'gender': 'male',
            'phone': '0912345678',
            'height_cm': 170,
            'weight_kg': 65
        }

        response1 = client.post('/api/v1/auth/line/register', json=initial_data)
        assert response1.status_code == 201
        data1 = response1.get_json()
        user_id_1 = data1["data"]["user"]["id"]

        # Second registration with same LINE ID but different data (should update)
        updated_data = {
            'lineUserId': 'U_upsert_test',
            'first_name': '更新',
            'last_name': '姓名',
            'gender': 'female',
            'phone': '0987654321',
            'height_cm': 165,
            'weight_kg': 55,
            'smoke_status': 'never'
        }

        response2 = client.post('/api/v1/auth/line/register', json=updated_data)
        assert response2.status_code == 201

        # Verify data was updated (same user ID)
        data2 = response2.get_json()
        user_id_2 = data2["data"]["user"]["id"]
        assert user_id_1 == user_id_2  # Same user

        # Verify updated values
        user = data2["data"]["user"]
        assert user["first_name"] == "更新"
        assert user["last_name"] == "姓名"
        assert user["line_user_id"] == "U_upsert_test"
