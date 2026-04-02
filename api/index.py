import os
import sys

# Ensure the root directory is in the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.main import app
except Exception as e:
    from fastapi import FastAPI
    app = FastAPI()
    
    @app.get("/")
    async def error_route():
        return {
            "error": "Failed to import app.main",
            "details": str(e),
            "sys_path": sys.path,
            "cwd": os.getcwd()
        }
