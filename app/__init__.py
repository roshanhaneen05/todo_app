import logging
import os
from flask import Flask
from app.config import Config


def create_app(config_class=Config):
    """Application Factory function."""
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    template_dir = os.path.join(base_dir, "templates")
    static_dir = os.path.join(base_dir, "static")

    app = Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir,
    )
    app.config.from_object(config_class)

    # Configure application logging
    log_level_str = app.config.get("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format="[%(asctime)s] %(levelname)s [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    app.logger.setLevel(log_level)

    # Register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app


# Expose default WSGI app instance for Gunicorn / server execution
app = create_app()
