import os
from pathlib import Path
from dotenv import load_dotenv

# Load root .env if present
root_dir = Path(__file__).resolve().parents[2]
env_path = root_dir / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)


class GatewaySettings:

    def __init__(self):
        self.ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")

        base_model = os.getenv("OLLAMA_MODEL", os.getenv("DEFAULT_MODEL", "qwen3:8b"))
        if not base_model.startswith("ollama/"):
            self.default_model: str = f"ollama/{base_model}"
        else:
            self.default_model: str = base_model

        self.gateway_port: int = int(os.getenv("GATEWAY_PORT", 8000))
        self.openinterpreter_port: int = int(os.getenv("OPENINTERPRETER_PORT", 8101))
        self.browser_use_port: int = int(os.getenv("BROWSER_USE_PORT", 8102))
        self.openhands_port: int = int(os.getenv("OPENHANDS_PORT", 8103))
        self.crewai_port: int = int(os.getenv("CREWAI_PORT", 8104))
        self.autogpt_port: int = int(os.getenv("AUTOGPT_PORT", 8105))

        self.default_http_timeout: float = float(os.getenv("DEFAULT_HTTP_TIMEOUT", 180.0))

    def get_service_model(self, service_name: str) -> str:
        env_key = f"{service_name.upper().replace('-', '_')}_MODEL"
        service_model = os.getenv(env_key)
        if service_model:
            if not service_model.startswith("ollama/"):
                return f"ollama/{service_model}"
            return service_model
        return self.default_model


settings = GatewaySettings()
