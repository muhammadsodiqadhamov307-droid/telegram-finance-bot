"""
Uzbek language messages for the Telegram bot
"""

# Welcome and help messages
WELCOME_MESSAGE = """🎉 Xush kelibsiz!

Men sizning moliyaviy operatsiyalaringizni kuzatishga yordam beradigan botman.

📊 Quyidagi buyruqlardan foydalanishingiz mumkin:

💰 /kirim <summa> <tavsif> - Daromad qo'shish
💸 /chiqim <summa> <tavsif> - Xarajat qo'shish
💵 /balans - Joriy balans va qisqacha ma'lumot
📅 /bugun - Bugungi tranzaksiyalar
📆 /hafta - Haftalik xulosa
📊 /oy - Oylik xulosa
🗑️ /ochir - Oxirgi tranzaksiyani o'chirish
📱 /dashboard - Web dasturni ochish
📂 /kategoriya - Kategoriyalarni boshqarish
❓ /yordam - Barcha buyruqlar ro'yxati

Boshlash uchun daromad yoki xarajat qo'shing! 🚀
"""

HELP_MESSAGE = """📖 Yordam

🔹 Daromad qo'shish:
/kirim 500000 Maosh
/kirim 200000 Freelance loyiha

🔹 Xarajat qo'shish:
/chiqim 50000 Oziq-ovqat
/chiqim 20000 Transport

🔹 Ma'lumotlarni ko'rish:
/balans - Joriy balansni ko'rish
/bugun - Bugungi tranzaksiyalar
/hafta - Haftalik statistika
/oy - Oylik hisobot

🔹 Boshqarish:
/ochir - Oxirgi tranzaksiyani bekor qilish
/kategoriya - Kategoriyalarni sozlash
/dashboard - To'liq dashboard

Savollaringiz bo'lsa, menga yozing! 😊
"""

# Transaction messages
INCOME_ADDED = """✅ Daromad qo'shildi!

💰 Summa: {amount:,.0f} UZS
📂 Kategoriya: {category}
📝 Tavsif: {description}
📅 Sana: {date}

💵 Joriy balans: {balance:,.0f} UZS
"""

EXPENSE_ADDED = """✅ Xarajat qo'shildi!

💸 Summa: {amount:,.0f} UZS
📂 Kategoriya: {category}
📝 Tavsif: {description}
📅 Sana: {date}

💵 Joriy balans: {balance:,.0f} UZS
"""

BALANCE_MESSAGE = """💰 Sizning balansingiz

💵 Joriy balans: {balance:,.0f} UZS

📊 Bu oyda:
💰 Daromad: {income:,.0f} UZS
💸 Xarajat: {expense:,.0f} UZS
📈 Farq: {diff:,.0f} UZS

📅 Oxirgi yangilash: {date}
"""

TODAY_SUMMARY = """📅 Bugungi tranzaksiyalar

💰 Daromad: {income:,.0f} UZS
💸 Xarajat: {expense:,.0f} UZS
📊 Sof: {net:,.0f} UZS

📋 Tranzaksiyalar soni: {count}
"""

WEEK_SUMMARY = """📆 Haftalik xuлоsa

💰 Daromad: {income:,.0f} UZS
💸 Xarajat: {expense:,.0f} UZS
📊 Sof: {net:,.0f} UZS

📋 Tranzaksiyalar: {count} ta
📈 Kunlik o'rtacha xarajat: {avg:,.0f} UZS
"""

MONTH_SUMMARY = """📊 Oylik hisobot

💰 Daromad: {income:,.0f} UZS
💸 Xarajat: {expense:,.0f} UZS
📊 Sof: {net:,.0f} UZS

📋 Jami tranzaksiyalar: {count} ta
📈 Kunlik o'rtacha: {avg:,.0f} UZS
💾 Tejash darajasi: {savings_rate:.1f}%
"""

DELETE_CONFIRM = """⚠️ Oxirgi tranzaksiyani o'chirmoqchimisiz?

{type} - {amount:,.0f} UZS
📝 {description}
📅 {date}
"""

TRANSACTION_DELETED = "✅ Tranzaksiya o'chirildi!"
DELETE_CANCELLED = "❌ Bekor qilindi"
NO_TRANSACTIONS = "📭 Hozircha tranzaksiyalar yo'q"

# Error messages
INVALID_AMOUNT = "❌ Xato summa! Iltimos, to'g'ri son kiriting.\n\nMisol: /kirim 100000 Maosh"
INVALID_COMMAND = "❌ Buyruq noto'g'ri. /yordam buyrug'idan foydalaning."
ERROR_OCCURRED = "❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring."

# Button labels
BTN_YES = "✅ Ha"
BTN_NO = "❌ Yo'q"
BTN_INCOME = "💰 Daromad"
BTN_EXPENSE = "💸 Xarajat"
BTN_BALANCE = "💵 Balans"
BTN_TODAY = "📅 Bugun"
BTN_DASHBOARD = "📊 Dashboard"
BTN_CANCEL = "🚫 Bekor qilish"

# Category management
CATEGORY_LIST = """📂 Kategoriyalar

💸 Xarajatlar:
{expense_categories}

💰 Daromadlar:
{income_categories}

Yangi kategoriya qo'shish uchun:
/kategoriya_qoshish <tur> <nom> <icon>
"""

CATEGORY_ADDED = "✅ Kategoriya qo'shildi: {name} {icon}"
CATEGORY_DELETED = "✅ Kategoriya o'chirildi"
CATEGORY_NOT_FOUND = "❌ Kategoriya topilmadi"

# Web App
WEBAPP_LAUNCH = """📱 Web Dashboardni ochish

Quyidagi tugmani bosing va to'liq dashboard ochiladi! 👇
"""

# Notifications
DAILY_SUMMARY_NOTIFICATION = """🌙 Kunlik xulosa

Bugun siz:
💰 {income:,.0f} UZS daromad qildingiz
💸 {expense:,.0f} UZS xarajat qildingiz

💵 Joriy balans: {balance:,.0f} UZS

Ertaga ko'rishguncha! 😊
"""
