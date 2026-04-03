import os
import uvicorn
from fastapi import FastAPI, Request, Form, Depends, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.models import init_db, SessionLocal, Lead, Message, BusinessProfile, KnowledgeFile
from app.ai_service import ai_service
from app.whatsapp_service import whatsapp_service

load_dotenv()

app = FastAPI(title="Leverage Logic Ventures - AI Manager Pro")

APP_DIR = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(os.path.dirname(APP_DIR), "static")
templates_path = os.path.join(os.path.dirname(APP_DIR), "templates")

if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

templates = Jinja2Templates(directory=templates_path)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
                greeting_message="Hi! I'm the AI assistant for Leverage Logic Ventures."
            )
            db.add(profile)
            db.commit()
        db.close()
    except Exception as e:
        print(f"Startup DB Error: {e}")

startup_init()

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    profile = db.query(BusinessProfile).first()
    files = db.query(KnowledgeFile).all()
    leads = db.query(Lead).all()
    return templates.TemplateResponse(request=request, name="index.html", context={"profile": profile, "files": files, "leads": leads})

@app.post("/update-wizard")
async def update_wizard(
    brand_name: str = Form(...), website_link: str = Form(...), brand_tone: str = Form(...),
    primary_goal: str = Form(...), common_objections: str = Form(...), greeting_message: str = Form(...),
    db: Session = Depends(get_db)
):
    profile = db.query(BusinessProfile).first()
    profile.brand_name, profile.website_link, profile.brand_tone = brand_name, website_link, brand_tone
    profile.primary_goal, profile.common_objections, profile.greeting_message = primary_goal, common_objections, greeting_message
    db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.post("/update-gateway")
async def update_gateway(gateway_url: str = Form(...), gateway_api_key: str = Form(...), db: Session = Depends(get_db)):
    profile = db.query(BusinessProfile).first()
    profile.gateway_url = gateway_url
    profile.gateway_api_key = gateway_api_key
    db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.post("/upload-knowledge")
async def upload_knowledge(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    text_content = content.decode('utf-8', errors='ignore')
    db.add(KnowledgeFile(filename=file.filename, content=text_content))
    db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.post("/delete-knowledge/{file_id}")
async def delete_knowledge(file_id: int, db: Session = Depends(get_db)):
    file_obj = db.query(KnowledgeFile).filter(KnowledgeFile.id == file_id).first()
    if file_obj:
        db.delete(file_obj)
        db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.get("/get-qr")
async def get_qr(db: Session = Depends(get_db)):
    profile = db.query(BusinessProfile).first()
    return await whatsapp_service.get_qr_code(profile, "Main")

@app.post("/link-number")
async def link_number(phone_number: str = Form(...), db: Session = Depends(get_db)):
    profile = db.query(BusinessProfile).first()
    result = await whatsapp_service.request_pairing_code(profile, "Main", phone_number)
    return JSONResponse(content=result)

@app.post("/webhook")
async def whatsapp_webhook(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    try:
        if data.get("event") == "messages.upsert":
            msg_data = data["data"]["message"]
            phone = msg_data["key"]["remoteJid"].split("@")[0]
            text = msg_data["message"].get("conversation", "") or msg_data["message"].get("extendedTextMessage", {}).get("text", "")
            if not text: return {"status": "ignored"}

            lead = db.query(Lead).filter(Lead.phone_number == phone).first()
            if not lead:
                lead = Lead(phone_number=phone)
                db.add(lead); db.commit(); db.refresh(lead)

            db.add(Message(lead_id=lead.id, role="user", content=text)); db.commit()

            profile = db.query(BusinessProfile).first()
            all_files = db.query(KnowledgeFile).all()
            kb = "\n---\n".join([f.content for f in all_files])
            
            history_objs = db.query(Message).filter(Message.lead_id == lead.id).order_by(Message.timestamp.desc()).limit(5).all()
            history = [{"role": m.role, "content": m.content} for m in reversed(history_objs[:-1])]

            ai_resp = await ai_service.generate_response(text, history, profile, kb)
            db.add(Message(lead_id=lead.id, role="assistant", content=ai_resp)); db.commit()

            await whatsapp_service.send_text(profile, "Main", phone, ai_resp)
            return {"status": "success"}
    except Exception as e: print(f"Webhook Error: {e}")
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)
