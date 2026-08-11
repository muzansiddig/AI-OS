import os
import traceback
from pathlib import Path
from typing import Any
import httpx

from app import config
from app.workspace import OUTPUTS, DEFAULT_WORKSPACE


class AutoGPTAdapter:

    def __init__(self):
        self.ollama_base_url = config.OLLAMA_BASE_URL
        self.model = config.MODEL_NAME

    async def chat(
        self,
        prompt: str,
        context: dict[str, Any] | None = None,
        artifacts: list[Any] | None = None,
        workspace: str | None = None,
        previous_results: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        target_workspace = Path(workspace or DEFAULT_WORKSPACE).resolve()
        target_workspace.mkdir(parents=True, exist_ok=True)

        # Call local Ollama chat API for autonomous goal planning & breakdown
        raw_model = self.model.replace("ollama/", "")
        endpoint = f"{self.ollama_base_url.rstrip('/')}/api/generate"

        system_prompt = (
            "You are AutoGPT, an autonomous goal-oriented research and execution agent. "
            "Decompose the user goal into structured execution steps and produce a clear result."
        )

        payload = {
            "model": raw_model,
            "prompt": f"{system_prompt}\n\nUSER GOAL:\n{prompt}",
            "stream": False,
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(endpoint, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    response_text = data.get("response", "").strip()

                    output_file = OUTPUTS / "autogpt_last.txt"
                    output_file.write_text(response_text, encoding="utf-8")

                    return {
                        "success": True,
                        "service": "autogpt",
                        "status": "completed",
                        "prompt": prompt,
                        "model": self.model,
                        "result": response_text,
                        "workspace": str(target_workspace),
                        "output_file": str(output_file),
                        "artifacts": artifacts or [],
                    }
                else:
                    return {
                        "success": False,
                        "service": "autogpt",
                        "status": "failed",
                        "error": "ollama_api_error",
                        "message": f"Ollama HTTP {response.status_code}: {response.text}",
                        "workspace": str(target_workspace),
                    }
        except Exception as e:
            return {
                "success": False,
                "service": "autogpt",
                "status": "failed",
                "error": "autogpt_execution_error",
                "message": str(e),
                "detail": traceback.format_exc(),
                "workspace": str(target_workspace),
            }


adapter = AutoGPTAdapter()
