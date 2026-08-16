import logging
from flask import Blueprint, jsonify, render_template, request, current_app
from app.database import check_db_health
from app.models import Task
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST, REGISTRY

logger = logging.getLogger(__name__)

main_bp = Blueprint("main", __name__)

# Register Prometheus metrics safely (handle potential re-imports in testing)
def _get_or_create_counter(name, documentation):
    for collector in list(REGISTRY._names_to_collectors.values()):
        if hasattr(collector, "_name") and collector._name == name:
            return collector
    return Counter(name, documentation)


TASKS_CREATED = _get_or_create_counter("tasks_created_total", "Total Tasks Created")
TASKS_COMPLETED = _get_or_create_counter("tasks_completed_total", "Total Tasks Completed")
HTTP_REQUESTS = _get_or_create_counter("http_requests_total", "Total HTTP Requests")


@main_bp.route("/")
def index():
    """Render application frontend single page interface."""
    return render_template("index.html")


@main_bp.route("/health", methods=["GET"])
def health():
    """Application and database health check endpoint."""
    if current_app.config.get("TESTING", False):
        return jsonify({"status": "healthy", "database": "connected"}), 200

    db_ok = check_db_health()
    status_code = 200 if db_ok else 503
    status_text = "healthy" if db_ok else "unhealthy"
    db_text = "connected" if db_ok else "disconnected"
    return jsonify({"status": status_text, "database": db_text}), status_code


@main_bp.route("/metrics", methods=["GET"])
def metrics():
    """Expose Prometheus application metrics."""
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


@main_bp.route("/api/tasks", methods=["GET"])
def get_tasks():
    """Retrieve all tasks."""
    try:
        tasks = Task.get_all()
        return jsonify(tasks), 200
    except Exception as e:
        logger.error(f"Error fetching tasks: {e}")
        return jsonify({"error": "Failed to fetch tasks"}), 500


@main_bp.route("/api/tasks", methods=["POST"])
def create_task():
    """Create a new task."""
    try:
        data = request.get_json() or {}
        title = data.get("title", "").strip()
        description = data.get("description", "").strip()

        if not title:
            return jsonify({"error": "Task title is required"}), 400

        task = Task.create(title, description)
        TASKS_CREATED.inc()
        logger.info(f"Task created with ID {task['id']}")
        return jsonify(task), 201
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        return jsonify({"error": "Failed to create task"}), 500


@main_bp.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    """Update task details (title, description, completed status)."""
    try:
        data = request.get_json() or {}
        title = data.get("title")
        description = data.get("description")
        completed = data.get("completed")

        if title is not None:
            title = str(title).strip()
            if not title:
                return jsonify({"error": "Task title cannot be empty"}), 400

        task = Task.update(task_id, title=title, description=description, completed=completed)
        if not task:
            return jsonify({"error": "Task not found"}), 404

        logger.info(f"Task {task_id} updated successfully")
        return jsonify(task), 200
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {e}")
        return jsonify({"error": "Failed to update task"}), 500


@main_bp.route("/api/tasks/<int:task_id>/complete", methods=["PATCH"])
def mark_complete(task_id):
    """Mark a task as completed."""
    try:
        task = Task.set_status(task_id, completed=True)
        if not task:
            return jsonify({"error": "Task not found"}), 404

        TASKS_COMPLETED.inc()
        logger.info(f"Task {task_id} marked as completed")
        return jsonify(task), 200
    except Exception as e:
        logger.error(f"Error marking task {task_id} complete: {e}")
        return jsonify({"error": "Failed to update task status"}), 500


@main_bp.route("/api/tasks/<int:task_id>/pending", methods=["PATCH"])
def mark_pending(task_id):
    """Mark a task as pending."""
    try:
        task = Task.set_status(task_id, completed=False)
        if not task:
            return jsonify({"error": "Task not found"}), 404

        logger.info(f"Task {task_id} marked as pending")
        return jsonify(task), 200
    except Exception as e:
        logger.error(f"Error marking task {task_id} pending: {e}")
        return jsonify({"error": "Failed to update task status"}), 500


@main_bp.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    """Delete a task by ID."""
    try:
        success = Task.delete(task_id)
        if not success:
            return jsonify({"error": "Task not found"}), 404

        logger.info(f"Task {task_id} deleted successfully")
        return jsonify({"message": "Task deleted successfully", "id": task_id}), 200
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {e}")
        return jsonify({"error": "Failed to delete task"}), 500
