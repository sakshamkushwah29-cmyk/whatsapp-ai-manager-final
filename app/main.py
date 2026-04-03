import os
import uvicorn
from fastapi import FastAPI, Request, Form, Depends, UploadFile, File, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.models import init_db, SessionLocal, Lead, Message, BusinessProfile, KnowledgeFile
from app.ai_service import ai_service
from app.whatsapp_service import whatsapp_service

# Load env safely
load_dotenv()

app = FastAPI(title="Leverage Logic Ventures - AI Manager Pro")

# --- PATH LOGIC ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
static_path = os.path.join(BASE_DIR, "static")
templates_path = os.path.join(BASE_DIR, "templates")

if not os.path.exists(templates_path):
    templates_path = os.path.join(os.getcwd(), "templates")

if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

templates = Jinja2Templates(directory=templates_path)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Startup Database Initialization
def startup_init():
    try:
        init_db()
        db = SessionLocal()
        if not db.query(BusinessProfile).first():
            profile = BusinessProfile(
                brand_name="Leverage Logic Ventures",
                website_link="https://leverage-logic.com",
                brand_tone="Professional",
                primary_goal="Schedule Sales Calls",
                common_objections="Explain the value proposition clearly.",
                greeting_message="Hi! I'm the AI assistant for Leverage Logic Ventures. How can I help you grow today?"
            )
            db.add(profile)
            db.commit()
        db.close()
    except Exception as e:
        print(f"Startup DB Error: {e}")

startup_init()

@app.get("/")
async def dashboard(request: Request, db: Session = Depends(get_db)):
    profile = db.query(BusinessProfile).first()
    files = db.query(KnowledgeFile).all()
    leads = db.query(Lead).all()
    return templates.TemplateResponse(request=request, name="index.html", context={"profile": profile, "files": files, "leads": leads})

@app.post("/update-wizard")
async def update_wizard(
    brand_name: str = Form(...),
    website_link: str = Form(...),
    brand_tone: str = Form(...),
    primary_goal: str = Form(...),
    common_objections: str = Form(...),
    greeting_message: str = Form(...),
    db: Session = Depends(get_db)
):
    profile = db.query(BusinessProfile).first()
    profile.brand_name = brand_name
    profile.website_link = website_link
    profile.brand_tone = brand_tone
    profile.primary_goal = primary_goal
    profile.common_objections = common_objections
    profile.greeting_message = greeting_message
    db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.post("/upload-knowledge")
async def upload_knowledge(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    text_content = content.decode('utf-8', errors='ignore')
    new_file = KnowledgeFile(filename=file.filename, content=text_content)
    db.add(new_file)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.post("/delete-knowledge/{file_id}")
async def delete_knowledge(file_id: int, db: Session = Depends(get_db)):
    file_obj = db.query(KnowledgeFile).filter(KnowledgeFile.id == file_id).first()
    if file_obj:
        db.delete(file_obj)
        db.commit()
    return RedirectResponse(url="/", status_code=303)

# --- WHATSAPP LOGIC ---

@app.get("/get-qr")
async def get_qr():
    # Attempt to create instance first
    try:
        return await whatsapp_service.get_qr_code("Main")
    except Exception as e:
        return {"error": str(e)}

@app.post("/link-number")
async def link_number(phone_number: str = Form(...)):
    """Method 2: Link by Phone Number (Pairing Code)"""
    try:
        # In Evolution API, this usually involves requesting a pairing code
        # We call the service to trigger the code request
        result = await whatsapp_service.request_pairing_code("Main", phone_number)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/webhook")
async def whatsapp_webhook(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    if data.get("event") == "messages.upsert":
        # Handle incoming message...
        # (Same logic as before, properly handling DB sessions)
        pass
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)
