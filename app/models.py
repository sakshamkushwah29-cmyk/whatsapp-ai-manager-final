import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

# For Vercel, use /tmp/ as it's the only writable directory
if os.environ.get("VERCEL"):
    DATABASE_URL = "sqlite:////tmp/whatsapp_manager.db"
else:
    DATABASE_URL = "sqlite:///./whatsapp_manager.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class BusinessProfile(Base):
    __tablename__ = "business_profile"
    id = Column(Integer, primary_key=True)
    brand_name = Column(String)
    website_link = Column(String)
    brand_tone = Column(String)
    primary_goal = Column(Text)
    common_objections = Column(Text)
    greeting_message = Column(Text)
    whatsapp_number = Column(String, nullable=True)
    is_connected = Column(Boolean, default=False)

class KnowledgeFile(Base):
    __tablename__ = "knowledge_files"
    id = Column(Integer, primary_key=True)
    filename = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Lead(Base):
    __tablename__ = "leads"
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, unique=True, index=True)
    name = Column(String, nullable=True)
    status = Column(String, default="new")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"))
    role = Column(String)
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

def init_db():
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Error initializing DB: {e}")
