from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from typing import Generator
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./finance.db")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database with tables"""
    from models import Base
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

def seed_default_categories():
    """Seed database with default Uzbek categories"""
    from models import Category, TransactionType
    
    db = SessionLocal()
    
    # Check if default categories already exist
    existing = db.query(Category).filter(Category.is_default == True).first()
    if existing:
        print("✅ Default categories already exist")
        db.close()
        return
    
    # Default expense categories in Uzbek
    expense_categories = [
        {"name": "Oziq-ovqat", "icon": "🍕", "color": "#EF4444"},
        {"name": "Transport", "icon": "🚗", "color": "#F59E0B"},
        {"name": "Uy-joy", "icon": "🏠", "color": "#8B5CF6"},
        {"name": "Kommunal", "icon": "💡", "color": "#06B6D4"},
        {"name": "Sog'liq", "icon": "⚕️", "color": "#EC4899"},
        {"name": "O'yin-kulgi", "icon": "🎮", "color": "#10B981"},
        {"name": "Kiyim", "icon": "👕", "color": "#6366F1"},
        {"name": "Ta'lim", "icon": "📚", "color": "#F97316"},
        {"name": "Boshqa", "icon": "📦", "color": "#64748B"},
    ]
    
    # Default income categories in Uzbek
    income_categories = [
        {"name": "Maosh", "icon": "💰", "color": "#10B981"},
        {"name": "Freelance", "icon": "💻", "color": "#3B82F6"},
        {"name": "Biznes", "icon": "🏢", "color": "#8B5CF6"},
        {"name": "Investitsiya", "icon": "📈", "color": "#059669"},
        {"name": "Sovg'a", "icon": "🎁", "color": "#EC4899"},
        {"name": "Boshqa", "icon": "💵", "color": "#64748B"},
    ]
    
    # Insert expense categories
    for cat_data in expense_categories:
        category = Category(
            user_id=None,
            type=TransactionType.EXPENSE,
            is_default=True,
            **cat_data
        )
        db.add(category)
    
    # Insert income categories
    for cat_data in income_categories:
        category = Category(
            user_id=None,
            type=TransactionType.INCOME,
            is_default=True,
            **cat_data
        )
        db.add(category)
    
    db.commit()
    db.close()
    print("✅ Default categories created successfully!")

if __name__ == "__main__":
    init_db()
    seed_default_categories()
