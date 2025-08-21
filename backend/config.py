import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the application"""
    
    # GROQ API Configuration
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    # Server Configuration
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    
    # CORS Configuration
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "https://astrologer-tawny.vercel.app,https://astrologer-weflys-projects.vercel.app,https://astrologer-git-main-weflys-projects.vercel.app").split(",")
    
    # Model Configuration
    MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.1-8b-instant")
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "800"))
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is required. Please set it in your .env file.")
        
        return True
