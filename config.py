import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the AI pipeline"""
    
    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
    LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
    LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "ai-pipeline")
    LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
    EURIAI_API_KEY = os.getenv("EURIAI_API_KEY", "euri-918d8acd66e83ca52f50f20a9d9df216bc317ad7704d271934a4511651eda6ae")
    
    # Qdrant Configuration
    QDRANT_URL = os.getenv("QDRANT_URL")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "ai_pipeline_docs")
    
    # Model Configuration
    MODEL_NAME = "gpt-4.1-nano"  # Using GPT-4.1 Nano everywhere
    EMBEDDING_MODEL = "models/embedding-001"
    
    # Weather API Configuration
    WEATHER_BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
    
    @classmethod
    def validate_config(cls):
        """Validate that all required environment variables are set"""
        required_vars = [
            "GEMINI_API_KEY",
            "OPENWEATHER_API_KEY", 
            "LANGSMITH_API_KEY",
            "QDRANT_URL",
            "QDRANT_API_KEY"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True 