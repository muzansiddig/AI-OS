from pathlib import Path

SERVICE_ROOT = Path(__file__).resolve().parents[1]

OUTPUTS = SERVICE_ROOT / "outputs"
OUTPUTS.mkdir(parents=True, exist_ok=True)

DEFAULT_WORKSPACE = SERVICE_ROOT / "workspace"
DEFAULT_WORKSPACE.mkdir(parents=True, exist_ok=True)
