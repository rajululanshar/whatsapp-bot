import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for WhatsApp Bot"""
    
    # Green API Configuration
    GREEN_API_URL = os.getenv('GREEN_API_URL', 'https://api.green-api.com')
    GREEN_API_TOKEN = os.getenv('GREEN_API_TOKEN')
    GREEN_API_INSTANCE = os.getenv('GREEN_API_INSTANCE')
    
    # OpenAI Configuration
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', '500'))
    OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))
    
    # Flask Configuration
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', '5000'))
    
    # Webhook Configuration
    WEBHOOK_URL = os.getenv('WEBHOOK_URL')
    
    # Bot Configuration
    BOT_NAME = os.getenv('BOT_NAME', 'WhatsApp AI Bot')
    BOT_DESCRIPTION = os.getenv('BOT_DESCRIPTION', 'AI Assistant powered by OpenAI')
    
    # Security Configuration
    ALLOWED_USERS = os.getenv('ALLOWED_USERS', '').split(',') if os.getenv('ALLOWED_USERS') else []
    ADMIN_USERS = os.getenv('ADMIN_USERS', '').split(',') if os.getenv('ADMIN_USERS') else []
    
    # Rate Limiting
    MAX_MESSAGES_PER_MINUTE = int(os.getenv('MAX_MESSAGES_PER_MINUTE', '10'))
    MAX_TOKENS_PER_DAY = int(os.getenv('MAX_TOKENS_PER_DAY', '10000'))
    
    # Response Configuration
    DEFAULT_SYSTEM_PROMPT = os.getenv('DEFAULT_SYSTEM_PROMPT', 
        'Kamu adalah asisten AI yang membantu dalam bahasa Indonesia. '
        'Jawab dengan ramah, informatif, dan singkat. '
        'Jika tidak tahu jawaban, katakan dengan jujur.')
    
    ERROR_MESSAGE = os.getenv('ERROR_MESSAGE', 
        'Maaf, saya sedang mengalami gangguan. Silakan coba lagi nanti.')
    
    WELCOME_MESSAGE = os.getenv('WELCOME_MESSAGE',
        'Halo! Saya adalah AI Assistant. Silakan tanya apa saja yang ingin Anda ketahui.')
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration"""
        required_vars = {
            'GREEN_API_TOKEN': cls.GREEN_API_TOKEN,
            'GREEN_API_INSTANCE': cls.GREEN_API_INSTANCE,
            'OPENROUTER_API_KEY': cls.OPENROUTER_API_KEY
        }
        
        missing_vars = [var for var, value in required_vars.items() if not value]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True
    
    @classmethod
    def get_green_api_url(cls, endpoint):
        """Generate Green API URL for specific endpoint"""
        return f"{cls.GREEN_API_URL}/waInstance{cls.GREEN_API_INSTANCE}/{endpoint}/{cls.GREEN_API_TOKEN}"
    
    @classmethod
    def is_user_allowed(cls, user_id):
        """Check if user is allowed to use the bot"""
        if not cls.ALLOWED_USERS:
            return True  # If no restrictions, allow all users
        return user_id in cls.ALLOWED_USERS
    
    @classmethod
    def is_admin_user(cls, user_id):
        """Check if user is admin"""
        return user_id in cls.ADMIN_USERS
    
    @classmethod
    def get_config_info(cls):
        """Get configuration information (without sensitive data)"""
        return {
            'bot_name': cls.BOT_NAME,
            'bot_description': cls.BOT_DESCRIPTION,
            'openai_model': cls.OPENAI_MODEL,
            'max_tokens': cls.OPENAI_MAX_TOKENS,
            'temperature': cls.OPENAI_TEMPERATURE,
            'flask_env': cls.FLASK_ENV,
            'has_user_restrictions': bool(cls.ALLOWED_USERS),
            'admin_users_count': len(cls.ADMIN_USERS),
            'rate_limit_per_minute': cls.MAX_MESSAGES_PER_MINUTE
        }

# Development Configuration
class DevelopmentConfig(Config):
    """Development specific configuration"""
    FLASK_DEBUG = True
    FLASK_ENV = 'development'

# Production Configuration  
class ProductionConfig(Config):
    """Production specific configuration"""
    FLASK_DEBUG = False
    FLASK_ENV = 'production'

# Configuration mapping
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': Config
}

def get_config(env_name=None):
    """Get configuration based on environment"""
    if env_name is None:
        env_name = os.getenv('FLASK_ENV', 'development')
    
    return config_map.get(env_name, Config)