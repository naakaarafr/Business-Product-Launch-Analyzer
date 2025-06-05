"""
Configuration settings for the CrewAI Business Analyzer
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class for API settings and retry logic"""
    
    # API Configuration
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    SERPER_API_KEY = os.getenv("SERPER_API_KEY")
    
    # Gemini Model Configuration
    GEMINI_MODEL = "gemini-2.0-flash"
    GEMINI_TEMPERATURE = 0.5
    GEMINI_VERBOSE = True
    
    # Quota Handling Configuration
    MAX_RETRIES = 3  # Maximum number of retries for quota errors
    BASE_RETRY_DELAY = 60  # Base delay in seconds
    EXPONENTIAL_BACKOFF = True  # Use exponential backoff for retries
    
    # Crew Configuration
    CREW_MAX_RETRIES = 2  # Maximum retries at crew level
    CREW_VERBOSE_LEVEL = 2
    
    @classmethod
    def validate_api_keys(cls):
        """Validate that all required API keys are present"""
        missing_keys = []
        
        if not cls.GOOGLE_API_KEY:
            missing_keys.append("GOOGLE_API_KEY")
        
        if not cls.SERPER_API_KEY:
            missing_keys.append("SERPER_API_KEY")
        
        return missing_keys
    
    @classmethod
    def get_retry_delay(cls, attempt: int) -> int:
        """Calculate retry delay based on attempt number"""
        if cls.EXPONENTIAL_BACKOFF:
            return cls.BASE_RETRY_DELAY * (2 ** attempt)
        else:
            return cls.BASE_RETRY_DELAY
    
    @classmethod
    def print_config_info(cls):
        """Print configuration information"""
        print("🔧 Configuration:")
        print(f"   - Gemini Model: {cls.GEMINI_MODEL}")
        print(f"   - Max Retries: {cls.MAX_RETRIES}")
        print(f"   - Base Retry Delay: {cls.BASE_RETRY_DELAY}s")
        print(f"   - Exponential Backoff: {cls.EXPONENTIAL_BACKOFF}")
        print(f"   - Google API Key: {'✓ Set' if cls.GOOGLE_API_KEY else '❌ Missing'}")
        print(f"   - Serper API Key: {'✓ Set' if cls.SERPER_API_KEY else '❌ Missing'}")
        print()

# Usage example:
if __name__ == "__main__":
    Config.print_config_info()
    missing = Config.validate_api_keys()
    if missing:
        print(f"❌ Missing API keys: {', '.join(missing)}")
    else:
        print("✅ All API keys are configured correctly")