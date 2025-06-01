# 🤖 WhatsApp AI Bot with Hidden User Roles

> **WhatsApp AI Bot yang canggih dengan sistem user role tersembunyi, menggunakan OpenRouter AI dan Green API**

## ✨ Fitur Utama

### 🎭 **Hidden User Role System**
- **Admin**: Akses penuh dengan badge `🔰 ADMIN`
- **VIP**: Layanan premium tanpa badge (tersembunyi)
- **Premium**: Enhanced AI tanpa badge (tersembunyi) 
- **Basic**: User biasa dengan AI standard

### 🧠 **AI Integration**
- **OpenRouter AI** dengan model Llama 3.3 8B
- **Context-aware** conversations
- **Role-based** AI responses
- **Fallback system** jika AI tidak tersedia

### 🔐 **Security Features**
- **Rate limiting** per user
- **Banned user** management
- **Admin-only commands**
- **Privacy-focused** (VIP/Premium tidak tahu status mereka)

### 📊 **Management System**
- **User statistics** tracking
- **Admin commands** untuk monitoring
- **No database** required (hardcoded config)
- **Real-time** webhook processing

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Green API Account
- OpenRouter API Key
- Railway Account (untuk hosting)

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/whatsapp-ai-bot.git
cd whatsapp-ai-bot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Setup
Buat file `.env`:
```env
# Green API Configuration
GREEN_API_URL=https://api.green-api.com
GREEN_API_TOKEN=your_green_api_token
GREEN_API_INSTANCE=your_instance_id

# OpenRouter AI
OPENROUTER_API_KEY=your_openrouter_api_key

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
```

### 4. Configure Users
Edit `app.py` bagian `SPECIAL_USERS`:
```python
SPECIAL_USERS = {
    "6285277801324@c.us": "admin",      # Ganti dengan nomor admin
    "6282225651172@c.us": "vip",        # Ganti dengan nomor VIP
    "628xxxxxxxxx@c.us": "premium",     # Ganti dengan nomor Premium
}
```

### 5. Run Locally
```bash
python app.py
```

Bot akan berjalan di `http://localhost:5000`

## 🌐 Deploy ke Railway

### 1. Persiapan Files
Pastikan ada file berikut:
- `requirements.txt`
- `Procfile`
- `app.py`, `bot.py`, `config.py`

### 2. Deploy Steps
1. **Push ke GitHub**
2. **Connect Railway** dengan GitHub repo
3. **Set Environment Variables** di Railway dashboard
4. **Deploy otomatis** akan berjalan

### 3. Setup Webhook
Setelah deploy, set webhook di Green API:
```
https://your-app.railway.app/webhook
```

## 📱 Penggunaan

### User Commands
```
Halo/Hi           → Greeting message
Test/Ping         → Bot status check
[Pertanyaan]      → AI response
```

### Admin Commands  
```
/check <nomor>    → Check user info & role
/users            → List all special users
/stats            → Bot statistics
/help             → Admin help
/status           → System status
```

## 🏗️ Struktur Project

```
whatsapp-ai-bot/
├── app.py              # Main Flask application
├── bot.py              # Bot logic & AI integration
├── config.py           # Configuration management
├── requirements.txt    # Python dependencies
├── Procfile           # Railway deployment config
├── .env.example       # Environment variables template
└── README.md          # This file
```

## ⚙️ Konfigurasi

### User Roles Configuration
```python
USER_ROLES = {
    "admin": {
        "name": "Administrator",
        "ai_model": "meta-llama/llama-3.3-8b-instruct:free",
        "max_tokens": 800,
        "temperature": 0.7,
        "show_badge": True
    },
    "vip": {
        "name": "VIP Princess", 
        "ai_model": "meta-llama/llama-3.3-8b-instruct:free",
        "max_tokens": 600,
        "show_badge": False  # Hidden role
    }
    # ... more roles
}
```

### AI Models Available
- `meta-llama/llama-3.3-8b-instruct:free`
- `meta-llama/llama-3.1-8b-instruct:free`
- Dapat diganti sesuai model OpenRouter lainnya

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Home page & bot info |
| `/webhook` | POST | WhatsApp webhook handler |
| `/status` | GET | Bot status & health check |
| `/users` | GET | User configuration info |

## 📊 Monitoring & Logs

### Railway Logs
```bash
# Lihat logs real-time di Railway dashboard
# Path: Project → Deployments → [Latest] → Logs
```

### Status Check
```bash
curl https://your-app.railway.app/status
```

### User Statistics
Admin dapat menggunakan `/stats` untuk melihat:
- Total users per role
- System status
- Privacy features info

## 🛡️ Security & Privacy

### Hidden Role System
- **VIP & Premium** users tidak tahu status khusus mereka
- Mendapat layanan lebih baik secara **natural**
- Hanya **admin** yang tahu struktur role lengkap

### Rate Limiting
- **Built-in** rate limiting per user
- **Configurable** limit per role
- **Automatic** cooldown system

### Access Control
- **Hardcoded** user management (no database)
- **Admin-only** system commands
- **Banned user** support

## 🚨 Troubleshooting

### Common Issues

#### Bot Tidak Merespons
```bash
# Check webhook URL
curl -X POST https://your-app.railway.app/webhook

# Check Green API instance status
# Pastikan webhook sudah diset dengan benar
```

#### AI Response Error
```bash
# Check OpenRouter API key
# Verify model availability
# Check rate limits
```

#### Environment Variables
```bash
# Pastikan semua env vars sudah diset di Railway
# Check dengan /status endpoint
```

### Debug Mode
```python
# Set di .env untuk development
FLASK_DEBUG=True
FLASK_ENV=development
```

## 🤝 Contributing

1. **Fork** repository
2. **Create** feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** changes (`git commit -m 'Add AmazingFeature'`)
4. **Push** to branch (`git push origin feature/AmazingFeature`)
5. **Open** Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 👨‍💻 Developer

**Rajulul Anshar** - Indonesia 🇮🇩
- Telegram: [@rajululanshar](https://t.me/rajululanshar)
- GitHub: [@rajululanshar](https://github.com/rajululanshar)

## 🙏 Acknowledgments

- [Green API](https://green-api.com) - WhatsApp API integration
- [OpenRouter](https://openrouter.ai) - AI model access
- [Railway](https://railway.app) - Hosting platform
- [Flask](https://flask.palletsprojects.com) - Web framework

## 📈 Roadmap

- [ ] **Database integration** untuk user management
- [ ] **Web dashboard** untuk admin
- [ ] **Multi-language** support
- [ ] **Plugin system** untuk fitur tambahan
- [ ] **Analytics dashboard**
- [ ] **Automated user role assignment**

## ⭐ Support

Jika project ini membantu Anda, berikan ⭐ di GitHub!

### 🐛 Bug Reports
Laporkan bug melalui [GitHub Issues](https://github.com/yourusername/whatsapp-ai-bot/issues)

### 💡 Feature Requests  
Ajukan fitur baru melalui [GitHub Discussions](https://github.com/yourusername/whatsapp-ai-bot/discussions)

---

<div align="center">

**Made with ❤️ by Rajulul Anshar**

[⬆ Back to top](#-whatsapp-ai-bot-with-hidden-user-roles)

</div>
