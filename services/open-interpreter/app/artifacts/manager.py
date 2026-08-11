class ArtifactManager:
    def __init__(self):
        self.items = []

    def add(self, file_path):
        self.items.append(file_path)

artifacts = ArtifactManager()
 
