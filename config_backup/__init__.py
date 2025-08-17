# Config package initialization
# Import all configuration from the main config.py file

import sys
import os

# Add the parent directory to the path so we can import from config.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    VECTOR_STORE_PATH, EMBEDDING_MODEL_NAME, OLLAMA_MODEL_NAME, 
    OLLAMA_BASE_URL, MAX_RETRIEVAL_DOCS, SECURITY_ENABLED, SECURITY_DIR, ENABLE_AUDIT_LOGGING,
    get_filter_options, DEFAULT_FILTERS, SEARCH_CONFIG, UI_CONFIG
) 