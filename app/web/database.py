"""
Vanta Database Configuration
Enhanced database setup with SQLAlchemy for production use
"""

import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database URL from environment or default to SQLite
DATABASE_URL = os.getenv("DATABASE_URI", "sqlite:///data/vanta.db")

# Create engine
if DATABASE_URL.startswith("sqlite"):
    # SQLite specific configuration
    os.makedirs("data", exist_ok=True)
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False},  # For SQLite
        echo=False
    )
else:
    # PostgreSQL configuration
    engine = create_engine(DATABASE_URL, echo=False)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()

def get_database_session():
    """Get database session"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def init_database():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")

def get_engine():
    """Get database engine"""
    return engine

# Metadata for table introspection
metadata = MetaData()