-- TaskMaster Pro MySQL Database Schema Initialization
CREATE DATABASE IF NOT EXISTS todo_db;
USE todo_db;

CREATE TABLE IF NOT EXISTS tasks (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert Seed Initial Tasks
INSERT INTO tasks (title, description, completed) VALUES
('Setup Docker & Docker Compose Infrastructure', 'Configure custom todo-network, persistent MySQL volume, and multi-stage container build.', TRUE),
('Implement Flask REST API Endpoints', 'Create GET, POST, PUT, PATCH, and DELETE endpoints with MySQL database integration.', TRUE),
('Build Glassmorphism Responsive Frontend', 'Design modern dark UI with real-time stats cards, filter tabs, modal editing, and toast alerts.', FALSE),
('Configure Nginx Reverse Proxy', 'Setup port 80 proxying to internal Flask application on container network with security headers.', FALSE);
