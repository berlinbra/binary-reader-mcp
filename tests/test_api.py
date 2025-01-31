import pytest
from fastapi.testclient import TestClient
from src.api.routes import router
from fastapi import FastAPI

app = FastAPI()
app.include_router(router)

@pytest.fixture
def client():
    return TestClient(app)

def test_analyze_endpoint_missing_file(client):
    response = client.post("/analyze", json={"file_path": "nonexistent.uasset"})
    assert response.status_code == 400
    assert "File not found" in response.json()["detail"]

def test_analyze_endpoint_invalid_request(client):
    response = client.post("/analyze", json={})
    assert response.status_code == 422  # Validation error

def test_analyze_endpoint_with_mock_file(client, tmp_path):
    # Create a mock .uasset file
    file_path = tmp_path / "test.uasset"
    with open(file_path, "wb") as f:
        f.write(bytes.fromhex('C1832A9E'))
        f.write(b"\x00" * 28)  # Padding for header and metadata
    
    response = client.post("/analyze", json={"file_path": str(file_path)})
    assert response.status_code == 200
    data = response.json()
    assert data["format"] == "unreal"
    assert "header" in data
    assert "metadata" in data