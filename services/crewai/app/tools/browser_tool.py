import httpx
from crewai.tools import BaseTool


class BrowserUseTool(BaseTool):
    name: str = "browser_use"
    description: str = (
        "Use this tool to control a web browser. "
        "It can open websites, navigate pages, interact with web pages, "
        "and perform browser-based tasks."
    )

    browser_url: str = "http://127.0.0.1:8102/chat"

    def _run(self, prompt: str) -> str:
        try:
            response = httpx.post(
                self.browser_url,
                json={
                    "prompt": prompt
                },
                timeout=180.0,
            )

            response.raise_for_status()

            data = response.json()

            return str(data.get("result", data))

        except Exception as e:
            return f"Browser-use error: {e}"
