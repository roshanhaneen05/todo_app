import pytest
from app import create_app
from app.models import Task


@pytest.fixture
def app():
    """Create and configure a new Flask app instance for each test."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
    })
    
    # Reset in-memory database before each test
    Task.reset_test_db()

    yield app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


def test_index_page(client):
    """Test root endpoint returns HTML page."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"TaskMaster" in response.data


def test_health_endpoint(client):
    """Test health status endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["status"] == "healthy"
    assert json_data["database"] == "connected"


def test_get_tasks_empty(client):
    """Test GET /api/tasks returns empty list initially."""
    response = client.get("/api/tasks")
    assert response.status_code == 200
    assert response.get_json() == []


def test_create_task(client):
    """Test POST /api/tasks creates a task."""
    payload = {
        "title": "Build Docker Container",
        "description": "Create production Dockerfile and compose file."
    }
    response = client.post("/api/tasks", json=payload)
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data["id"] == 1
    assert json_data["title"] == "Build Docker Container"
    assert json_data["description"] == "Create production Dockerfile and compose file."
    assert json_data["completed"] is False


def test_create_task_missing_title(client):
    """Test POST /api/tasks fails if title is missing."""
    response = client.post("/api/tasks", json={"description": "No title here"})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_update_task(client):
    """Test PUT /api/tasks/<id> updates existing task."""
    # Create task first
    post_res = client.post("/api/tasks", json={"title": "Original Title"})
    task_id = post_res.get_json()["id"]

    update_payload = {
        "title": "Updated Title",
        "description": "Updated Description",
        "completed": True
    }
    put_res = client.put(f"/api/tasks/{task_id}", json=update_payload)
    assert put_res.status_code == 200
    json_data = put_res.get_json()
    assert json_data["title"] == "Updated Title"
    assert json_data["description"] == "Updated Description"
    assert json_data["completed"] is True


def test_mark_task_complete_and_pending(client):
    """Test PATCH endpoints for marking tasks complete and pending."""
    post_res = client.post("/api/tasks", json={"title": "Test Task"})
    task_id = post_res.get_json()["id"]

    # Mark Complete
    complete_res = client.patch(f"/api/tasks/{task_id}/complete")
    assert complete_res.status_code == 200
    assert complete_res.get_json()["completed"] is True

    # Mark Pending
    pending_res = client.patch(f"/api/tasks/{task_id}/pending")
    assert pending_res.status_code == 200
    assert pending_res.get_json()["completed"] is False


def test_delete_task(client):
    """Test DELETE /api/tasks/<id> removes task."""
    post_res = client.post("/api/tasks", json={"title": "Task to Delete"})
    task_id = post_res.get_json()["id"]

    del_res = client.delete(f"/api/tasks/{task_id}")
    assert del_res.status_code == 200
    assert del_res.get_json()["id"] == task_id

    # Verify task no longer exists
    get_res = client.get("/api/tasks")
    assert len(get_res.get_json()) == 0


def test_nonexistent_task_404(client):
    """Test 404 response when modifying nonexistent task ID."""
    assert client.put("/api/tasks/999", json={"title": "Test"}).status_code == 404
    assert client.patch("/api/tasks/999/complete").status_code == 404
    assert client.patch("/api/tasks/999/pending").status_code == 404
    assert client.delete("/api/tasks/999").status_code == 404
