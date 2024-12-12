import os
from dotenv import load_dotenv
import secrets
load_dotenv()

# MongoDB Configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'perplexity_clone')

# Authentication Configuration
SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

# API Keys
SERPER_API_KEY = os.getenv('SERPER_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Embedding Model
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'
