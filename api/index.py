import os
import sys

# Crucial: Ensure the root directory is in the python path for Vercel
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from app.main import app
except Exception as e:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    import traceback
    
    app = FastAPI()
    
    @app.get("/")
    async def dashboard_error():
        return JSONResponse({
            "error": "CRITICAL STARTUP ERROR",
            "message": str(e),
            "traceback": traceback.format_exc(),
            "root_dir": root_dir,
            "sys_path": sys.path
        }, status_code=500)

@app.get("/ping")
async def ping():
    return {"status": "ok", "message": "Server is alive!"}

# Export the app for Vercel
app = app
