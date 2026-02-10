from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters, ConversationHandler
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from models import User, Transaction, Category, TransactionType
from database import get_db, SessionLocal
from messages import *
import os
import re

# Get bot token from environment
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBAPP_URL = os.getenv("FRONTEND_URL", "https://your-domain.com")

# Conversation states
WAITING_AMOUNT, WAITING_DESCRIPTION = range(2)

def get_user_balance(db: Session, telegram_id: int) -> float:
    """Calculate user's current balance"""
    income = db.query(Transaction).filter(
        Transaction.user_id == telegram_id,
        Transaction.type == TransactionType.INCOME
    ).with_entities(Transaction.amount).all()
    
    expense = db.query(Transaction).filter(
        Transaction.user_id == telegram_id,
        Transaction.type == TransactionType.EXPENSE
    ).with_entities(Transaction.amount).all()
    
    total_income = sum(t[0] for t in income)
    total_expense = sum(t[0] for t in expense)
    
    return total_income - total_expense

def parse_transaction_command(text: str) -> tuple:
    """Parse transaction command: /kirim 50000 taxi"""
    parts = text.split(maxsplit=2)
    
    if len(parts) < 2:
        return None, None
    
    try:
        amount = float(parts[1].replace(",", "").replace(" ", ""))
        description = parts[2] if len(parts) > 2 else "Tavsif yo'q"
        return amount, description
    except ValueError:
        return None, None

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    db = SessionLocal()
    
    # Check if user exists
    existing_user = db.query(User).filter(User.telegram_id == user.id).first()
    
    if not existing_user:
        # Create new user
        new_user = User(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        db.add(new_user)
        db.commit()
    
    db.close()
    
    # Send welcome message with keyboard
    await update.message.reply_text(
        WELCOME_MESSAGE,
        reply_markup=get_main_keyboard()
    )

async def income_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /kirim command"""
    db = SessionLocal()
    user_id = update.effective_user.id
    
    # Parse command
    amount, description = parse_transaction_command(update.message.text)
    
    if amount is None or amount <= 0:
        await update.message.reply_text(INVALID_AMOUNT)
        db.close()
        return
    
    # Get or create default income category
    category = db.query(Category).filter(
        Category.is_default == True,
        Category.type == TransactionType.INCOME,
        Category.name == "Boshqa"
    ).first()
    
    # Create transaction
    transaction = Transaction(
        user_id=user_id,
        type=TransactionType.INCOME,
        amount=amount,
        category_id=category.id if category else None,
        description=description,
        transaction_date=datetime.now()
    )
    
    db.add(transaction)
    db.commit()
    
    # Get updated balance
    balance = get_user_balance(db, user_id)
    
    # Send confirmation
    message = INCOME_ADDED.format(
        amount=amount,
        category=category.name if category else "Boshqa",
        description=description,
        date=datetime.now().strftime("%d.%m.%Y %H:%M"),
        balance=balance
    )
    
    # Add undo button
    keyboard = [[InlineKeyboardButton("🔙 Bekor qilish", callback_data=f"undo_{transaction.id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(message, reply_markup=reply_markup)
    db.close()

async def expense_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /chiqim command"""
    db = SessionLocal()
    user_id = update.effective_user.id
    
    # Parse command
    amount, description = parse_transaction_command(update.message.text)
    
    if amount is None or amount <= 0:
        await update.message.reply_text(INVALID_AMOUNT)
        db.close()
        return
    
    # Get or create default expense category
    category = db.query(Category).filter(
        Category.is_default == True,
        Category.type == TransactionType.EXPENSE,
        Category.name == "Boshqa"
    ).first()
    
    # Create transaction
    transaction = Transaction(
        user_id=user_id,
        type=TransactionType.EXPENSE,
        amount=amount,
        category_id=category.id if category else None,
        description=description,
        transaction_date=datetime.now()
    )
    
    db.add(transaction)
    db.commit()
    
    # Get updated balance
    balance = get_user_balance(db, user_id)
    
    # Send confirmation
    message = EXPENSE_ADDED.format(
        amount=amount,
        category=category.name if category else "Boshqa",
        description=description,
        date=datetime.now().strftime("%d.%m.%Y %H:%M"),
        balance=balance
    )
    
    # Add undo button
    keyboard = [[InlineKeyboardButton("🔙 Bekor qilish", callback_data=f"undo_{transaction.id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(message, reply_markup=reply_markup)
    db.close()

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /balans command"""
    db = SessionLocal()
    user_id = update.effective_user.id
    
    # Get current balance
    balance = get_user_balance(db, user_id)
    
    # Get this month's stats
    now = datetime.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    month_income = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.type == TransactionType.INCOME,
        Transaction.transaction_date >= month_start
    ).with_entities(Transaction.amount).all()
    
    month_expense = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.type == TransactionType.EXPENSE,
        Transaction.transaction_date >= month_start
    ).with_entities(Transaction.amount).all()
    
    total_income = sum(t[0] for t in month_income)
    total_expense = sum(t[0] for t in month_expense)
    
    message = BALANCE_MESSAGE.format(
        balance=balance,
        income=total_income,
        expense=total_expense,
        diff=total_income - total_expense,
        date=now.strftime("%d.%m.%Y %H:%M")
    )
    
    await update.message.reply_text(message)
    db.close()

async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /bugun command"""
    db = SessionLocal()
    user_id = update.effective_user.id
    
    # Get today's transactions
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    today_income = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.type == TransactionType.INCOME,
        Transaction.transaction_date >= today_start
    ).all()
    
    today_expense = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.type == TransactionType.EXPENSE,
        Transaction.transaction_date >= today_start
    ).all()
    
    total_income = sum(t.amount for t in today_income)
    total_expense = sum(t.amount for t in today_expense)
    count = len(today_income) + len(today_expense)
    
    message = TODAY_SUMMARY.format(
        income=total_income,
        expense=total_expense,
        net=total_income - total_expense,
        count=count
    )
    
    await update.message.reply_text(message)
    db.close()

async def week_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /hafta command"""
    db = SessionLocal()
    user_id = update.effective_user.id
    
    # Get this week's transactions
    week_start = datetime.now() - timedelta(days=7)
    
    week_income = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.type == TransactionType.INCOME,
        Transaction.transaction_date >= week_start
    ).all()
    
    week_expense = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.type == TransactionType.EXPENSE,
        Transaction.transaction_date >= week_start
    ).all()
    
    total_income = sum(t.amount for t in week_income)
    total_expense = sum(t.amount for t in week_expense)
    count = len(week_income) + len(week_expense)
    avg_daily = total_expense / 7 if total_expense > 0 else 0
    
    message = WEEK_SUMMARY.format(
        income=total_income,
        expense=total_expense,
        net=total_income - total_expense,
        count=count,
        avg=avg_daily
    )
    
    await update.message.reply_text(message)
    db.close()

async def month_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /oy command"""
    db = SessionLocal()
    user_id = update.effective_user.id
    
    # Get this month's transactions
    now = datetime.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    days_in_month = (now - month_start).days + 1
    
    month_income = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.type == TransactionType.INCOME,
        Transaction.transaction_date >= month_start
    ).all()
    
    month_expense = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.type == TransactionType.EXPENSE,
        Transaction.transaction_date >= month_start
    ).all()
    
    total_income = sum(t.amount for t in month_income)
    total_expense = sum(t.amount for t in month_expense)
    count = len(month_income) + len(month_expense)
    avg_daily = total_expense / days_in_month if total_expense > 0 else 0
    savings_rate = ((total_income - total_expense) / total_income * 100) if total_income > 0 else 0
    
    message = MONTH_SUMMARY.format(
        income=total_income,
        expense=total_expense,
        net=total_income - total_expense,
        count=count,
        avg=avg_daily,
        savings_rate=savings_rate
    )
    
    await update.message.reply_text(message)
    db.close()

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /yordam command"""
    await update.message.reply_text(HELP_MESSAGE)

async def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ochir command"""
    db = SessionLocal()
    user_id = update.effective_user.id
    
    # Get last transaction
    last_transaction = db.query(Transaction).filter(
        Transaction.user_id == user_id
    ).order_by(Transaction.created_at.desc()).first()
    
    if not last_transaction:
        await update.message.reply_text(NO_TRANSACTIONS)
        db.close()
        return
    
    # Ask for confirmation
    transaction_type = "💰 Daromad" if last_transaction.type == TransactionType.INCOME else "💸 Xarajat"
    message = DELETE_CONFIRM.format(
        type=transaction_type,
        amount=last_transaction.amount,
        description=last_transaction.description or "Tavsif yo'q",
        date=last_transaction.transaction_date.strftime("%d.%m.%Y %H:%M")
    )
    
    keyboard = [
        [InlineKeyboardButton(BTN_YES, callback_data=f"delete_yes_{last_transaction.id}"),
         InlineKeyboardButton(BTN_NO, callback_data="delete_no")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(message, reply_markup=reply_markup)
    db.close()

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    db = SessionLocal()
    
    if query.data.startswith("delete_yes_"):
        transaction_id = int(query.data.split("_")[2])
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        
        if transaction:
            db.delete(transaction)
            db.commit()
            await query.edit_message_text(TRANSACTION_DELETED)
        
    elif query.data == "delete_no":
        await query.edit_message_text(DELETE_CANCELLED)
    
    elif query.data.startswith("undo_"):
        transaction_id = int(query.data.split("_")[1])
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        
        if transaction:
            db.delete(transaction)
            db.commit()
            await query.edit_message_text(TRANSACTION_DELETED)
    
    db.close()

async def handle_button_income(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle 💰 Daromad button click"""
    context.user_data['transaction_type'] = 'income'
    await update.message.reply_text(
        "💰 Daromad qo'shish\n\nSumma va tavsifni kiriting:\nMasalan: 100000 Maosh\n\nYoki faqat summa: 100000",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🚫 Bekor qilish")]], resize_keyboard=True)
    )
    return WAITING_AMOUNT

async def handle_button_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle 💸 Xarajat button click"""
    context.user_data['transaction_type'] = 'expense'
    await update.message.reply_text(
        "💸 Xarajat qo'shish\n\nSumma va tavsifni kiriting:\nMasalan: 5000 nonga\n\nYoki faqat summa: 5000",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🚫 Bekor qilish")]], resize_keyboard=True)
    )
    return WAITING_AMOUNT

async def handle_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle amount and description input (single line)"""
    text = update.message.text.strip()
    
    if text == "🚫 Bekor qilish":
        await update.message.reply_text(
            "❌ Bekor qilindi",
            reply_markup=get_main_keyboard()
        )
        return ConversationHandler.END
    
    # Parse input - try to extract amount and description
    parts = text.split(None, 1)  # Split by whitespace, max 2 parts
    
    try:
        # First part should be the amount
        amount = float(parts[0].replace(",", "").replace(" ", ""))
        if amount <= 0:
            await update.message.reply_text("❌ Summa musbat bo'lishi kerak. Qaytadan kiriting:")
            return WAITING_AMOUNT
        
        # Second part is description (if provided)
        description = parts[1] if len(parts) > 1 else "Boshqa"
        
        # Save transaction immediately
        db = SessionLocal()
        user_id = update.effective_user.id
        transaction_type = context.user_data['transaction_type']
        
        # Get default category
        category = db.query(Category).filter(
            Category.is_default == True,
            Category.type == (TransactionType.INCOME if transaction_type == 'income' else TransactionType.EXPENSE),
            Category.name == "Boshqa"
        ).first()
        
        # Create transaction
        transaction = Transaction(
            user_id=user_id,
            type=TransactionType.INCOME if transaction_type == 'income' else TransactionType.EXPENSE,
            amount=amount,
            category_id=category.id if category else None,
            description=description,
            transaction_date=datetime.now()
        )
        
        db.add(transaction)
        db.commit()
        
        # Get updated balance
        balance = get_user_balance(db, user_id)
        
        # Send confirmation
        if transaction_type == 'income':
            message = INCOME_ADDED.format(
                amount=amount,
                category=category.name if category else "Boshqa",
                description=description,
                date=datetime.now().strftime("%d.%m.%Y %H:%M"),
                balance=balance
            )
        else:
            message = EXPENSE_ADDED.format(
                amount=amount,
                category=category.name if category else "Boshqa",
                description=description,
                date=datetime.now().strftime("%d.%m.%Y %H:%M"),
                balance=balance
            )
        
        await update.message.reply_text(message, reply_markup=get_main_keyboard())
        db.close()
        
        return ConversationHandler.END
        
    except (ValueError, IndexError):
        await update.message.reply_text("❌ Noto'g'ri format!\n\nTo'g'ri format:\n• 5000 nonga\n• 100000 Maosh\n\nQaytadan kiriting:")
        return WAITING_AMOUNT

async def handle_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """This function is no longer used but kept for compatibility"""
    return ConversationHandler.END

async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the conversation"""
    await update.message.reply_text(
        "❌ Bekor qilindi",
        reply_markup=get_main_keyboard()
    )
    return ConversationHandler.END

async def handle_button_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle 💵 Balans button click"""
    await balance_command(update, context)

async def handle_button_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle 📅 Bugun button click"""
    await today_command(update, context)

async def handle_button_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle 📊 Dashboard button click"""
    keyboard = [[InlineKeyboardButton("📊 Dashboard ochish", web_app=WebAppInfo(url=WEBAPP_URL))]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "📱 Web Dashboard\n\nQuyidagi tugmani bosing:",
        reply_markup=reply_markup
    )

def get_main_keyboard():
    """Get main keyboard with buttons"""
    keyboard = [
        [KeyboardButton("💰 Daromad"), KeyboardButton("💸 Xarajat")],
        [KeyboardButton("💵 Balans"), KeyboardButton("📅 Bugun")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Initialize bot application
def create_bot():
    """Create and configure bot application"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Conversation handler for adding transactions
    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^💰 Daromad$"), handle_button_income),
            MessageHandler(filters.Regex("^💸 Xarajat$"), handle_button_expense),
        ],
        states={
            WAITING_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_amount)],
            WAITING_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_description)],
        },
        fallbacks=[
            MessageHandler(filters.Regex("^🚫 Bekor qilish$"), cancel_conversation),
            CommandHandler("start", start_command)
        ],
    )
    
    # Add conversation handler
    application.add_handler(conv_handler)
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("kirim", income_command))
    application.add_handler(CommandHandler("chiqim", expense_command))
    application.add_handler(CommandHandler("balans", balance_command))
    application.add_handler(CommandHandler("bugun", today_command))
    application.add_handler(CommandHandler("hafta", week_command))
    application.add_handler(CommandHandler("oy", month_command))
    application.add_handler(CommandHandler("yordam", help_command))
    application.add_handler(CommandHandler("ochir", delete_command))
    
    # Add button handlers
    application.add_handler(MessageHandler(filters.Regex("^💵 Balans$"), handle_button_balance))
    application.add_handler(MessageHandler(filters.Regex("^📅 Bugun$"), handle_button_today))
    application.add_handler(MessageHandler(filters.Regex("^📊 Dashboard$"), handle_button_dashboard))
    
    # Add callback query handler
    application.add_handler(CallbackQueryHandler(button_callback))
    
    return application

if __name__ == "__main__":
    print("🤖 Bot ishga tushmoqda...")
    app = create_bot()
    app.run_polling()
