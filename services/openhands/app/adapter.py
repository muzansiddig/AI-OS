import os
import traceback
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from workspace root if available
env_path = Path(__file__).resolve().parents[3] / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

from openhands.sdk import Agent, Conversation, LLM


class OpenHandsAdapter:

    def __init__(self):
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
        self.model = os.getenv(
            "OPENHANDS_MODEL",
            os.getenv("DEFAULT_MODEL", "ollama/qwen3:8b"),
        )
        self.llm = LLM(
            model=self.model,
            ollama_base_url=self.ollama_base_url,
            api_key="ollama",
        )

    def chat(
        self,
        prompt: str,
        context: dict | None = None,
        artifacts: list | None = None,
        workspace: str | None = None,
        previous_results: dict | None = None,
    ):
        try:
            target_workspace = workspace or "workspace/project"
            Path(target_workspace).mkdir(parents=True, exist_ok=True)

            agent = Agent(llm=self.llm)
            conversation = Conversation(
                agent=agent,
                workspace=target_workspace,
            )

            conversation.send_message(prompt)
            conversation.run()

            return {
                "success": True,
                "service": "openhands",
                "status": "completed",
                "prompt": prompt,
                "model": self.model,
                "workspace": target_workspace,
                "artifacts": artifacts or [],
            }
        except Exception as e:
            error_msg = str(e)
            tb = traceback.format_exc()
            return {
                "success": False,
                "service": "openhands",
                "status": "failed",
                "prompt": prompt,
                "model": self.model,
                "error": "openhands_execution_error",
                "message": error_msg,
                "detail": tb,
                "workspace": workspace,
            }


adapter = OpenHandsAdapter()
