from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
import json
import logging
from datetime import datetime
from bot import WhatsAppBot
from config import Config

# Inisialisasi bot
config = Config()
bot = WhatsAppBot(config)

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Green API Configuration
GREEN_API_URL = os.getenv('GREEN_API_URL')
GREEN_API_TOKEN = os.getenv('GREEN_API_TOKEN')
GREEN_API_INSTANCE = os.getenv('GREEN_API_INSTANCE')

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# ===== USER MANAGEMENT SYSTEM (NO DATABASE) =====

# Konfigurasi User - Hardcoded untuk user tertentu
SPECIAL_USERS = {
    # Format: "nomor@c.us": "role"
    "6285277801324@c.us": "admin",      # Ganti dengan nomor admin (Developer)
    "6282225651172@c.us": "vip",        # Ganti dengan nomor VIP
    "@c.us": "premium",    # Ganti dengan nomor Premium
    # Tambahkan user khusus lainnya di sini
}

# Banned users - Static list
BANNED_USERS = {
    # "628xxxxx@c.us",  # Uncomment dan tambahkan nomor yang ingin di-ban
}

# User Roles Configuration
USER_ROLES = {
    "admin": {
        "name": "Administrator",
        "ai_model": "meta-llama/llama-3.3-8b-instruct:free",  # Model yang tersedia
        "max_tokens": 800,
        "temperature": 0.7,
        "priority": 1,
        "features": ["full_access", "system_control", "user_management", "advanced_ai"],
        "show_badge": True  # Admin tetap menampilkan badge
    },
    "vip": {
        "name": "VIP Princess",
        "ai_model": "meta-llama/llama-3.3-8b-instruct:free",
        "max_tokens": 600,
        "temperature": 0.7,
        "priority": 2,
        "features": [
            "priority_responses",
            "extended_answers"
        ],
        "show_badge": False  # VIP tidak menampilkan badge
    },
    "premium": {
        "name": "Premium User",
        "ai_model": "meta-llama/llama-3.1-8b-instruct:free", 
        "max_tokens": 500,
        "temperature": 0.6,
        "priority": 3,
        "features": ["enhanced_ai", "extended_response"],
        "show_badge": False  # Premium tidak menampilkan badge
    },
    "basic": {
        "name": "Basic User",
        "ai_model": "meta-llama/llama-3.1-8b-instruct:free",
        "max_tokens": 250,
        "temperature": 0.6,
        "priority": 4,
        "features": ["basic_ai"],
        "show_badge": False
    }
}

# ===== USER HELPER FUNCTIONS =====

def get_user_role(chat_id):
    """Get user role based on chat_id"""
    if chat_id in BANNED_USERS:
        return "banned"
    
    return SPECIAL_USERS.get(chat_id, "basic")

def get_user_config(chat_id):
    """Get user configuration based on role"""
    role = get_user_role(chat_id)
    
    if role == "banned":
        return {
            "role": "banned",
            "name": "Banned User",
            "blocked": True
        }
    
    config = USER_ROLES.get(role, USER_ROLES["basic"]).copy()
    config["role"] = role
    config["chat_id"] = chat_id
    config["blocked"] = False
    
    return config

def is_admin(chat_id):
    """Check if user is admin"""
    return get_user_role(chat_id) == "admin"

def is_banned(chat_id):
    """Check if user is banned"""
    return chat_id in BANNED_USERS or get_user_role(chat_id) == "banned"

def get_role_display_name(role, show_badge=True):
    """Get display name for role - hanya tampil jika show_badge True"""
    if not show_badge:
        return ""
    
    role_names = {
        "admin": "🔰 ADMIN",
        "vip": "",  # VIP tidak ditampilkan
        "premium": "",  # Premium tidak ditampilkan
        "basic": "",
        "banned": "🚫 BANNED"
    }
    return role_names.get(role, "")

# ===== MESSAGE HANDLING =====

