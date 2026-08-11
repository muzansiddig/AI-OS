import os
from pathlib import Path
from dotenv import load_dotenv

# Load root .env
env_path = Path(__file__).resolve().parents[3] / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
MODEL_NAME = os.getenv("AUTOGPT_MODEL", os.getenv("DEFAULT_MODEL", "ollama/qwen3:8b"))
SERVICE_PORT = int(os.getenv("AUTOGPT_PORT", 8105))
