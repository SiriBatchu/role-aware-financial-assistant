"""Configuration and environment setup."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Model Configuration
MODEL_NAME = "gpt-4o-mini"
MODEL_TEMPERATURE = 0.1
MODEL_MAX_TOKENS = 512

# Embedding Model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Audit Log
AUDIT_LOG_FILE = "audit_log.jsonl"

# Suppress tokenizer warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

def validate_config():
    """Validate required configuration."""
    if not OPENAI_API_KEY:
        raise ValueError("❌ OPENAI_API_KEY not found. Create a .env file with your key.")
    return True
