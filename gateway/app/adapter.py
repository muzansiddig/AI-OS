from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT / "gateway") not in sys.path:
    sys.path.append(str(ROOT / "gateway"))

from app.artifacts.manager import artifacts
from app.workspace import OUTPUTS

class OpenInterpreterAdapter:
    def chat(self, prompt: str):  # تغيير الاسم هنا إلى chat
        result = interpreter.chat(prompt)  # تأكد من تعريف interpreter
        output_file = OUTPUTS / "open_interpreter_last.txt"
        output_file.write_text(
            str(result),
            encoding="utf-8"
        )
        artifacts.add(output_file)
        return result

adapter = OpenInterpreterAdapter()
