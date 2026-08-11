import sys
import traceback
from pathlib import Path

root_path = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

print("Testing Open Interpreter direct execution...")

try:
    from app.adapter import adapter
    res = adapter.chat(prompt="Say OK")
    print("RESULT:", res)
except Exception as e:
    print("EXCEPTION OCCURRED:", e)
    traceback.print_exc()
