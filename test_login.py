from fastapi.testclient import TestClient
from main import app  # Import your FastAPI app

# Initialize the TestClient with the FastAPI app
client = TestClient(app)

# Sample user data for tests
valid_user = {
    "email": "a@a.com",
    "password": "123"
}

invalid_user = {
    "email": "a@a.com",
    "password": "wrongpassword"
}


no_user = {
    "email": "a@abc.com",
    "password": "wrongpassword"
}


def get_token():
    """Helper function to get a valid token from the /token endpoint."""
    response = client.get("/token")
    token_data = response.json()
    return f"Bearer {token_data['access_token']}"  # Return the full Authorization header value

def test_login_success():
    # Get the token first
    token = get_token()
    
    # Set the Authorization header with the token
    headers = {
        "Authorization": token
    }
    
    # Send the login request with valid credentials and the Authorization header
    response = client.post("/login", json=valid_user, headers=headers)
    
    # Check if the response is as expected
    assert response.status_code == 200
    
    # Parse the JSON response
    json_response = response.json()
    
    # Check only the status and message, and confirm access_token and token_type are present
    assert json_response["status"] == 0
    assert json_response["message"] == "Login success"
    assert "access_token" in json_response
    assert json_response["token_type"] == "bearer"


def test_login_failed():
    # Get the token first
    token = get_token()
    
    # Set the Authorization header with the token
    headers = {
        "Authorization": token
    }
    
    # Send the login request with valid credentials and the Authorization header
    response = client.post("/login", json=invalid_user, headers=headers)
    
    # Check if the response is as expected
    assert response.status_code == 200
    
    # Parse the JSON response
    json_response = response.json()
    
    # Check only the status and message, and confirm access_token and token_type are present
    assert json_response["status"] == 1
    assert json_response["message"] == "Invalid login credentials supplied"


def test_login_nouser():
    # Get the token first
    token = get_token()
    
    # Set the Authorization header with the token
    headers = {
        "Authorization": token
    }
    
    # Send the login request with valid credentials and the Authorization header
    response = client.post("/login", json=no_user, headers=headers)
    
    # Check if the response is as expected
    assert response.status_code == 200
    
    # Parse the JSON response
    json_response = response.json()
    
    # Check only the status and message, and confirm access_token and token_type are present
    assert json_response["status"] == 1
    assert json_response["message"] =='Invalid login credentials supplied'

