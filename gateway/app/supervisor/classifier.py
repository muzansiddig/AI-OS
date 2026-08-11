import re
from typing import NamedTuple


class IntentResult(NamedTuple):
    intent: str
    suggested_services: list[str]
    confidence: float


class IntentClassifier:

    def _matches_any(self, text: str, keywords: list[str]) -> bool:
        for kw in keywords:
            if " " in kw:
                if kw in text:
                    return True
            else:
                pattern = r"\b" + re.escape(kw) + r"\b"
                if re.search(pattern, text, re.IGNORECASE):
                    return True
        return False

    def classify(self, prompt: str) -> IntentResult:
        text = prompt.lower()

        # Web Browsing & Automation Intent
        browser_keywords = [
            "browser", "web", "scrape", "github", "google", "linkedin",
            "youtube", "chrome", "website", "url", "search online", "browse"
        ]
        if self._matches_any(text, browser_keywords):
            return IntentResult(
                intent="web_browsing",
                suggested_services=["browser_use"],
                confidence=0.85,
            )

        # Software Engineering & Repository Coding Intent
        code_keywords = [
            "react", "flutter", "django", "fastapi", "code", "coding",
            "software", "app", "debug", "repository", "refactor", "bug"
        ]
        if self._matches_any(text, code_keywords):
            return IntentResult(
                intent="code_generation",
                suggested_services=["openhands"],
                confidence=0.85,
            )

        # Multi-Agent Workflow Intent
        crew_keywords = ["agent", "workflow", "crew", "team", "multi_agent"]
        if self._matches_any(text, crew_keywords):
            return IntentResult(
                intent="multi_agent_workflow",
                suggested_services=["crewai"],
                confidence=0.8,
            )

        # Autonomous Task & Research Intent
        autogpt_keywords = ["autonomous", "autogpt", "goal", "planning", "research"]
        if self._matches_any(text, autogpt_keywords):
            return IntentResult(
                intent="autonomous_task",
                suggested_services=["autogpt"],
                confidence=0.85,
            )

        # Terminal & OS Execution Intent
        terminal_keywords = [
            "terminal", "cmd", "powershell", "bash", "os", "folder", "dir",
            "file", "script", "command", "afteh", "افتح", "شغل", "احذف", "انسخ"
        ]
        if self._matches_any(text, terminal_keywords):
            return IntentResult(
                intent="terminal_command",
                suggested_services=["open_interpreter"],
                confidence=0.9,
            )

        # Default Fallback Intent
        return IntentResult(
            intent="general_task",
            suggested_services=["open_interpreter"],
            confidence=0.5,
        )


classifier = IntentClassifier()
