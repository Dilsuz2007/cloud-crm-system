def test_login_success(client, test_users):
    # The login endpoint uses OAuth2PasswordRequestForm, which expects form data
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test_admin@texstyle.uz", "password": "admin123"}
    )
    assert response.status_code == 200
    json_data = response.json()
    assert "access_token" in json_data
    assert json_data["token_type"] == "bearer"

def test_login_invalid_credentials(client, test_users):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test_admin@texstyle.uz", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Email yoki parol noto'g'ri"

def test_get_me_success(client, admin_headers):
    response = client.get("/api/v1/auth/me", headers=admin_headers)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["email"] == "test_admin@texstyle.uz"
    assert json_data["role"] == "admin"
    assert json_data["full_name"] == "Test Admin"

def test_get_me_unauthorized(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert "detail" in response.json()
