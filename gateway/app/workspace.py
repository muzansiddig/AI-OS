from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = ROOT / "workspace"
PROJECTS = WORKSPACE / "projects"
DOWNLOADS = WORKSPACE / "downloads"
UPLOADS = WORKSPACE / "uploads"
TEMP = WORKSPACE / "temp"
OUTPUTS = WORKSPACE / "outputs"
LOGS = WORKSPACE / "logs"

for folder in (
    PROJECTS,
    DOWNLOADS,
    UPLOADS,
    TEMP,
    OUTPUTS,
    LOGS,
):
    folder.mkdir(parents=True, exist_ok=True)
