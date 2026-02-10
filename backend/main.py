from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db, init_db, seed_default_categories
from models import User, Transaction, Category, TransactionType
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import os
import hashlib
import hmac
from urllib.parse import parse_qsl

app = FastAPI(title="Finance Bot API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Pydantic models
class TransactionCreate(BaseModel):
    type: str
    amount: float
    category_id: Optional[int] = None
    description: Optional[str] = None
    transaction_date: Optional[datetime] = None

class TransactionResponse(BaseModel):
    id: int
    type: str
    amount: float
    category_id: Optional[int]
    category_name: Optional[str]
    description: Optional[str]
    transaction_date: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

class CategoryResponse(BaseModel):
    id: int
    name: str
    type: str
    icon: str
    color: str
    is_default: bool
    
    class Config:
        from_attributes = True

class SummaryResponse(BaseModel):
    total_income: float
    total_expense: float
    balance: float
    transaction_count: int

# Authentication
def verify_telegram_webapp_data(init_data: str) -> Optional[int]:
    """Verify Telegram WebApp initData and return user telegram_id"""
    try:
        parsed_data = dict(parse_qsl(init_data))
        received_hash = parsed_data.pop('hash', None)
        
        if not received_hash:
            return None
        
        # Create data check string
        data_check_arr = [f"{k}={v}" for k, v in sorted(parsed_data.items())]
        data_check_string = '\n'.join(data_check_arr)
        
        # Calculate hash
        secret_key = hmac.new("WebAppData".encode(), BOT_TOKEN.encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        
        if calculated_hash == received_hash:
            # Extract user data
            import json
            user_data = json.loads(parsed_data.get('user', '{}'))
            return user_data.get('id')
        
        return None
    except:
        return None

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    """Get current authenticated user"""
    init_data = credentials.credentials
    telegram_id = verify_telegram_webapp_data(init_data)
    
    if not telegram_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Noto'g'ri autentifikatsiya ma'lumotlari"
        )
    
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Foydalanuvchi topilmadi"
        )
    
    return user

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    seed_default_categories()
    print("✅ API ishga tushdi!")

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Finance Bot API", "status": "running"}

# User endpoints
@app.get("/api/user/profile")
def get_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return {
        "telegram_id": current_user.telegram_id,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "username": current_user.username,
        "currency": current_user.currency,
        "theme": current_user.theme,
        "language": current_user.language
    }

# Transaction endpoints
@app.get("/api/transactions", response_model=List[TransactionResponse])
def get_transactions(
    skip: int = 0,
    limit: int = 100,
    type: Optional[str] = None,
    category_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user transactions with filters"""
    query = db.query(Transaction).filter(Transaction.user_id == current_user.telegram_id)
    
    if type:
        query = query.filter(Transaction.type == type)
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    if start_date:
        query = query.filter(Transaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(Transaction.transaction_date <= end_date)
    
    transactions = query.order_by(Transaction.transaction_date.desc()).offset(skip).limit(limit).all()
    
    # Add category names
    result = []
    for t in transactions:
        trans_dict = {
            "id": t.id,
            "type": t.type.value,
            "amount": t.amount,
            "category_id": t.category_id,
            "category_name": t.category.name if t.category else None,
            "description": t.description,
            "transaction_date": t.transaction_date,
            "created_at": t.created_at
        }
        result.append(trans_dict)
    
    return result

@app.post("/api/transactions", response_model=TransactionResponse)
def create_transaction(
    transaction: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new transaction"""
    new_transaction = Transaction(
        user_id=current_user.telegram_id,
        type=TransactionType.INCOME if transaction.type == "income" else TransactionType.EXPENSE,
        amount=transaction.amount,
        category_id=transaction.category_id,
        description=transaction.description,
        transaction_date=transaction.transaction_date or datetime.now()
    )
    
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    
    return {
        "id": new_transaction.id,
        "type": new_transaction.type.value,
        "amount": new_transaction.amount,
        "category_id": new_transaction.category_id,
        "category_name": new_transaction.category.name if new_transaction.category else None,
        "description": new_transaction.description,
        "transaction_date": new_transaction.transaction_date,
        "created_at": new_transaction.created_at
    }

@app.delete("/api/transactions/{transaction_id}")
def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a transaction"""
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.telegram_id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Tranzaksiya topilmadi")
    
    db.delete(transaction)
    db.commit()
    
    return {"message": "Tranzaksiya o'chirildi"}

# Analytics endpoints
@app.get("/api/analytics/summary", response_model=SummaryResponse)
def get_summary(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get financial summary for specified period"""
    start_date = datetime.now() - timedelta(days=days)
    
    income = db.query(Transaction).filter(
        Transaction.user_id == current_user.telegram_id,
        Transaction.type == TransactionType.INCOME,
        Transaction.transaction_date >= start_date
    ).all()
    
    expense = db.query(Transaction).filter(
        Transaction.user_id == current_user.telegram_id,
        Transaction.type == TransactionType.EXPENSE,
        Transaction.transaction_date >= start_date
    ).all()
    
    total_income = sum(t.amount for t in income)
    total_expense = sum(t.amount for t in expense)
    
    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": total_income - total_expense,
        "transaction_count": len(income) + len(expense)
    }

@app.get("/api/analytics/by-category")
def get_category_breakdown(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get spending breakdown by category"""
    start_date = datetime.now() - timedelta(days=days)
    
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.telegram_id,
        Transaction.transaction_date >= start_date
    ).all()
    
    # Group by category
    category_totals = {}
    for t in transactions:
        category_name = t.category.name if t.category else "Boshqa"
        if category_name not in category_totals:
            category_totals[category_name] = {
                "income": 0,
                "expense": 0,
                "icon": t.category.icon if t.category else "📦",
                "color": t.category.color if t.category else "#64748B"
            }
        
        if t.type == TransactionType.INCOME:
            category_totals[category_name]["income"] += t.amount
        else:
            category_totals[category_name]["expense"] += t.amount
    
    return category_totals

# Category endpoints
@app.get("/api/categories", response_model=List[CategoryResponse])
def get_categories(
    type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all categories (default + user custom)"""
    query = db.query(Category).filter(
        (Category.user_id == current_user.telegram_id) | (Category.is_default == True)
    )
    
    if type:
        query = query.filter(Category.type == type)
    
    categories = query.all()
    return categories

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