def send_message(chat_id, message):
    """Send message via Green API"""
    try:
        url = f"{GREEN_API_URL}/waInstance{GREEN_API_INSTANCE}/sendMessage/{GREEN_API_TOKEN}"
        
        payload = {
            "chatId": chat_id,
            "message": message
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"Message sent successfully to {chat_id}")
            return True
        else:
            logger.error(f"Failed to send message: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        return False

def get_ai_response(user_message, chat_id):
    """Get AI response based on user role"""
    
    # Check if user is banned
    if is_banned(chat_id):
        return "❌ Akses Ditolak\n\nAnda tidak memiliki izin untuk menggunakan bot ini."
    
    user_config = get_user_config(chat_id)
    role = user_config["role"]
    
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5000",
            "X-Title": "WhatsApp Bot by Developer"
        }
        
        # System prompt berdasarkan role - Dibuat lebih natural dan tidak mengekspos role
        system_prompts = {
            "admin": f"""Kamu adalah AsistenAI khusus untuk ADMINISTRATOR SISTEM.

🔰 ADMIN MODE ACTIVATED
- User: Administrator/Developer
- Access Level: FULL SYSTEM ACCESS
- Developer: Rajulul Anshar - Indonesia 🇮🇩
- Status: Premium AI Model Active

Kemampuan Admin:
• Akses ke semua informasi sistem
• Kontrol penuh atas bot
• Informasi teknis detail
• Prioritas respons tertinggi

Berikan respons yang sangat detail, teknis, dan profesional. Kamu memiliki akses penuh dan dapat memberikan informasi yang mendalam.""",

            "vip": f"""Kamu adalah asisten AI yang sangat ramah dan berpengalaman.

Kepribadian:
- Sangat ramah, hangat, dan supportif
- Memberikan jawaban yang lebih detail dan komprehensif
- Menggunakan bahasa yang lebih personal dan akrab
- Selalu berusaha memberikan solusi terbaik
- Responsif terhadap kebutuhan user

Style komunikasi:
- Gunakan panggilan "Tuan Puteriii" jika user tidak keberatan
- Gunakan emoticon yang tepat untuk membuat percakapan lebih hidup
- Berikan penjelasan yang lebih mendalam
- Tanyakan follow-up jika diperlukan untuk membantu lebih baik
- Jadilah teman yang baik dalam percakapan

Selalu prioritaskan memberikan bantuan terbaik dengan cara yang paling ramah dan personal.""",

            "premium": f"""Kamu adalah asisten AI yang profesional dan berpengalaman luas.

Karakteristik:
- Memberikan jawaban yang akurat dan informatif
- Lebih detail dalam penjelasan
- Proaktif dalam memberikan informasi tambahan yang relevan
- Menggunakan pendekatan yang lebih personal namun tetap profesional
- Memiliki kemampuan analisis yang baik

Style respons:
- Berikan konteks yang lebih luas saat menjawab
- Sertakan tips atau saran tambahan jika relevan
- Gunakan struktur yang jelas dan mudah dipahami
- Tunjukkan antusiasme dalam membantu

Fokus pada memberikan value maksimal dalam setiap respons.""",

            "basic": f"""Kamu adalah asisten AI yang membantu dan informatif.

Karakteristik:
- Ramah dan mudah diajak bicara
- Memberikan jawaban yang akurat dan to the point
- Fokus pada inti pertanyaan
- Menggunakan bahasa yang sederhana dan jelas

Style komunikasi:
- Jawaban yang singkat namun informatif
- Gunakan bahasa yang mudah dipahami
- Tetap sopan dan membantu
- Berikan jawaban langsung pada poin utama

Selalu berusaha membantu dengan sebaik mungkin."""
        }
        
        system_prompt = system_prompts.get(role, system_prompts["basic"])
        
        payload = {
            "model": user_config["ai_model"],
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "max_tokens": user_config["max_tokens"],
            "temperature": user_config["temperature"],
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }
        
        response = requests.post(
            OPENROUTER_BASE_URL, 
            headers=headers, 
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            ai_message = data['choices'][0]['message']['content'].strip()
            
            # Add role badge hanya untuk admin
            role_badge = get_role_display_name(role, user_config.get("show_badge", False))
            if role_badge:
                ai_message = f"{role_badge}\n\n{ai_message}"
            
            logger.info(f"AI Response generated for {role} user: {chat_id}")
            return ai_message
        else:
            logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
            return f"❌ Error AI Service\n\nTerjadi kesalahan saat memproses permintaan Anda.\nError Code: {response.status_code}"
            
    except Exception as e:
        logger.error(f"Error in get_ai_response: {str(e)}")
        return get_fallback_response(user_message, chat_id)

def get_fallback_response(user_message, chat_id):
    """Fallback response ketika AI tidak tersedia"""
    
    if is_banned(chat_id):
        return "❌ Akses Ditolak\n\nAnda tidak memiliki izin untuk menggunakan bot ini."
    
    user_config = get_user_config(chat_id)
    role = user_config["role"]
    message_lower = user_message.lower()
    
    # Hanya admin yang menampilkan badge
    role_badge = get_role_display_name(role, user_config.get("show_badge", False))
    prefix = f"{role_badge}\n\n" if role_badge else ""
    
    # Response untuk pertanyaan tentang developer/bot
    if any(keyword in message_lower for keyword in ['developer', 'pembuat', 'siapa', 'dibuat', 'creator']):
        base_response = f"""🤖 Tentang AsistenAI Bot

👨‍💻 Developer: Rajulul Anshar - Indonesia 🇮🇩
⚡ Teknologi: Python Flask + OpenRouter AI

💡 Info: Bot menggunakan AI untuk memberikan respons yang akurat dan membantu!"""
        
        if role == "admin":
            return f"""{prefix}{base_response}

🏷️ Your Status: Administrator

🔰 Admin Features:
• Full system access & control
• Premium AI model (Llama 8B)
• Unlimited detailed responses
• System management capabilities
• Highest priority processing"""
        else:
            return f"{prefix}{base_response}"

    # Status user - hanya admin yang bisa lihat detail
    elif any(word in message_lower for word in ['status', 'role', 'level', 'akses']):
        if role == "admin":
            return f"""{prefix}ℹ️ Admin Status Information

🏷️ Role: Administrator
📊 Access Level: Full System Access
🚀 Priority: Level 1 (Highest)

🔰 Admin Features:
• Full system access & control
• Premium AI model (Llama 8B)
• Unlimited detailed responses
• System management capabilities

💬 You have full administrative privileges."""
        else:
            return f"""😊 Bot Status: Online

🤖 AsistenAI siap membantu Anda!
✨ Kirim pertanyaan atau pesan apa saja dan saya akan berikan jawaban terbaik.

💡 Tip: Semakin spesifik pertanyaan Anda, semakin akurat jawaban yang bisa saya berikan!"""

    # Greeting berdasarkan role - dibuat natural
    elif any(word in message_lower for word in ['halo', 'hai', 'hello', 'hi', 'hei']):
        greetings = {
            "admin": f"{prefix}👋 Selamat datang, Administrator!\n\n🔰 Sistem mengenali Anda sebagai admin dengan akses penuh.",
            "vip": f"👋 Halo! Senang sekali bisa bertemu dengan Anda! 😊\n\n✨ Saya di sini untuk membantu dengan sepenuh hati. Ada yang bisa saya bantu hari ini?",
            "premium": f"👋 Selamat datang! \n\n😊 Saya siap memberikan bantuan terbaik untuk Anda. Apa yang bisa saya bantu hari ini?",
            "basic": f"👋 Halo!\n\n😊 Senang bisa membantu Anda hari ini."
        }
        
        greeting = greetings.get(role, greetings["basic"])
        return f"""{greeting}

🤖 AsistenAI siap membantu Anda!

💬 Kirim pertanyaan atau pesan apa saja!"""

    # Test/ping
    elif any(word in message_lower for word in ['test', 'ping', 'coba', 'aktif']):
        if role == "admin":
            return f"""{prefix}✅ Bot Status: ONLINE

🤖 AsistenAI berfungsi dengan baik!
🏷️ Your Level: Administrator
🔗 AI Service: Premium Model
👨‍💻 Developer: Rajulul Anshar

🚀 Full administrative access active!"""
        else:
            return f"""✅ Bot Online & Siap Membantu!

🤖 AsistenAI berfungsi dengan baik!
👨‍💻 Developer: Rajulul Anshar
🇮🇩 Made in Indonesia

🚀 Siap melayani dengan sepenuh hati!"""

    # Default response berdasarkan role
    else:
        responses = {
            "admin": f"""{prefix}💭 Pesan Diterima: "{user_message}"

🤖 AsistenAI (Admin Mode) siap membantu!

🔰 Admin Features:
• Full system access & control
• Premium AI model (Llama 8B) 
• Unlimited detailed responses
• System management capabilities

💡 Tip: Gunakan admin commands atau tanyakan apa saja!""",

            "vip": f"""💭 Terima kasih sudah mengirim pesan! 😊

"{user_message}"

✨ Saya akan dengan senang hati membantu Anda! Pertanyaan Anda sangat menarik, dan saya siap memberikan jawaban yang detail dan bermanfaat.

💡 Tip: Jangan ragu untuk bertanya apa saja - saya di sini untuk memberikan bantuan terbaik! 🌟""",

            "premium": f"""💭 Pesan Anda diterima dengan baik:

"{user_message}"

🤖 AsistenAI siap memberikan bantuan komprehensif untuk Anda!

💡 Tip: Silakan ajukan pertanyaan apapun, saya akan berikan jawaban yang informatif dan detail sesuai kebutuhan Anda!""",

            "basic": f"""💭 Pesan Diterima: "{user_message}"

🤖 AsistenAI siap membantu!

💡 Tip: Tanyakan apa saja dan saya akan berikan jawaban terbaik!"""
        }
        
        return responses.get(role, responses["basic"])

def process_admin_commands(message, chat_id):
    """Process admin commands (simple version without database)"""
    if not is_admin(chat_id):
        return None
    
    message_lower = message.lower()
    
    # Check user info: /check 628123456789
    if message_lower.startswith('/check'):
        parts = message.split()
        if len(parts) >= 2:
            target_number = parts[1]
            target_chat_id = f"{target_number}@c.us" if not target_number.endswith('@c.us') else target_number
            
            target_role = get_user_role(target_chat_id)
            target_config = get_user_config(target_chat_id)
            
            return f"""🔰 ADMIN - User Check

📱 Number: {target_number}
🏷️ Role: {target_role.title()}
🚫 Banned: {'Yes' if is_banned(target_chat_id) else 'No'}
⚡ AI Model: {target_config.get('ai_model', 'N/A')}
🎯 Max Tokens: {target_config.get('max_tokens', 'N/A')}
📊 Priority: Level {target_config.get('priority', 'N/A')}
👁️ Show Badge: {target_config.get('show_badge', False)}

Features:
{chr(10).join('• ' + feature for feature in target_config.get('features', []))}"""
        else:
            return "🔰 ADMIN COMMAND\n\nFormat: /check <nomor>\nContoh: /check 628123456789"
    
    # List special users: /users
    elif message_lower == '/users':
        users_info = "🔰 ADMIN - Special Users List\n\n"
        
        for chat_id, role in SPECIAL_USERS.items():
            number = chat_id.replace('@c.us', '')
            badge_status = "🏷️" if USER_ROLES.get(role, {}).get('show_badge', False) else "🔇"
            users_info += f"📱 {number} - {role.title()} {badge_status}\n"
        
        if BANNED_USERS:
            users_info += f"\n🚫 Banned Users:\n"
            for banned_id in BANNED_USERS:
                number = banned_id.replace('@c.us', '')
                users_info += f"❌ {number}\n"
        
        users_info += f"\n📊 Summary:\n"
        users_info += f"• Total Special Users: {len(SPECIAL_USERS)}\n"
        users_info += f"• Total Banned: {len(BANNED_USERS)}\n"
        users_info += f"• Hidden Roles: VIP & Premium (no badge shown)\n"
        
        return users_info
    
    # Bot stats: /stats
    elif message_lower == '/stats':
        admin_count = sum(1 for role in SPECIAL_USERS.values() if role == 'admin')
        vip_count = sum(1 for role in SPECIAL_USERS.values() if role == 'vip') 
        premium_count = sum(1 for role in SPECIAL_USERS.values() if role == 'premium')
        
        return f"""🔰 ADMIN - Bot Statistics

👥 User Distribution:
• Admin: {admin_count} (🏷️ Badge shown)
• VIP: {vip_count} (🔇 Hidden role)
• Premium: {premium_count} (🔇 Hidden role)
• Banned: {len(BANNED_USERS)}

⚙️ System Status:
• Green API: ✅ Connected
• OpenRouter AI: ✅ Active
• Bot Status: 🟢 Online

🤖 AI Models:
• Admin: Llama 8B (Free)
• VIP/Premium/Basic: Llama 8B

📊 Performance:
• Response Priority: Role-based
• Token Limits: Dynamic per role
• Role Visibility: Admin only

🔇 Privacy Features:
• VIP & Premium users tidak tahu status mereka
• Layanan lebih baik tanpa disclosure
• Natural user experience"""
    
    # Help commands: /help
    elif message_lower == '/help':
        return """🔰 ADMIN COMMANDS

User Management:
• /check <nomor> - Check user info & role status
• /users - List all special users with badges
• /stats - Show bot statistics & privacy info

Information:
• /help - Show this help
• /status - Check system status

Privacy Features:
• VIP & Premium users tidak menampilkan badge
• Mereka mendapat layanan lebih baik secara natural
• Hanya admin yang tahu struktur role lengkap

Note: 
- Admin commands hanya bisa digunakan oleh admin
- User management dilakukan melalui hardcoded config
- Untuk mengubah role, edit SPECIAL_USERS di kode"""
    
    return None

# ===== FLASK ROUTES =====

@app.route('/')
def home():
    """Home endpoint"""
    return jsonify({
        "status": "WhatsApp Bot with Hidden User Roles is running!",
        "webhook_url": "/webhook",
        "special_users": len(SPECIAL_USERS),
        "banned_users": len(BANNED_USERS),
        "roles": list(USER_ROLES.keys()),
        "privacy": "VIP & Premium roles are hidden from users"
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Main webhook endpoint"""
    try:
        data = request.get_json()
        logger.info(f"Received webhook: {json.dumps(data, indent=2)}")
        
        if data and data.get('typeWebhook') == 'incomingMessageReceived':
            sender_data = data.get('senderData', {})
            message_data = data.get('messageData', {})
            
            chat_id = sender_data.get('chatId')
            sender_name = sender_data.get('senderName', 'Unknown')
            
            if message_data.get('typeMessage') == 'textMessage':
                user_message = message_data.get('textMessageData', {}).get('textMessage', '')
                
                logger.info(f"Message from {sender_name} ({chat_id}) [{get_user_role(chat_id)}]: {user_message}")
                
                # Skip empty messages
                if not user_message.strip():
                    return jsonify({"status": "empty message ignored"})
                
                # Skip bot's own messages  
                bot_phone = f"{GREEN_API_INSTANCE}@c.us"
                if sender_data.get('sender') == bot_phone:
                    return jsonify({"status": "bot message ignored"})
                
                # Process admin commands first
                admin_response = process_admin_commands(user_message, chat_id)
                if admin_response:
                    send_message(chat_id, admin_response)
                    return jsonify({"status": "admin command processed"})
                
                # Get AI response based on user role
                ai_response = get_ai_response(user_message, chat_id)
                
                # Send response
                if send_message(chat_id, ai_response):
                    return jsonify({"status": f"message processed for {get_user_role(chat_id)} user"})
                else:
                    return jsonify({"status": "error sending response"})
        
        return jsonify({"status": "webhook received"})
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/users')
def api_users():
    """API endpoint to view user configuration"""
    return jsonify({
        "special_users": SPECIAL_USERS,
        "banned_users": list(BANNED_USERS),
        "roles_config": USER_ROLES,
        "total_special": len(SPECIAL_USERS),
        "total_banned": len(BANNED_USERS),
        "privacy_note": "VIP & Premium users don't see their special status"
    })

@app.route('/status')
def status():
    """Status endpoint"""
    return jsonify({
        "status": "healthy",
        "mode": "hidden_roles",
        "database": "none",
        "special_users": len(SPECIAL_USERS),
        "banned_users": len(BANNED_USERS),
        "roles": list(USER_ROLES.keys()),
        "privacy_features": {
            "admin_badge": True,
            "vip_badge": False,
            "premium_badge": False,
            "basic_badge": False
        },
        "green_api_configured": bool(GREEN_API_URL and GREEN_API_TOKEN and GREEN_API_INSTANCE),
        "openrouter_configured": bool(OPENROUTER_API_KEY)
    })

if __name__ == '__main__':
    required_vars = ['GREEN_API_URL', 'GREEN_API_TOKEN', 'GREEN_API_INSTANCE', 'OPENROUTER_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
        logger.error("Please check your .env file")
    else:
        logger.info("Starting WhatsApp Bot with Hidden User Roles...")
        logger.info(f"Special users configured: {len(SPECIAL_USERS)}")
        logger.info(f"Banned users: {len(BANNED_USERS)}")
        logger.info("Privacy mode: VIP & Premium roles are hidden from users")
        app.run(debug=True, host='0.0.0.0', port=5000)