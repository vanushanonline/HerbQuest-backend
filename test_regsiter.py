import pytest
from fastapi.testclient import TestClient
from main import app  # Import your FastAPI app
import bcrypt

from database import (
    get_user_collection, User,
    store_image_metadata, update_processing_time, 
    store_plant_data
)

# Initialize the TestClient with the FastAPI app
client = TestClient(app)

# Sample user data for tests
new_user = {
    "email": "testuser@example.com",
    "password": "password123"
}

existing_user = {
    "email": "a@a.com",
    "password": "password456"
}


def get_token():
    """Helper function to get a valid token from the /token endpoint."""
    response = client.get("/token")
    token_data = response.json()
    return f"Bearer {token_data['access_token']}"  # Return the full Authorization header value


def test_register_new_user():
    """Test for successful registration of a new user."""

    # Get the token first
    token = get_token()
    
    # Set the Authorization header with the token
    headers = {
        "Authorization": token
    }

    # Send the POST request to the /register endpoint
    response = client.post("/register", json=new_user, headers=headers)

    # Check if the response is as expected
    assert response.status_code == 200
    json_response = response.json()
    
    assert json_response["status"] == 0
    assert json_response["message"] == "User registered successfully"
    user_collection = get_user_collection()
    # Verify that the user was actually added to the database
    registered_user = user_collection.find_one({"email": new_user["email"]})
    assert registered_user is not None
    assert bcrypt.checkpw(new_user["password"].encode('utf-8'), registered_user["password"].encode('utf-8'))
    
    # Clean up by deleting the user after the test
    delete_result = user_collection.delete_one({"email": new_user["email"]})
    assert delete_result.deleted_count == 1  # Ensure the user was deleted

def test_register_existing_user():
    """Test for trying to register a user that already exists."""
    # Get the token first
    token = get_token()
    
    # Set the Authorization header with the token
    headers = {
        "Authorization": token
    }

    # Send the POST request to the /register endpoint
    response = client.post("/register", json=existing_user, headers=headers)

    # Check if the response is as expected
    assert response.status_code == 200
    json_response = response.json()
    
    assert json_response["status"] == 1
    assert json_response["message"] == "Email already registered"
