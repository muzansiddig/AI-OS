import os
import traceback
from pathlib import Path
from dotenv import load_dotenv

# Load root .env
env_path = Path(__file__).resolve().parents[3] / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

from browser_use import Agent
from browser_use.llm import ChatOllama


class BrowserUseAdapter:

    def __init__(self):
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
        self.model = os.getenv(
            "BROWSER_USE_MODEL",
            os.getenv("DEFAULT_MODEL", "ollama/qwen3:8b"),
        )
        # Strip ollama/ prefix if ChatOllama expects plain model name
        model_name = self.model.replace("ollama/", "")
        self.llm = ChatOllama(
            model=model_name,
            host=self.ollama_base_url,
        )

    async def chat(
        self,
        prompt: str,
        context: dict | None = None,
        artifacts: list | None = None,
        workspace: str | None = None,
        previous_results: dict | None = None,
    ):
        try:
            agent = Agent(
                task=prompt,
                llm=self.llm,
                use_vision=False,
                max_failures=2,
                max_actions_per_step=1,
                max_history_items=6,
                enable_planning=False,
                directly_open_url=True,
                use_judge=False,
            )

            history = await agent.run(max_steps=5)

            final_result = history.final_result()
            if final_result is None:
                final_result = ""

            result_lower = str(final_result).lower()
            has_failure_keywords = any(kw in result_lower for kw in ["failed", "error", "not found", "unable", "invalid", "unresponsive"])
            is_successful = history.is_successful() if hasattr(history, "is_successful") else not has_failure_keywords
            if has_failure_keywords:
                is_successful = False

            status = "completed" if is_successful else "failed"

            return {
                "success": is_successful,
                "service": "browser_use",
                "status": status,
                "prompt": prompt,
                "model": self.model,
                "workspace": workspace,
                "result": final_result,
                "context": context or {},
                "artifacts": artifacts or [],
                "previous_results": previous_results or {},
            }

        except Exception as e:
            return {
                "success": False,
                "service": "browser_use",
                "status": "failed",
                "prompt": prompt,
                "workspace": workspace,
                "error": "browser_use_execution_error",
                "message": str(e),
                "detail": traceback.format_exc(),
            }


adapter = BrowserUseAdapter()
