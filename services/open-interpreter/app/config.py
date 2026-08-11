import os
from pathlib import Path
from dotenv import load_dotenv
from interpreter import interpreter

# Load root .env
env_path = Path(__file__).resolve().parents[3] / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
MODEL_NAME = os.getenv("OPENINTERPRETER_MODEL", os.getenv("DEFAULT_MODEL", "ollama/qwen3:8b"))

# Extract raw model name for Ollama if prefix exists
raw_model = MODEL_NAME.replace("ollama/", "")

interpreter.offline = True
interpreter.auto_run = True
interpreter.debug_mode = False

# Set parameters directly on interpreter.llm
interpreter.llm.model = f"ollama/{raw_model}"
interpreter.llm.api_base = OLLAMA_BASE_URL.rstrip('/')
interpreter.llm.supports_functions = False
interpreter.llm.context_window = 4096
interpreter.llm.max_tokens = 2048

os.environ["OLLAMA_HOST"] = OLLAMA_BASE_URL
