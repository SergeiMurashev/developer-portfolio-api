from fastapi.testclient import TestClient

from app.main import app


def test_contact_validation() -> None:
    client = TestClient(app)
    response = client.post("/api/contact", json={"name": "", "phone": "1", "email": "bad", "comment": ""})
    assert response.status_code == 422

