import os
import uvicorn
from fastapi import FastAPI, Request, Form, Depends, UploadFile, File, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.models import init_db, SessionLocal, Lead, Message, BusinessProfile, KnowledgeFile
from app.ai_service import ai_service
from app.whatsapp_service import whatsapp_service

# Load env safely
load_dotenv()

app = FastAPI(title="WhatsApp AI Manager Business Pro")

# --- PATH LOGIC START ---
# We calculate paths relative to the root of the project to be safe for Vercel.
APP_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(APP_DIR)
TEMPLATES_DIR = os.path.join(APP_DIR, "templates")
STATIC_DIR = os.path.join(APP_DIR, "static")

# If on Vercel, paths can be tricky. We'll check multiple locations if needed.
if not os.path.exists(TEMPLATES_DIR):
    TEMPLATES_DIR = "/var/task/app/templates" # Vercel default task path

if not os.path.exists(STATIC_DIR):
    STATIC_DIR = "/var/task/app/static"

# Mount Static if it exists
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Initialize Templates
if os.path.exists(TEMPLATES_DIR):
    templates = Jinja2Templates(directory=TEMPLATES_DIR)
else:
    # This will be caught by the except block in api/index.py if it crashes here
    raise Exception(f"CRITICAL: Templates directory not found at {TEMPLATES_DIR}")
# --- PATH LOGIC END ---

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
                brand_name="My Brand",
                website_link="https://mysite.com",
                brand_tone="Professional",
                primary_goal="Help customers",
                common_objections="None",
                greeting_message="Hi! How can I help?"
            )
            db.add(profile)
            db.commit()
        db.close()
    except Exception as e:
        print(f"Startup DB Error: {e}")

# Run once during module import
startup_init()

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    try:
        profile = db.query(BusinessProfile).first()
        files = db.query(KnowledgeFile).all()
        leads = db.query(Lead).all()
        
        return templates.TemplateResponse("index.html", {
            "request": request, 
            "profile": profile, 
            "files": files, 
            "leads": leads
        })
    except Exception as e:
        import traceback
        err = traceback.format_exc()
        return HTMLResponse(
            content=f"<html><body style='padding:50px; font-family:sans-serif;'><h1>❌ Dashboard Error</h1><pre style='background:#f1f1f1; padding:20px;'>{err}</pre></body></html>",
            status_code=500
        )

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
    try:
        profile = db.query(BusinessProfile).first()
        if not profile:
            profile = BusinessProfile()
            db.add(profile)
            
        profile.brand_name = brand_name
        profile.website_link = website_link
        profile.brand_tone = brand_tone
        profile.primary_goal = primary_goal
        profile.common_objections = common_objections
        profile.greeting_message = greeting_message
        db.commit()
    except Exception as e:
        print(f"Update Wizard Error: {e}")
    return RedirectResponse(url="/", status_code=303)

@app.post("/upload-knowledge")
async def upload_knowledge(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        content = await file.read()
        text_content = content.decode('utf-8', errors='ignore')
        new_file = KnowledgeFile(filename=file.filename, content=text_content)
        db.add(new_file)
        db.commit()
    except Exception as e:
        print(f"Upload Error: {e}")
    return RedirectResponse(url="/", status_code=303)

@app.get("/get-qr")
async def get_qr():
    try:
        return await whatsapp_service.get_qr_code("Main")
    except Exception as e:
        return {"error": str(e)}

@app.post("/webhook")
async def whatsapp_webhook(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        if data.get("event") == "messages.upsert":
            message_data = data["data"]["message"]
            remote_jid = message_data["key"]["remoteJid"]
            phone_number = remote_jid.split("@")[0]
            
            text = message_data["message"].get("conversation", "") or \
                   message_data["message"].get("extendedTextMessage", {}).get("text", "")

            if not text: return {"status": "ignored"}

            lead = db.query(Lead).filter(Lead.phone_number == phone_number).first()
            if not lead:
                lead = Lead(phone_number=phone_number)
                db.add(lead)
                db.commit()
                db.refresh(lead)

            db.add(Message(lead_id=lead.id, role="user", content=text))
            db.commit()

            profile = db.query(BusinessProfile).first()
            all_files = db.query(KnowledgeFile).all()
            knowledge_base = "\n---\n".join([f.content for f in all_files])
            
            history_objs = db.query(Message).filter(Message.lead_id == lead.id).order_by(Message.timestamp.desc()).limit(5).all()
            history = [{"role": m.role, "content": m.content} for m in reversed(history_objs[:-1])]

            ai_response = ai_service.generate_response(text, history, profile, knowledge_base)

            db.add(Message(lead_id=lead.id, role="assistant", content=ai_response))
            db.commit()

            await whatsapp_service.send_text("Main", phone_number, ai_response)
            return {"status": "success"}
    except Exception as e:
        print(f"Webhook Error: {e}")
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)
