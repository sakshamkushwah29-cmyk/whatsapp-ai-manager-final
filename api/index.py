import os
import sys

# Ensure the root directory is in the python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from app.main import app
except Exception as e:
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse
    import traceback
    
    app = FastAPI()
    
    @app.get("/")
    async def diagnostic_route():
        error_msg = traceback.format_exc()
        content = f"""
        <html>
        <head><title>AI Manager Diagnostic</title></head>
        <body style="font-family: sans-serif; padding: 40px; background: #fef2f2;">
            <h1 style="color: #991b1b;">⚠️ Startup Error</h1>
            <p>The app failed to start on Vercel. Here is the technical reason:</p>
            <pre style="background: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #fee2e2; overflow: auto;">{error_msg}</pre>
            <hr>
            <h3>Environment Check:</h3>
            <ul>
                <li><strong>CWD:</strong> {os.getcwd()}</li>
                <li><strong>File:</strong> {__file__}</li>
                <li><strong>Python Path:</strong> {sys.path}</li>
            </ul>
        </body>
        </html>
        """
        return HTMLResponse(content=content, status_code=500)
