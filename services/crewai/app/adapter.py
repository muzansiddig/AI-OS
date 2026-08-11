import os
import traceback
from pathlib import Path
from dotenv import load_dotenv

# Load root .env
env_path = Path(__file__).resolve().parents[3] / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

from crewai import Agent, Crew, LLM, Task
from app.tools.browser_tool import BrowserUseTool


class CrewAIAdapter:

    def __init__(self):
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
        self.model = os.getenv(
            "CREWAI_MODEL",
            os.getenv("DEFAULT_MODEL", "ollama/qwen3:8b"),
        )
        self.llm = LLM(
            model=self.model,
            base_url=self.ollama_base_url,
        )
        self.browser_tool = BrowserUseTool()

    def chat(
        self,
        prompt: str,
        context: dict | None = None,
        artifacts: list | None = None,
        workspace: str | None = None,
        previous_results: dict | None = None,
    ):
        try:
            agent = Agent(
                role="AI Operating System Assistant",
                goal=(
                    "Understand the user's request, reason about it, "
                    "and use available tools when necessary."
                ),
                backstory=(
                    "You are the central reasoning agent inside an AI operating system. "
                    "You can answer questions directly and use browser automation "
                    "when the task requires interacting with websites."
                ),
                llm=self.llm,
                tools=[
                    self.browser_tool,
                ],
                verbose=True,
                allow_delegation=False,
            )

            task = Task(
                description=prompt,
                expected_output=(
                    "A clear and useful answer. "
                    "If browser automation was required, "
                    "include the result returned by the browser."
                ),
                agent=agent,
            )

            crew = Crew(
                agents=[agent],
                tasks=[task],
                verbose=True,
            )

            result = crew.kickoff()

            return {
                "success": True,
                "service": "crewai",
                "status": "completed",
                "prompt": prompt,
                "model": self.model,
                "workspace": workspace,
                "result": str(result),
                "context": context or {},
                "artifacts": artifacts or [],
                "previous_results": previous_results or {},
            }

        except Exception as e:
            return {
                "success": False,
                "service": "crewai",
                "status": "failed",
                "prompt": prompt,
                "workspace": workspace,
                "error": "crewai_execution_error",
                "message": str(e),
                "detail": traceback.format_exc(),
            }


adapter = CrewAIAdapter()
