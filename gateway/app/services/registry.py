from typing import Optional
from app.config import settings
from app.workspace import DOWNLOADS, PROJECTS, TEMP


class ServiceConfig:

    def __init__(
        self,
        name: str,
        port: int,
        workspace: str,
        capabilities: list[str],
        description: str,
        enabled: bool = True,
    ):
        self.name = name
        self.port = port
        self.url = f"http://127.0.0.1:{port}"
        self.workspace = workspace
        self.capabilities = capabilities
        self.description = description
        self.enabled = enabled
        self.status = "unknown"
        self.last_check = None


class ServiceRegistry:

    def __init__(self):
        self.services: dict[str, ServiceConfig] = {
            "open_interpreter": ServiceConfig(
                name="open_interpreter",
                port=settings.openinterpreter_port,
                workspace=str(TEMP),
                capabilities=[
                    "terminal",
                    "cmd",
                    "powershell",
                    "bash",
                    "os",
                    "folder",
                    "dir",
                    "file_system",
                    "python_exec",
                    "افتح",
                    "شغل",
                    "احذف",
                    "انسخ",
                ],
                description="OS Command Line & Terminal Execution Engine",
                enabled=True,
            ),
            "browser_use": ServiceConfig(
                name="browser_use",
                port=settings.browser_use_port,
                workspace=str(DOWNLOADS),
                capabilities=[
                    "browser",
                    "web",
                    "scrape",
                    "github",
                    "google",
                    "linkedin",
                    "youtube",
                    "chrome",
                ],
                description="Web Browser Automation Engine",
                enabled=True,
            ),
            "openhands": ServiceConfig(
                name="openhands",
                port=settings.openhands_port,
                workspace=str(PROJECTS),
                capabilities=[
                    "code",
                    "coding",
                    "software_engineering",
                    "react",
                    "flutter",
                    "django",
                    "fastapi",
                    "debug",
                    "repository",
                    "build_app",
                ],
                description="OpenHands Software Engineering Agent",
                enabled=True,
            ),
            "crewai": ServiceConfig(
                name="crewai",
                port=settings.crewai_port,
                workspace=str(PROJECTS),
                capabilities=[
                    "agent",
                    "workflow",
                    "crew",
                    "team",
                    "multi_agent",
                ],
                description="CrewAI Multi-Agent Workflow Engine",
                enabled=True,
            ),
            "autogpt": ServiceConfig(
                name="autogpt",
                port=settings.autogpt_port,
                workspace=str(PROJECTS),
                capabilities=[
                    "autonomous",
                    "planning",
                    "research",
                    "goal",
                ],
                description="AutoGPT Autonomous Task Engine",
                enabled=True,
            ),
        }

    def get_service(self, name: str) -> Optional[ServiceConfig]:
        service = self.services.get(name)
        if service and service.enabled:
            return service
        return None

    def has_service(self, name: str) -> bool:
        service = self.services.get(name)
        return service is not None and service.enabled

    def list_services(self) -> list[str]:
        return [name for name, s in self.services.items() if s.enabled]

    def match_capabilities(self, prompt: str) -> list[str]:
        text = prompt.lower()
        matched = []
        for service_name, config in self.services.items():
            if not config.enabled:
                continue
            for cap in config.capabilities:
                if cap.lower() in text:
                    matched.append(service_name)
                    break
        return matched


service_registry = ServiceRegistry()
