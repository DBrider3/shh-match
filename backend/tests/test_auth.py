import pytest
from fastapi.testclient import TestClient


def test_sync_kakao_new_user(client: TestClient):
    """Test syncing new Kakao user"""
    response = client.post(
        "/api/v1/auth/sync-kakao",
        json={
            "kakaoUserId": "123456789",
            "email": "test@example.com",
            "nickname": "테스트유저"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "jwt" in data
    assert "user" in data
    assert data["user"]["kakaoUserId"] == "123456789"


def test_sync_kakao_existing_user(client: TestClient):
    """Test syncing existing Kakao user"""
    # First registration
    response1 = client.post(
        "/api/v1/auth/sync-kakao",
        json={
            "kakaoUserId": "123456789",
            "nickname": "테스트유저"
        }
    )
    assert response1.status_code == 200

    # Second registration (should return existing user)
    response2 = client.post(
        "/api/v1/auth/sync-kakao",
        json={
            "kakaoUserId": "123456789",
            "nickname": "테스트유저2"
        }
    )
    assert response2.status_code == 200
    assert response1.json()["user"]["id"] == response2.json()["user"]["id"]


def test_get_me_unauthorized(client: TestClient):
    """Test getting user info without authentication"""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 403  # No auth header


def test_get_me_with_auth(client: TestClient):
    """Test getting user info with authentication"""
    # Create user and get token
    auth_response = client.post(
        "/api/v1/auth/sync-kakao",
        json={
            "kakaoUserId": "123456789",
            "nickname": "테스트유저"
        }
    )
    token = auth_response.json()["jwt"]

    # Get user info
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert "profile" in data
    assert "preferences" in data