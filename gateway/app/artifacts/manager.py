from pathlib import Path
from app.workspace import OUTPUTS

class ArtifactManager:

    def __init__(self):
        self.files = []

    def add(self, path):
        path = Path(path)

        if path.exists():
            self.files.append(str(path))

    def all(self):
        return self.files

    def clear(self):
        self.files.clear()

artifacts = ArtifactManager()
