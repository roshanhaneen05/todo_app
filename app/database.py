import os
import time
import logging
import sqlite3
import pymysql
from pymysql.cursors import DictCursor

logger = logging.getLogger(__name__)


class SQLiteCursorWrapper:
    def __init__(self, cursor):
        self._cursor = cursor
        self.lastrowid = None

    def execute(self, sql, params=()):
        sql = sql.replace("%s", "?")
        self._cursor.execute(sql, params)
        self.lastrowid = self._cursor.lastrowid
        return self

    def fetchall(self):
        return [dict(r) for r in self._cursor.fetchall()]

    def fetchone(self):
        r = self._cursor.fetchone()
        return dict(r) if r else None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class SQLiteConnectionWrapper:
    def __init__(self, conn):
        self._conn = conn

    def cursor(self):
        return SQLiteCursorWrapper(self._conn.cursor())

    def close(self):
        self._conn.close()


def get_sqlite_connection():
    """Establish and return SQLite connection for local development without MySQL."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "todo.db")
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.isolation_level = None  # autocommit mode
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                completed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tasks;")
        if cursor.fetchone()[0] == 0:
            cursor.executemany("""
                INSERT INTO tasks (title, description, completed) VALUES (?, ?, ?);
            """, [
                ('Setup Infrastructure', 'Configure Flask application, SQLite/MySQL persistence, and environment setup.', 1),
                ('Implement Flask REST API Endpoints', 'Create GET, POST, PUT, PATCH, and DELETE endpoints with database integration.', 1),
                ('Build Glassmorphism Responsive Frontend', 'Design modern dark UI with real-time stats cards, filter tabs, modal editing, and toast alerts.', 0),
                ('Configure Nginx Reverse Proxy', 'Setup port 80 proxying to internal Flask application with security headers.', 0)
            ])
    return SQLiteConnectionWrapper(conn)


def get_db_connection():
    """
    Establish and return a database connection.
    Attempts MySQL first; falls back to SQLite for local non-Docker development.
    """
    if os.getenv("USE_SQLITE", "").lower() in ("true", "1"):
        return get_sqlite_connection()

    host = os.getenv("MYSQL_HOST", "mysql")
    port = int(os.getenv("MYSQL_PORT", 3306))
    user = os.getenv("MYSQL_USER", "todo_user")
    password = os.getenv("MYSQL_PASSWORD", "todo_password")
    db = os.getenv("MYSQL_DATABASE", "todo_db")

    # Fast check for default non-Docker host 'mysql' which won't resolve locally
    if host == "mysql":
        max_retries = 1
        retry_delay = 0
    else:
        max_retries = 3
        retry_delay = 2

    for attempt in range(1, max_retries + 1):
        try:
            connection = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=db,
                cursorclass=DictCursor,
                autocommit=True,
                connect_timeout=2,
            )
            return connection
        except Exception as err:
            logger.warning(
                f"MySQL connection attempt {attempt}/{max_retries} failed ({err})."
            )
            if attempt < max_retries:
                time.sleep(retry_delay)

    logger.info("MySQL not reachable. Falling back to local SQLite database.")
    return get_sqlite_connection()


def check_db_health():
    """Check database connectivity for health monitoring."""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1;")
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Health check failed to connect to database: {e}")
        return False

