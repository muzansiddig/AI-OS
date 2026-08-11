import os
import traceback
from pathlib import Path
from typing import Any
from interpreter import interpreter

from app import config  # noqa: F401
from app.workspace import OUTPUTS


class OpenInterpreterAdapter:

    def chat(
        self,
        prompt: str,
        context: dict[str, Any] | None = None,
        artifacts: list[Any] | None = None,
        workspace: str | None = None,
        previous_results: dict[str, Any] | None = None,
    ):
        context = context or {}
        artifacts = artifacts or []
        previous_results = previous_results or {}

        execution_workspace = Path(
            workspace or getattr(config, "DEFAULT_WORKSPACE", "workspace/temp")
        ).resolve()

        execution_workspace.mkdir(
            parents=True,
            exist_ok=True,
        )

        runtime_prompt = f"""
You are the execution engine of AI-OS.

REAL WORKSPACE:
{execution_workspace}

USER TASK:
{prompt}

Rules:
- Execute the user's task.
- Reply with a brief summary of actions.
"""

        previous_cwd = Path.cwd()

        try:
            os.chdir(execution_workspace)

            # Ensure auto_run and offline are strictly enforced before chat call
            interpreter.auto_run = True
            interpreter.offline = True
            interpreter.display = False

            result = interpreter.chat(
                runtime_prompt,
                display=False,
            )

            output_file = OUTPUTS / "open_interpreter_last.txt"
            OUTPUTS.mkdir(parents=True, exist_ok=True)
            output_file.write_text(
                str(result),
                encoding="utf-8",
            )

            return {
                "success": True,
                "service": "open_interpreter",
                "status": "completed",
                "result": result,
                "workspace": str(execution_workspace),
                "output_file": str(output_file),
            }

        except Exception as e:
            error_msg = str(e)
            tb = traceback.format_exc()
            return {
                "success": False,
                "service": "open_interpreter",
                "status": "failed",
                "error": "open_interpreter_execution_error",
                "message": error_msg,
                "detail": tb,
                "workspace": str(execution_workspace),
            }

        finally:
            os.chdir(previous_cwd)


adapter = OpenInterpreterAdapter()
