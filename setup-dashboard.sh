#!/bin/bash
# Quick Dashboard Setup Script for EC2

echo "🚀 Setting up Finance Bot Dashboard..."

# Get EC2 public IP
PUBLIC_IP=$(curl -s http://checkip.amazonaws.com)
echo "📍 Your EC2 Public IP: $PUBLIC_IP"

# Check if we're in the right directory
if [ ! -f "backend/main.py" ]; then
    echo "❌ Error: Please run this script from telegram-finance-bot directory"
    exit 1
fi

# 1. Install Nginx
echo ""
echo "📦 Installing Nginx..."
sudo yum install nginx -y

# 2. Install Node.js if not present
if ! command -v node &> /dev/null; then
    echo "📦 Installing Node.js..."
    curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
    sudo yum install nodejs -y
fi

# 3. Install PM2 globally
echo "📦 Installing PM2..."
sudo npm install -g pm2

# 4. Build frontend
echo ""
echo "🏗️  Building frontend..."
cd frontend

# Create .env.production
cat > .env.production << EOF
VITE_API_URL=http://$PUBLIC_IP/api
EOF

# Install dependencies and build
npm install
npm run build

if [ ! -d "dist" ]; then
    echo "❌ Frontend build failed!"
    exit 1
fi

echo "✅ Frontend built successfully!"

# 5. Configure Nginx
echo ""
echo "⚙️  Configuring Nginx..."
sudo tee /etc/nginx/conf.d/finance-bot.conf > /dev/null << EOF
server {
    listen 80;
    server_name _;

    # Frontend
    location / {
        root /home/ec2-user/telegram-finance-bot/frontend/dist;
        try_files \$uri \$uri/ /index.html;
        add_header Cache-Control "no-cache";
    }

    # API
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOF

# Test and start Nginx
sudo nginx -t
sudo systemctl start nginx
sudo systemctl enable nginx

echo "✅ Nginx configured!"

# 6. Update .env with FRONTEND_URL
echo ""
echo "⚙️  Updating .env..."
cd ~/telegram-finance-bot

if ! grep -q "FRONTEND_URL" .env; then
    echo "FRONTEND_URL=http://$PUBLIC_IP" >> .env
fi

# 7. Start services with PM2
echo ""
echo "🚀 Starting services..."
cd backend
source venv/bin/activate

# Stop existing processes if any
pm2 delete finance-api 2>/dev/null || true
pm2 delete finance-bot 2>/dev/null || true

# Start API and Bot
pm2 start main.py --name finance-api --interpreter python3
pm2 start bot.py --name finance-bot --interpreter python3

pm2 save
pm2 startup | tail -n 1 | bash

echo ""
echo "✅ Setup complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Dashboard is ready!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Dashboard URL: http://$PUBLIC_IP"
echo "🤖 Telegram Bot: Working"
echo "🔌 API Server: http://$PUBLIC_IP/api"
echo ""
echo "Next steps:"
echo "1. Open Security Group in AWS Console"
echo "2. Add Inbound rule: HTTP (port 80) from 0.0.0.0/0"
echo "3. Visit: http://$PUBLIC_IP"
echo "4. Use Dashboard button in Telegram bot"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Useful commands:"
echo "  pm2 status        - Check status"
echo "  pm2 logs          - View logs"
echo "  pm2 restart all   - Restart all services"
echo ""
