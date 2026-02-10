# Cloud Server Deployment Guide - Telegram Finance Bot

## 🚀 Server'da Deploy Qilish

### 1. Repository'ga o'ting
```bash
cd telegram-finance-bot
ls -la  # Barcha fayllarni ko'rish
```

### 2. Python va Node.js o'rnatilganligini tekshiring
```bash
python3 --version  # Python 3.10+ kerak
node --version     # Node.js 18+ kerak
npm --version
```

**Agar o'rnatilmagan bo'lsa:**
```bash
# Python 3.10+
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip -y

# Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y
```

### 3. PostgreSQL o'rnatish
```bash
# PostgreSQL o'rnatish
sudo apt install postgresql postgresql-contrib -y

# PostgreSQL ishga tushirish
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Database yaratish
sudo -u postgres psql -c "CREATE DATABASE finance_bot;"
sudo -u postgres psql -c "CREATE USER botuser WITH PASSWORD 'strong_password_here';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE finance_bot TO botuser;"
```

### 4. Environment Variables sozlash
```bash
# .env fayl yaratish
cp .env.example .env

# Nano yoki vim bilan tahrirlash
nano .env
```

**.env faylini to'ldiring:**
```env
TELEGRAM_BOT_TOKEN=your_actual_bot_token_from_botfather
DATABASE_URL=postgresql://botuser:strong_password_here@localhost:5432/finance_bot
JWT_SECRET=your-very-long-random-secret-key-here
API_HOST=0.0.0.0
API_PORT=8000
WEBHOOK_URL=https://your-domain.com/webhook
```

**Saqlash:** `Ctrl+X`, `Y`, `Enter`

### 5. Backend sozlash
```bash
cd backend

# Virtual environment yaratish
python3 -m venv venv

# Aktivatsiya
source venv/bin/activate

# Dependencies o'rnatish
pip install -r requirements.txt

# Database initialize
python database.py
```

**Ko'rishingiz kerak:**
```
✅ Database tables created successfully!
✅ Default categories created successfully!
```

### 6. Backend test qilish
```bash
# API test
python main.py
```

Yangi terminal oching va test qiling:
```bash
curl http://localhost:8000/
# Ko'rishingiz kerak: {"message":"Finance Bot API","status":"running"}
```

`Ctrl+C` bilan to'xtating.

### 7. Bot test qilish
```bash
# Backend terminal'da
python bot.py
```

Telegram'da botingizga `/start` yuboring. Javob bersa ✅

`Ctrl+C` bilan to'xtating.

### 8. Production uchun PM2 bilan ishga tushirish

**PM2 o'rnatish:**
```bash
sudo npm install -g pm2
```

**Bot va API ni ishga tushirish:**
```bash
cd ~/telegram-finance-bot/backend

# API server
pm2 start main.py --name finance-api --interpreter python3

# Telegram bot
pm2 start bot.py --name finance-bot --interpreter python3

# Status ko'rish
pm2 status

# Logs ko'rish
pm2 logs finance-bot
pm2 logs finance-api
```

**Auto-restart sozlash:**
```bash
pm2 save
pm2 startup
# Ko'rsatilgan buyruqni copy-paste qiling (sudo bilan)
```

### 9. Frontend sozlash (ixtiyoriy - Web Dashboard uchun)

```bash
cd ~/telegram-finance-bot/frontend

# Dependencies o'rnatish
npm install

# Build qilish
npm run build

# Static files dist/ papkasida bo'ladi
```

**Nginx bilan serve qilish:**
```bash
sudo apt install nginx -y

# Nginx config
sudo nano /etc/nginx/sites-available/finance-bot
```

**Config:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        root /root/telegram-finance-bot/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_exchange;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

**Aktivlashtirish:**
```bash
sudo ln -s /etc/nginx/sites-available/finance-bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 10. SSL (HTTPS) sozlash - MUHIM!

Telegram WebApp HTTPS talab qiladi:

```bash
# Certbot o'rnatish
sudo apt install certbot python3-certbot-nginx -y

# SSL sertifikat olish
sudo certbot --nginx -d your-domain.com

# Auto-renewal test
sudo certbot renew --dry-run
```

### 11. Firewall sozlash
```bash
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw enable
sudo ufw status
```

---

## ✅ Tekshirish

### Bot ishlayaptimi?
```bash
pm2 status
# Ikkalasi ham "online" bo'lishi kerak
```

### Logs ko'rish
```bash
pm2 logs finance-bot --lines 50
pm2 logs finance-api --lines 50
```

### Bot'ni Telegram'da test qilish
1. Telegram'da botingizga o'ting
2. `/start` yuboring
3. `/kirim 100000 Test` - daromad qo'shing
4. `/balans` - balansni ko'ring

### Web Dashboard test qilish
1. Bot'da `/dashboard` yuboring (Telegram WebApp button orqali)
2. Yoki browser'da: `https://your-domain.com`

---

## 🔧 Muammolarni hal qilish

### Bot javob bermayapti
```bash
# Logs tekshiring
pm2 logs finance-bot --lines 100

# Bot token to'g'rimi?
cat .env | grep TELEGRAM_BOT_TOKEN

# Restart
pm2 restart finance-bot
```

### Database xatosi
```bash
# PostgreSQL ishlamoqdami?
sudo systemctl status postgresql

# Database connection test
sudo -u postgres psql finance_bot -c "SELECT COUNT(*) FROM users;"
```

### API ishlamayapti
```bash
pm2 logs finance-api
pm2 restart finance-api

# Portni tekshirish
sudo netstat -tulpn | grep 8000
```

---

## 📊 Monitoring

### PM2 Monitoring
```bash
pm2 monit  # Real-time monitoring
```

### System resources
```bash
htop  # CPU, RAM
df -h  # Disk space
```

---

## 🔄 Update qilish

GitHub'dan yangi versiyani olish:

```bash
cd ~/telegram-finance-bot

# Pull latest changes
git pull origin main

# Backend update
cd backend
source venv/bin/activate
pip install -r requirements.txt
pm2 restart finance-bot
pm2 restart finance-api

# Frontend update (if needed)
cd ../frontend
npm install
npm run build
sudo systemctl reload nginx
```

---

## 🎉 Tayyor!

Botingiz ishlamoqda:
- ✅ Telegram bot online
- ✅ API server running
- ✅ Database working
- ✅ Web dashboard available (agar SSL sozlagan bo'lsangiz)

**Foydali buyruqlar:**
```bash
pm2 status          # Statusni ko'rish
pm2 logs            # Loglarni ko'rish
pm2 restart all     # Barchasini restart
pm2 stop all        # Barchasini to'xtatish
```

---

## 📞 Yordam kerakmi?

- Logs: `pm2 logs`
- Status: `pm2 status`
- Restart: `pm2 restart finance-bot finance-api`

Muvaffaqiyatlar! 🚀
