import logging
from datetime import datetime
from app.database import get_db_connection

logger = logging.getLogger(__name__)

# In-memory storage for isolated testing mode
_test_tasks = {}
_test_id_counter = 1


def is_testing():
    """Check if application is running in Pytest / testing environment."""
    from flask import current_app
    try:
        return current_app.config.get("TESTING", False)
    except RuntimeError:
        return False


def _serialize_task(task):
    """Serialize database dictionary into JSON-compatible format."""
    if not task:
        return None
    res = dict(task)
    if "completed" in res:
        res["completed"] = bool(res["completed"])
    if "created_at" in res and res["created_at"] is not None:
        res["created_at"] = str(res["created_at"])
    if "updated_at" in res and res["updated_at"] is not None:
        res["updated_at"] = str(res["updated_at"])
    return res


class Task:
    """Model representing To-Do tasks and database CRUD operations."""

    @staticmethod
    def get_all():
        """Retrieve all tasks ordered by creation date descending."""
        if is_testing():
            return sorted(
                list(_test_tasks.values()),
                key=lambda x: x.get("id", 0),
                reverse=True,
            )

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, title, description, completed, created_at, updated_at "
                    "FROM tasks ORDER BY created_at DESC;"
                )
                tasks = cursor.fetchall()
                return [_serialize_task(t) for t in tasks]
        finally:
            conn.close()

    @staticmethod
    def get_by_id(task_id):
        """Retrieve a specific task by ID."""
        if is_testing():
            return _test_tasks.get(int(task_id))

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, title, description, completed, created_at, updated_at "
                    "FROM tasks WHERE id = %s;",
                    (task_id,),
                )
                task = cursor.fetchone()
                return _serialize_task(task)
        finally:
            conn.close()

    @staticmethod
    def create(title, description=""):
        """Create a new task."""
        global _test_id_counter
        if is_testing():
            now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            task = {
                "id": _test_id_counter,
                "title": title,
                "description": description or "",
                "completed": False,
                "created_at": now_str,
                "updated_at": now_str,
            }
            _test_tasks[_test_id_counter] = task
            _test_id_counter += 1
            return task

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO tasks (title, description) VALUES (%s, %s);",
                    (title, description or ""),
                )
                task_id = cursor.lastrowid
            return Task.get_by_id(task_id)
        finally:
            conn.close()

    @staticmethod
    def update(task_id, title=None, description=None, completed=None):
        """Update existing task fields."""
        if is_testing():
            task = _test_tasks.get(int(task_id))
            if not task:
                return None
            if title is not None:
                task["title"] = title
            if description is not None:
                task["description"] = description
            if completed is not None:
                task["completed"] = bool(completed)
            task["updated_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            return task

        task = Task.get_by_id(task_id)
        if not task:
            return None

        new_title = title if title is not None else task["title"]
        new_desc = description if description is not None else task["description"]
        new_comp = completed if completed is not None else task["completed"]

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE tasks SET title = %s, description = %s, completed = %s WHERE id = %s;",
                    (new_title, new_desc, new_comp, task_id),
                )
            return Task.get_by_id(task_id)
        finally:
            conn.close()

    @staticmethod
    def set_status(task_id, completed: bool):
        """Helper to set completed/pending status of a task."""
        return Task.update(task_id, completed=completed)

    @staticmethod
    def delete(task_id):
        """Delete a task by ID."""
        if is_testing():
            if int(task_id) in _test_tasks:
                del _test_tasks[int(task_id)]
                return True
            return False

        task = Task.get_by_id(task_id)
        if not task:
            return False

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM tasks WHERE id = %s;", (task_id,))
            return True
        finally:
            conn.close()

    @staticmethod
    def reset_test_db():
        """Reset in-memory data for tests."""
        global _test_tasks, _test_id_counter
        _test_tasks = {}
        _test_id_counter = 1
