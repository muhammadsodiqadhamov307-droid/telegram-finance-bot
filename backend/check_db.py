import argparse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
import sys

# Default path, but allow override
DEFAULT_DB_PATH = "/home/ec2-user/telegram-finance-bot/backend/finance.db"

def inspect_db(path):
    print(f"\n🕵️ INSPECTING DATABASE: {path}")
    
    if not os.path.exists(path):
        print(f"❌ ERROR: File not found at {path}")
        return

    try:
        # Create engine
        db_url = f"sqlite:///{path}"
        engine = create_engine(db_url)
        with engine.connect() as conn:
            # 1. Check Users
            print("\n--- 👤 USERS ---")
            # User table uses telegram_id as PK, there is no 'id' column
            result = conn.execute(text("SELECT telegram_id, first_name, username FROM users"))
            users = result.fetchall()
            if not users:
                print("⚠️  No users found! Did you run /start in the bot?")
            else:
                for u in users:
                    print(f"Telegram ID: {u.telegram_id} | Name: {u.first_name} (@{u.username})")

            # 2. Check Transactions (Last 5)
            print("\n--- 💰 RECENT TRANSACTIONS ---")
            result = conn.execute(text("SELECT id, user_id, amount, type, description, transaction_date FROM transactions ORDER BY transaction_date DESC LIMIT 5"))
            transactions = result.fetchall()
            if not transactions:
                print("⚠️  No transactions found! Add income/expense in the bot.")
            else:
                for t in transactions:
                    print(f"ID: {t.id} | User: {t.user_id} | {t.type.upper()}: {t.amount} | Desc: {t.description}")
            
            # 3. Check Categories count
            result = conn.execute(text("SELECT count(*) FROM categories"))
            cat_count = result.scalar()
            print(f"\n--- 📂 TOTAL CATEGORIES: {cat_count} ---")

    except Exception as e:
        print(f"❌ Error reading database: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inspect Finance Bot Database")
    parser.add_argument("--path", default=DEFAULT_DB_PATH, help="Path to sqlite database file")
    args = parser.parse_args()
    
    inspect_db(args.path)
