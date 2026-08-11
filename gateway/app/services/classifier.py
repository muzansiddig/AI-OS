class Classifier:

    def classify(self, prompt: str) -> str:

        text = prompt.lower()

        # ===== Open Interpreter =====
        if any(word in text for word in [
            "افتح",
            "شغل",
            "احذف",
            "انسخ",
            "move",
            "copy",
            "delete",
            "terminal",
            "cmd",
            "powershell"
        ]):
            return "open_interpreter"

        # ===== Browser Use =====
        if any(word in text for word in [
            "google",
            "chrome",
            "browser",
            "linkedin",
            "github",
            "youtube",
            "website"
        ]):
            return "browser_use"

        # ===== OpenHands =====
        if any(word in text for word in [
            "project",
            "react",
            "flutter",
            "django",
            "fastapi",
            "python",
            "code",
            "program"
        ]):
            return "openhands"

        # ===== CrewAI =====
        if any(word in text for word in [
            "agents",
            "multi agent",
            "crew",
            "team"
        ]):
            return "crewai"

        # ===== AutoGPT =====
        if any(word in text for word in [
            "plan",
            "research",
            "analyze",
            "goal"
        ]):
            return "autogpt"

        return "openhands"


classifier = Classifier()
