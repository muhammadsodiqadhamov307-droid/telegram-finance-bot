# Web Dashboard Setup Guide - EC2

## 🎯 Maqsad
Telegram bot uchun web dashboard o'rnatish (charts, analytics, transaction management)

---

## 1️⃣ API Server (FastAPI) ishga tushirish

```bash
# Backend directory'ga o'ting
cd ~/telegram-finance-bot/backend

# Virtual environment aktivlashtirish
source venv/bin/activate

# API server test qilish
python main.py
```

**Yangi terminal oching va test qiling:**
```bash
curl http://localhost:8000/
# Ko'rishingiz kerak: {"message":"Finance Bot API","status":"running"}
```

Ishlasa `Ctrl+C` bilan to'xtating, keyin PM2 bilan ishga tushiramiz.

---

## 2️⃣ Node.js va NPM o'rnatish (agar yo'q bo'lsa)

```bash
# Node.js versiyasini tekshirish
node --version
npm --version

# Agar o'rnatilmagan bo'lsa:
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install nodejs -y
```

---

## 3️⃣ Frontend build qilish

```bash
cd ~/telegram-finance-bot/frontend

# Dependencies o'rnatish (birinchi marta)
npm install

# API URL ni sozlash
# Agar sizning EC2 public IP: 1.2.3.4 bo'lsa
export VITE_API_URL=http://YOUR_EC2_PUBLIC_IP:8000

# Build qilish
npm run build

# Build muvaffaqiyatli bo'lsa, dist/ papka yaratiladi
ls -la dist/
```

---

## 4️⃣ Nginx o'rnatish va sozlash

```bash
# Nginx o'rnatish
sudo yum install nginx -y

# Nginx config yaratish
sudo nano /etc/nginx/conf.d/finance-bot.conf
```

**Config faylga quyidagini kiriting:**

```nginx
server {
    listen 80;
    server_name _;  # Yoki sizning domain: your-domain.com

    # Frontend (React app)
    location / {
        root /home/ec2-user/telegram-finance-bot/frontend/dist;
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "no-cache";
    }

    # API (FastAPI)
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_cache_bypass $http_upgrade;
    }
}
```

**Saqlash:** `Ctrl+X`, `Y`, `Enter`

```bash
# Nginx test qilish
sudo nginx -t

# Nginx ishga tushirish
sudo systemctl start nginx
sudo systemctl enable nginx
```

---

## 5️⃣ AWS Security Group sozlash

**AWS Console'da:**

1. EC2 → Instances → Select your instance
2. Security → Security Groups
3. **Inbound rules** → Edit inbound rules
4. Add rule:
   - Type: HTTP
   - Port: 80
   - Source: 0.0.0.0/0
5. Save rules

---

## 6️⃣ PM2 bilan API va Bot ishga tushirish

```bash
# PM2 o'rnatish (agar yo'q bo'lsa)
sudo npm install -g pm2

cd ~/telegram-finance-bot/backend

# API server ishga tushirish
pm2 start main.py --name finance-api --interpreter python3

# Bot ishga tushirish
pm2 start bot.py --name finance-bot --interpreter python3

# Status tekshirish
pm2 status

# Logs ko'rish
pm2 logs finance-api
pm2 logs finance-bot

# Auto-restart sozlash
pm2 save
pm2 startup
```

---

## 7️⃣ .env faylni yangilash

```bash
cd ~/telegram-finance-bot
nano .env
```

**FRONTEND_URL ni qo'shing:**
```env
TELEGRAM_BOT_TOKEN=your_bot_token
DATABASE_URL=postgresql://botuser:password@localhost:5432/finance_bot
JWT_SECRET=your-secret-key
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_URL=http://YOUR_EC2_PUBLIC_IP
```

**YOUR_EC2_PUBLIC_IP ni o'z IP'ingiz bilan almashtiring:**
```bash
# EC2 public IP ni olish
curl http://checkip.amazonaws.com
```

Saqlang va PM2 ni restart qiling:
```bash
pm2 restart all
```

---

## 8️⃣ Frontend API URL ni to'g'rilash

```bash
cd ~/telegram-finance-bot/frontend

# .env.production yaratish
nano .env.production
```

**Quyidagini kiriting:**
```env
VITE_API_URL=http://YOUR_EC2_PUBLIC_IP/api
```

**Qayta build qiling:**
```bash
npm run build

# Nginx restart
sudo systemctl reload nginx
```

---

## 9️⃣ Dashboard buttoni qayta yoqish

Bot'dagi Dashboard button'ini yoqish uchun GitHub'dan oxirgi versiyani tortib oling.

Yoki manual qo'shish:

```bash
nano ~/telegram-finance-bot/backend/bot.py
```

`get_main_keyboard()` funksiyasini quyidagicha o'zgartiring:

```python
def get_main_keyboard():
    """Get main keyboard with buttons"""
    keyboard = [
        [KeyboardButton("💰 Daromad"), KeyboardButton("💸 Xarajat")],
        [KeyboardButton("💵 Balans"), KeyboardButton("📅 Bugun")],
        [KeyboardButton("📊 Dashboard")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
```

Saqlang va bot'ni restart qiling:
```bash
pm2 restart finance-bot
```

---

## ✅ Test qilish

### 1. API Test:
```bash
curl http://YOUR_EC2_PUBLIC_IP/api/
# Javob: {"message":"Finance Bot API","status":"running"}
```

### 2. Frontend Test:
Browser'da: `http://YOUR_EC2_PUBLIC_IP`

Ko'rishingiz kerak: Dashboard login page yoki main page

### 3. Telegram'da Test:
1. Bot'ga o'ting
2. 📊 **Dashboard** tugmasini bosing
3. Dashboard ochilishi kerak

---

## 🔧 Muammolarni hal qilish

### Frontend ochilmayapti
```bash
# Nginx logs
sudo tail -f /var/log/nginx/error.log

# Nginx restart
sudo systemctl restart nginx
```

### API ishlamayapti
```bash
# PM2 logs
pm2 logs finance-api

# Port band bo'lganmi?
sudo netstat -tulpn | grep 8000

# Restart
pm2 restart finance-api
```

### Telegram WebApp HTTPS xatosi
Telegram WebApp requires HTTPS. You'll need to set up SSL:

```bash
# Install Certbot
sudo yum install certbot python3-certbot-nginx -y

# Get domain (you need a domain name pointing to your EC2)
sudo certbot --nginx -d your-domain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

---

## 📊 Status tekshirish

```bash
# Barcha servicela
pm2 status

# Nginx
sudo systemctl status nginx

# PostgreSQL
sudo systemctl status postgresql

# Barcha portlar
sudo netstat -tulpn | grep LISTEN
```

---

## 🎉 Tayyor!

Dashboard manzili: `http://YOUR_EC2_PUBLIC_IP`

**Telegram'dan kirish:**
Bot → 📊 Dashboard tugmasi → Dashboard ochiladi

**Muhim:** Production uchun SSL (HTTPS) sozlang!
