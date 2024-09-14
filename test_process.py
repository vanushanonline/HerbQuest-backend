import pytest
from fastapi.testclient import TestClient
from main import app  # Import your FastAPI app

# Initialize the TestClient with the FastAPI app
client = TestClient(app)

# Paths to the test images
butterfly_pea_image = "Validation/ButterflyPea/009_0.jpg"
common_wireweed_image = "Validation/CommonWireweed/011_27.jpg"
crown_flower_image = "Validation/CrownFlower/013_7.jpg"
green_chireta_image = "Validation/GreenChireta/014_56.jpg"
heart_leaved_moonseed_image = "Validation/HeartLeavedMoonseed/050_54.jpg"
holy_basil_image = "Validation/HolyBasil/015_25.jpg"
indian_copper_leaf_image = "Validation/IndianCopperLeaf/016_57.jpg"
indian_jujube_image = "Validation/IndianJujube/017_22.jpg"
indian_stinging_nettle_image = "Validation/IndianStingingNettle/019_57.jpg"
ivy_gourd_image = "Validation/IvyGourd/022_18.jpg"
rosary_pea_image = "Validation/RosaryPea/038_4.jpg"
small_water_clover_image = "Validation/SmallWaterClover/040_33.jpg"
spider_wisp_image = "Validation/SpiderWisp/041_21.jpg"
square_stalked_vine_image = "Validation/SquareStalkedVine/042_78.jpg"
trellis_vine_image = "Validation/TrellisVine/047_3.jpg"

def get_token():
    """Helper function to get a valid token from the /token endpoint."""
    response = client.get("/token")
    token_data = response.json()
    return f"Bearer {token_data['access_token']}"  # Return the full Authorization header value

@pytest.fixture(scope="function")
def load_image_file(image_path):
    """Fixture to load an image file object."""
    return open(image_path, "rb")

def process_image_test(image_file, expected_name):
    """Helper function to process an image and run assertions."""
    # Get the token first
    token = get_token()

    # Set the Authorization header with the token
    headers = {"Authorization": token}

    # Prepare the file upload
    files = {"file": (image_file.name.split("/")[-1], image_file, "image/jpeg")}

    # Send the POST request to the /process endpoint
    response = client.post("/process", files=files, headers=headers)

    # Check if the response is as expected
    assert response.status_code == 200

    # Parse the JSON response
    json_response = response.json()
    name = json_response['data']['name']
    print(f"Processed Image: {name}")

    # Check the status, message, and data fields
    assert json_response["status"] == 0
    assert "message" in json_response
    assert "data" in json_response

    # Check if the predicted name matches the expected name
    assert name == expected_name

# Test functions for each image

def test_process_butterfly_pea():
    with open(butterfly_pea_image, "rb") as image_file:
        process_image_test(image_file, "Butterfly Pea")

def test_process_common_wireweed():
    with open(common_wireweed_image, "rb") as image_file:
        process_image_test(image_file, "Common Wireweed")

def test_process_crown_flower():
    with open(crown_flower_image, "rb") as image_file:
        process_image_test(image_file, "Crown Flower")

def test_process_green_chireta():
    with open(green_chireta_image, "rb") as image_file:
        process_image_test(image_file, "Green Chireta")

def test_process_heart_leaved_moonseed():
    with open(heart_leaved_moonseed_image, "rb") as image_file:
        process_image_test(image_file, "Heart-Leaved Moonseed")

def test_process_holy_basil():
    with open(holy_basil_image, "rb") as image_file:
        process_image_test(image_file, "Holy Basil")

def test_process_indian_copper_leaf():
    with open(indian_copper_leaf_image, "rb") as image_file:
        process_image_test(image_file, "Indian Copperleaf")

def test_process_indian_jujube():
    with open(indian_jujube_image, "rb") as image_file:
        process_image_test(image_file, "Indian Jujube")

def test_process_indian_stinging_nettle():
    with open(indian_stinging_nettle_image, "rb") as image_file:
        process_image_test(image_file, "Indian Stinging Nettle")

def test_process_ivy_gourd():
    with open(ivy_gourd_image, "rb") as image_file:
        process_image_test(image_file, "Ivy Gourd")

def test_process_rosary_pea():
    with open(rosary_pea_image, "rb") as image_file:
        process_image_test(image_file, "Rosary Pea")

def test_process_small_water_clover():
    with open(small_water_clover_image, "rb") as image_file:
        process_image_test(image_file, "Small Water Clover")

def test_process_spider_wisp():
    with open(spider_wisp_image, "rb") as image_file:
        process_image_test(image_file, "Spider Wisp")

def test_process_square_stalked_vine():
    with open(square_stalked_vine_image, "rb") as image_file:
        process_image_test(image_file, "Square Stalked Vine")

def test_process_trellis_vine():
    with open(trellis_vine_image, "rb") as image_file:
        process_image_test(image_file, "Trellis Vine")
