# Moliya Tracker - Telegram Finance Bot

**Telegram bot va Web Dashboard orqali moliyaviy operatsiyalarni kuzatish tizimi**

## 📋 Tavsif

Bu loyiha Telegram bot va chiroyli web dashboard yordamida daromad va xarajatlarni kuzatishga yordam beradi. Foydalanuvchilar Telegram orqali tezkor operatsiya qo'shishlari va web dasturda batafsil statistika va grafiklar ko'rishlari mumkin.

## ✨ Asosiy imkoniyatlar

### 🤖 Telegram Bot
- `/start` - Botni boshlash va ro'yxatdan o'tish
- `/kirim <summa> <tavsif>` - Daromad qo'shish
- `/chiqim <summa> <tavsif>` - Xarajat qo'shish
- `/balans` - Joriy balans va umumiy ma'lumot
- `/bugun` - Bugungi tranzaksiyalar
- `/hafta` - Haftalik hisobot
- `/oy` - Oylik hisobot
- `/ochir` - Oxirgi tranzaksiyani o'chirish
- `/yordam` - Yordam va buyruqlar ro'yxati

### 📱 Web Dashboard
- Balans va statistika kartalari
- Interaktiv grafiklar (balans tendentsiyasi, kategoriyalar bo'yicha)
- Tranzaksiyalarni qidirish va filtrlash
- Tezkor daromad/xarajat qo'shish
- Qorong'u/yorug' mavzu
- To'liq responsiv dizayn

## 🛠️ Texnologiyalar

### Backend
- **Python 3.10+**
- **python-telegram-bot** - Telegram bot
- **FastAPI** - REST API
- **SQLAlchemy** - ORM
- **PostgreSQL** - Ma'lumotlar bazasi

### Frontend
- **React 18** + **TypeScript**
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Chart.js** - Grafiklar
- **Framer Motion** - Animatsiyalar
- **React Query** - Data fetching

## 📦 O'rnatish

### Talablar
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Telegram Bot Token ([BotFather](https://t.me/botfather) orqali)

### 1. Repository ni klonlash
```bash
git clone <repository-url>
cd telegram_bot
```

### 2. Backend sozlash

```bash
cd backend

# Virtual environment yaratish
python -m venv venv

# Aktivatsiya qilish (Windows)
venv\Scripts\activate

# Aktivatsiya qilish (Linux/Mac)
source venv/bin/activate

# Dependencies o'rnatish
pip install -r requirements.txt
```

### 3. Ma'lumotlar bazasi sozlash

PostgreSQL serveringizda yangi database yarating:
```sql
CREATE DATABASE finance_bot;
```

### 4. Environment variables

`.env` fayl yarating (`.env.example` asosida):
```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here
DATABASE_URL=postgresql://user:password@localhost:5432/finance_bot
JWT_SECRET=your_secret_key_here
API_HOST=0.0.0.0
API_PORT=8000
WEBHOOK_URL=https://your-domain.com/webhook
```

### 5. Database ni initialize qilish

```bash
python database.py
```

### 6. Frontend sozlash

```bash
cd frontend

# Dependencies o'rnatish
npm install

# .env fayl yaratish
echo "VITE_API_URL=http://localhost:8000" > .env
```

## 🚀 Ishga tushirish

### Development

**Backend (Terminal 1):**
```bash
cd backend
python bot.py
```

**API Server (Terminal 2):**
```bash
cd backend
python main.py
```

**Frontend (Terminal 3):**
```bash
cd frontend
npm run dev
```

Frontend `http://localhost:3000` da ochiladi.

### Production

#### Backend deployment (Railway/Render)

1. Repository ni GitHub ga push qiling
2. Railway/Render'da yangi project yarating
3. Environment variables ni to'ldiring
4. PostgreSQL database qo'shing
5. Deploy qiling

#### Frontend deployment

```bash
cd frontend
npm run build
```

`dist` papkasini static hosting servicega (Vercel, Netlify, Cloudflare Pages) yuklang.

## 📱 Telegram Web App sozlash

1. [BotFather](https://t.me/botfather) ga o'ting
2. `/setmenubutton` buyrug'ini yuboring
3. Botingizni tanlang
4. "Dashboard" nomini kiriting
5. Frontend URL ni kiriting

## 🎨 Screenshot'lar

### Bot Interface
![Bot Commands](docs/bot-screenshot.png)

### Web Dashboard
![Dashboard](docs/dashboard-screenshot.png)

## 📖 API Dokumentatsiya

API Swagger dokumentatsiyasi: `http://localhost:8000/docs`

### Asosiy endpoint'lar

#### Tranzaksiyalar
- `GET /api/transactions` - Barcha tranzaksiyalar
- `POST /api/transactions` - Yangi tranzaksiya
- `DELETE /api/transactions/{id}` - Tranzaksiyani o'chirish

#### Statistika
- `GET /api/analytics/summary` - Umumiy xuлоsa
- `GET /api/analytics/by-category` - Kategoriyalar bo'yicha

#### Kategoriyalar
- `GET /api/categories` - Barcha kategoriyalar

## 🔒 Xavfsizlik

- Telegram WebApp initData authentication
- SQL injection himoyasi (Prepared statements)
- HTTPS only
- Input validation
- Rate limiting

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm run test
```

## 📝 Litsenziya

MIT License

## 🤝 Hissa qo'shish

Pull request'lar xush kelibsiz! Katta o'zgarishlar uchun avval issue oching.

## 📧 Aloqa

Savollar bo'lsa, issue yoki pull request oching.

## 🙏 Minnatdorchilik

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Chart.js](https://www.chartjs.org/)

---

**Dasturchi bilan:** ❤️ Python va React

**Til:** 🇺🇿 O'zbek tili
