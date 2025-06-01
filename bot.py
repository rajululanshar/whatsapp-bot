import requests
import openai
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from config import Config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WhatsAppBot:
    """Main WhatsApp Bot Class"""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.message_history: Dict[str, List] = {}
        self.user_stats: Dict[str, Dict] = {}
        self.rate_limiter: Dict[str, List] = {}
        
        # Validate configuration
        try:
            self.config.validate_config()
            logger.info("Bot configuration validated successfully")
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            raise
        
        # Setup OpenAI
        openai.api_key = self.config.OPENROUTER_API_KEY
        
        logger.info(f"WhatsApp Bot initialized: {self.config.BOT_NAME}")
    
    def is_rate_limited(self, user_id: str) -> bool:
        """Check if user is rate limited"""
        current_time = time.time()
        user_messages = self.rate_limiter.get(user_id, [])
        
        # Remove old messages (older than 1 minute)
        user_messages = [msg_time for msg_time in user_messages if current_time - msg_time < 60]
        self.rate_limiter[user_id] = user_messages
        
        # Check rate limit
        if len(user_messages) >= self.config.MAX_MESSAGES_PER_MINUTE:
            return True
        
        # Add current message time
        user_messages.append(current_time)
        self.rate_limiter[user_id] = user_messages
        
        return False
    
    def update_user_stats(self, user_id: str, message: str, response: str):
        """Update user statistics"""
        if user_id not in self.user_stats:
            self.user_stats[user_id] = {
                'first_message': datetime.now(),
                'last_message': datetime.now(),
                'message_count': 0,
                'total_tokens_used': 0
            }
        
        stats = self.user_stats[user_id]
        stats['last_message'] = datetime.now()
        stats['message_count'] += 1
        stats['total_tokens_used'] += len(message.split()) + len(response.split())
        
    def get_ai_response(self, user_message: str, user_id: str = None) -> str:
        """Get response from OpenAI"""
        try:
            # Check for specific commands
            if user_message.lower().startswith('/help'):
                return self.get_help_message()
            
            if user_message.lower().startswith('/status') and self.config.is_admin_user(user_id):
                return self.get_status_message()
            
            if user_message.lower().startswith('/stats') and user_id:
                return self.get_user_stats(user_id)
            
            # Get conversation history for context
            context_messages = self.get_conversation_context(user_id)
            
            # Add current message
            context_messages.append({"role": "user", "content": user_message})
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model=self.config.OPENAI_MODEL,
                messages=context_messages,
                max_tokens=self.config.OPENAI_MAX_TOKENS,
                temperature=self.config.OPENAI_TEMPERATURE
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Update conversation history
            self.update_conversation_history(user_id, user_message, ai_response)
            
            # Update user statistics
            if user_id:
                self.update_user_stats(user_id, user_message, ai_response)
            
            return ai_response
            
        except openai.error.RateLimitError:
            logger.error("OpenAI rate limit exceeded")
            return "Maaf, terlalu banyak permintaan. Silakan coba lagi dalam beberapa menit."
        
        except openai.error.InvalidRequestError as e:
            logger.error(f"OpenAI invalid request: {e}")
            return "Maaf, permintaan tidak valid. Silakan coba dengan pertanyaan yang berbeda."
        
        except openai.error.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            return self.config.ERROR_MESSAGE
        
        except Exception as e:
            logger.error(f"Error getting AI response: {str(e)}")
            return self.config.ERROR_MESSAGE
    
    def get_conversation_context(self, user_id: str, max_messages: int = 5) -> List[Dict]:
        """Get conversation context for user"""
        context = [{"role": "system", "content": self.config.DEFAULT_SYSTEM_PROMPT}]
        
        if user_id and user_id in self.message_history:
            recent_messages = self.message_history[user_id][-max_messages:]
            for msg in recent_messages:
                context.append({"role": "user", "content": msg["user"]})
                context.append({"role": "assistant", "content": msg["bot"]})
        
        return context
    
    def update_conversation_history(self, user_id: str, user_message: str, bot_response: str):
        """Update conversation history"""
        if not user_id:
            return
        
        if user_id not in self.message_history:
            self.message_history[user_id] = []
        
        self.message_history[user_id].append({
            "timestamp": datetime.now(),
            "user": user_message,
            "bot": bot_response
        })
        
        # Keep only last 20 messages per user
        if len(self.message_history[user_id]) > 20:
            self.message_history[user_id] = self.message_history[user_id][-20:]
    
    def send_message(self, chat_id: str, message: str) -> bool:
        """Send message via Green API"""
        try:
            url = self.config.get_green_api_url("sendMessage")
            
            payload = {
                "chatId": chat_id,
                "message": message
            }
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"Message sent successfully to {chat_id}")
                return True
            else:
                logger.error(f"Failed to send message: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            logger.error("Timeout sending message")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error sending message: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return False
    
    def process_message(self, webhook_data: Dict) -> Dict:
        """Process incoming webhook message"""
        try:
            webhook_body = webhook_data.get('body', {})
            
            # Check if it's an incoming message
            if (webhook_body.get('typeWebhook') != 'incomingMessageReceived' or 
                webhook_body.get('messageData', {}).get('typeMessage') != 'textMessage'):
                return {"status": "ignored", "reason": "not a text message"}
            
            # Extract message details
            sender_data = webhook_body.get('senderData', {})
            message_data = webhook_body.get('messageData', {})
            
            chat_id = sender_data.get('chatId')
            sender_name = sender_data.get('senderName', 'Unknown')
            user_message = message_data.get('textMessageData', {}).get('textMessage', '')
            
            # Skip empty messages
            if not user_message.strip():
                return {"status": "ignored", "reason": "empty message"}
            
            # Skip bot's own messages
            if sender_data.get('sender') == self.config.GREEN_API_INSTANCE:
                return {"status": "ignored", "reason": "bot message"}
            
            # Check if user is allowed
            if not self.config.is_user_allowed(chat_id):
                return {"status": "ignored", "reason": "user not allowed"}
            
            # Check rate limiting
            if self.is_rate_limited(chat_id):
                self.send_message(chat_id, "Anda mengirim pesan terlalu cepat. Silakan tunggu sebentar.")
                return {"status": "rate_limited"}
            
            logger.info(f"Processing message from {sender_name} ({chat_id}): {user_message}")
            
            # Get AI response
            ai_response = self.get_ai_response(user_message, chat_id)
            
            # Send response
            if self.send_message(chat_id, ai_response):
                return {
                    "status": "success",
                    "chat_id": chat_id,
                    "user_message": user_message,
                    "bot_response": ai_response
                }
            else:
                return {"status": "error", "reason": "failed to send response"}
                
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {"status": "error", "reason": str(e)}
    
    def get_help_message(self) -> str:
        """Get help message"""
        return f"""🤖 *{self.config.BOT_NAME}*

Saya adalah AI Assistant yang siap membantu Anda!

*Perintah yang tersedia:*
• Kirim pesan biasa untuk bertanya apa saja
• /help - Tampilkan pesan bantuan ini
• /stats - Lihat statistik penggunaan Anda

*Tips:*
• Tanya apa saja dalam bahasa Indonesia
• Saya bisa membantu dengan informasi umum, perhitungan, dan diskusi
• Jika ada error, coba kirim pesan lagi

Selamat menggunakan! 😊"""
    
    def get_status_message(self) -> str:
        """Get bot status (admin only)"""
        total_users = len(self.user_stats)
        total_messages = sum(stats['message_count'] for stats in self.user_stats.values())
        
        return f"""📊 *Bot Status*

*Statistik:*
• Total pengguna: {total_users}
• Total pesan: {total_messages}
• Model AI: {self.config.OPENAI_MODEL}

*Konfigurasi:*
• Rate limit: {self.config.MAX_MESSAGES_PER_MINUTE} pesan/menit
• Max tokens: {self.config.OPENAI_MAX_TOKENS}
• Temperature: {self.config.OPENAI_TEMPERATURE}

Status: ✅ Online"""
    
    def get_user_stats(self, user_id: str) -> str:
        """Get user statistics"""
        if user_id not in self.user_stats:
            return "Anda belum memiliki statistik penggunaan."
        
        stats = self.user_stats[user_id]
        days_active = (datetime.now() - stats['first_message']).days + 1
        
        return f"""📈 *Statistik Penggunaan Anda*

• Pesan dikirim: {stats['message_count']}
• Hari aktif: {days_active}
• Pesan terakhir: {stats['last_message'].strftime('%d/%m/%Y %H:%M')}
• Rata-rata pesan/hari: {stats['message_count'] / days_active:.1f}

Terima kasih telah menggunakan bot ini! 🙏"""