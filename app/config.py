import os


class Config:
    """Production and development configuration loaded from environment variables."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # MySQL Database Connection Settings
    MYSQL_HOST = os.getenv("MYSQL_HOST", "mysql")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
    MYSQL_USER = os.getenv("MYSQL_USER", "todo_user")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "todo_password")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "todo_db")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
