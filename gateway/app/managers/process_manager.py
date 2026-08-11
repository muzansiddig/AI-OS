from pathlib import Path
import subprocess

PROJECT_ROOT = Path(__file__).resolve().parents[3]

SERVICES = {
    "open_interpreter": PROJECT_ROOT / "services" / "open-interpreter",
    "browser_use": PROJECT_ROOT / "services" / "browser-use",
    "openhands": PROJECT_ROOT / "services" / "openhands",
    "crewai": PROJECT_ROOT / "services" / "crewai",
}

class ProcessManager:

    def service_path(self, name: str):
        return SERVICES[name]

    def exists(self, name: str):
        return self.service_path(name).exists()

process_manager = ProcessManager()
