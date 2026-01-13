import os

# Defaults to "MOBILE" (Android/iOS). Can be set to "WEB".
AI_HEALING_APP_TYPE = os.environ.get("AI_HEALING_APP_TYPE", "MOBILE").upper()
# Defaults to "ANDROID" (Android). Can be set to "IOS" or "WEB".
AI_HEALING_PLATFORM = os.environ.get("AI_HEALING_PLATFORM", "ANDROID").upper()
# Retries
AI_HEALING_MAX_RETRIES = int(os.environ.get("AI_HEALING_MAX_RETRIES", 2))

# Metadata for Recording
PROJECT_NAME = os.environ.get("PROJECT_NAME", "Unknown Project")
PILLAR_NAME = os.environ.get("PILLAR_NAME", "Unknown Pillar")

# Provider Configuration
# Options: "anthropic", "openai", "gemini", "groq"
AI_HEALING_PROVIDER = os.environ.get("AI_HEALING_PROVIDER", "anthropic").lower()
# Anthropic Configuration
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")
# OpenAI Configuration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4-turbo")
# Google Gemini Configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-pro-latest")
# Groq Configuration
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama3-70b-8192")

# Database Configuration (PostgreSQL)
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
DB_NAME = os.environ.get("DB_NAME", "ai_healing")
# Toggle for Database Recording
AI_HEALING_DB_ENABLED = (
    os.environ.get("AI_HEALING_DB_ENABLED", "true").lower() == "true"
)
