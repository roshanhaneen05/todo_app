import os
import sys

# Ensure root folder is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

app = create_app()

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 5000))
    print(f"\nTaskMaster Pro To-Do App is running at http://{host}:{port}/\n")
    app.run(host=host, port=port, debug=True)
